import pytest
from httpx import AsyncClient

from app.auth import hash_password
from app.models import (
    CustomStatus,
    StatusSet,
    StatusSetScope,
    StatusTransition,
    SubTeam,
    TaskStatus,
    User,
    UserRole,
)


async def _login(async_client: AsyncClient, username: str) -> str:
    response = await async_client.post(
        "/api/auth/token",
        data={"username": username, "password": "password"},
    )
    assert response.status_code == 200
    return response.json()["access_token"]


async def _create_user(
    db_session,
    *,
    email: str,
    username: str,
    role: UserRole,
    sub_team_id: int,
) -> User:
    user = User(
        email=email,
        username=username,
        full_name=username.title(),
        hashed_password=hash_password("password"),
        role=role,
        sub_team_id=sub_team_id,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


async def _create_status_set(db_session, *, suffix: str = ""):
    sub_team = SubTeam(name=f"Workflow Team{suffix}", supervisor_id=None)
    db_session.add(sub_team)
    await db_session.commit()
    await db_session.refresh(sub_team)

    status_set = StatusSet(
        scope=StatusSetScope.sub_team_default,
        sub_team_id=sub_team.id,
    )
    db_session.add(status_set)
    await db_session.commit()
    await db_session.refresh(status_set)

    todo = CustomStatus(
        status_set_id=status_set.id,
        name=f"To Do{suffix}",
        slug=f"todo{suffix}".strip("_"),
        color="#64748b",
        position=0,
        is_done=False,
        legacy_status=TaskStatus.todo,
    )
    review = CustomStatus(
        status_set_id=status_set.id,
        name=f"Review{suffix}",
        slug=f"review{suffix}".strip("_"),
        color="#f59e0b",
        position=1,
        is_done=False,
        legacy_status=TaskStatus.review,
    )
    done = CustomStatus(
        status_set_id=status_set.id,
        name=f"Done{suffix}",
        slug=f"done{suffix}".strip("_"),
        color="#10b981",
        position=2,
        is_done=True,
        legacy_status=TaskStatus.done,
    )
    db_session.add_all([todo, review, done])
    await db_session.commit()
    await db_session.refresh(todo)
    await db_session.refresh(review)
    await db_session.refresh(done)
    return sub_team, status_set, todo, review, done


def test_default_status_set_model_includes_seeded_legacy_statuses():
    status_set = StatusSet(scope=StatusSetScope.sub_team_default, sub_team_id=1)
    status_set.statuses = [
        CustomStatus(
            name="To Do",
            slug="todo",
            color="#64748b",
            position=0,
            is_done=False,
            legacy_status=TaskStatus.todo,
        ),
        CustomStatus(
            name="In Progress",
            slug="in_progress",
            color="#0ea5e9",
            position=1,
            is_done=False,
            legacy_status=TaskStatus.in_progress,
        ),
        CustomStatus(
            name="Review",
            slug="review",
            color="#f59e0b",
            position=2,
            is_done=False,
            legacy_status=TaskStatus.review,
        ),
        CustomStatus(
            name="Done",
            slug="done",
            color="#10b981",
            position=3,
            is_done=True,
            legacy_status=TaskStatus.done,
        ),
        CustomStatus(
            name="Blocked",
            slug="blocked",
            color="#f43f5e",
            position=4,
            is_done=False,
            legacy_status=TaskStatus.blocked,
        ),
    ]

    assert [status.slug for status in status_set.statuses] == [
        "todo",
        "in_progress",
        "review",
        "done",
        "blocked",
    ]
    assert [status.legacy_status for status in status_set.statuses] == [
        TaskStatus.todo,
        TaskStatus.in_progress,
        TaskStatus.review,
        TaskStatus.done,
        TaskStatus.blocked,
    ]


def test_done_status_has_is_done_true():
    done_status = CustomStatus(
        name="Done",
        slug="done",
        color="#10b981",
        position=3,
        is_done=True,
        legacy_status=TaskStatus.done,
    )

    assert done_status.is_done is True


@pytest.mark.asyncio
async def test_status_transition_model_can_create_valid_transition(db_session):
    _, status_set, todo, review, _ = await _create_status_set(db_session, suffix="_model")

    transition = StatusTransition(
        status_set_id=status_set.id,
        from_status_id=todo.id,
        to_status_id=review.id,
    )
    db_session.add(transition)
    await db_session.commit()
    await db_session.refresh(transition)

    assert transition.id is not None
    assert transition.status_set_id == status_set.id
    assert transition.from_status_id == todo.id
    assert transition.to_status_id == review.id


@pytest.mark.asyncio
async def test_transition_replace_validates_auth_pairs_and_empty_payload(
    async_client: AsyncClient, db_session
):
    sub_team, status_set, todo, review, done = await _create_status_set(
        db_session, suffix="_api"
    )
    _, other_set, other_todo, _, _ = await _create_status_set(
        db_session, suffix="_other"
    )
    supervisor = await _create_user(
        db_session,
        email="workflow-supervisor@example.com",
        username="workflow-supervisor",
        role=UserRole.supervisor,
        sub_team_id=sub_team.id,
    )
    member = await _create_user(
        db_session,
        email="workflow-member@example.com",
        username="workflow-member",
        role=UserRole.member,
        sub_team_id=sub_team.id,
    )
    sub_team.supervisor_id = supervisor.id
    await db_session.commit()
    status_set_id = status_set.id
    todo_id = todo.id
    review_id = review.id
    done_id = done.id
    other_set_id = other_set.id
    other_todo_id = other_todo.id
    supervisor_username = supervisor.username
    member_username = member.username

    member_token = await _login(async_client, member_username)
    member_headers = {"Authorization": f"Bearer {member_token}"}
    response = await async_client.post(
        f"/api/status-sets/{status_set_id}/transitions",
        json={"transitions": [{"from_status_id": todo_id, "to_status_id": review_id}]},
        headers=member_headers,
    )
    assert response.status_code == 403

    supervisor_token = await _login(async_client, supervisor_username)
    supervisor_headers = {"Authorization": f"Bearer {supervisor_token}"}
    response = await async_client.post(
        f"/api/status-sets/{status_set_id}/transitions",
        json={
            "transitions": [
                {"from_status_id": todo_id, "to_status_id": review_id},
                {"from_status_id": review_id, "to_status_id": done_id},
            ]
        },
        headers=supervisor_headers,
    )
    assert response.status_code == 200
    assert {(row["from_status_id"], row["to_status_id"]) for row in response.json()} == {
        (todo_id, review_id),
        (review_id, done_id),
    }

    response = await async_client.post(
        f"/api/status-sets/{status_set_id}/transitions",
        json={
            "transitions": [
                {"from_status_id": todo_id, "to_status_id": review_id},
                {"from_status_id": todo_id, "to_status_id": review_id},
            ]
        },
        headers=supervisor_headers,
    )
    assert response.status_code == 400

    response = await async_client.post(
        f"/api/status-sets/{status_set_id}/transitions",
        json={"transitions": [{"from_status_id": todo_id, "to_status_id": todo_id}]},
        headers=supervisor_headers,
    )
    assert response.status_code == 400

    response = await async_client.post(
        f"/api/status-sets/{status_set_id}/transitions",
        json={
            "transitions": [
                {"from_status_id": todo_id, "to_status_id": other_todo_id}
            ]
        },
        headers=supervisor_headers,
    )
    assert other_set_id != status_set_id
    assert response.status_code == 400

    response = await async_client.post(
        f"/api/status-sets/{status_set_id}/transitions",
        json={"transitions": []},
        headers=supervisor_headers,
    )
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_transition_get_filters_archived_endpoints_and_writes_reject_archived(
    async_client: AsyncClient, db_session
):
    sub_team, status_set, todo, review, _ = await _create_status_set(
        db_session, suffix="_archived"
    )
    supervisor = await _create_user(
        db_session,
        email="workflow-archived-supervisor@example.com",
        username="workflow-archived-supervisor",
        role=UserRole.supervisor,
        sub_team_id=sub_team.id,
    )
    sub_team.supervisor_id = supervisor.id
    await db_session.commit()
    status_set_id = status_set.id
    todo_id = todo.id
    review_id = review.id
    supervisor_username = supervisor.username
    token = await _login(async_client, supervisor_username)
    headers = {"Authorization": f"Bearer {token}"}

    response = await async_client.post(
        f"/api/status-sets/{status_set_id}/transitions",
        json={"transitions": [{"from_status_id": todo_id, "to_status_id": review_id}]},
        headers=headers,
    )
    assert response.status_code == 200
    transition_id = response.json()[0]["id"]

    review.is_archived = True
    await db_session.commit()

    response = await async_client.get(
        f"/api/status-sets/{status_set_id}/transitions",
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json() == []

    response = await async_client.get(
        f"/api/status-sets/{status_set_id}/transitions?include_archived=true",
        headers=headers,
    )
    assert response.status_code == 200
    assert [row["id"] for row in response.json()] == [transition_id]

    response = await async_client.post(
        f"/api/status-sets/{status_set_id}/transitions",
        json={"transitions": [{"from_status_id": todo_id, "to_status_id": review_id}]},
        headers=headers,
    )
    assert response.status_code == 400

    response = await async_client.delete(
        f"/api/status-sets/{status_set_id}/transitions/{transition_id}",
        headers=headers,
    )
    assert response.status_code == 200

    response = await async_client.delete(
        f"/api/status-sets/{status_set_id}/transitions/{transition_id}",
        headers=headers,
    )
    assert response.status_code == 404
