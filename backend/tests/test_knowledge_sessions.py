from datetime import datetime, timedelta, timezone

import pytest
from httpx import AsyncClient
from sqlalchemy import select

from app.models import (
    EventNotification,
    KnowledgeSession,
    NotificationEventType,
    NotificationStatus,
    SubTeam,
    User,
    UserRole,
)
from app.utils.auth import create_access_token, hash_password


async def _login(db_session, username: str) -> str:
    result = await db_session.execute(select(User).where(User.username == username))
    user = result.scalar_one()
    return create_access_token({"sub": str(user.id)})


async def _create_user(
    db_session,
    *,
    email: str,
    username: str,
    full_name: str,
    role: UserRole,
    sub_team_id: int | None,
) -> User:
    user = User(
        email=email,
        username=username,
        full_name=full_name,
        hashed_password=hash_password("password"),
        role=role,
        sub_team_id=sub_team_id,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


async def _build_scope_graph(db_session):
    team_a = SubTeam(name="Team A", supervisor_id=None)
    team_b = SubTeam(name="Team B", supervisor_id=None)
    db_session.add_all([team_a, team_b])
    await db_session.commit()
    await db_session.refresh(team_a)
    await db_session.refresh(team_b)

    manager = await _create_user(
        db_session,
        email="manager@example.com",
        username="manager",
        full_name="Manager User",
        role=UserRole.manager,
        sub_team_id=team_a.id,
    )
    supervisor_a = await _create_user(
        db_session,
        email="supervisor-a@example.com",
        username="supervisor-a",
        full_name="Supervisor A",
        role=UserRole.supervisor,
        sub_team_id=team_a.id,
    )
    supervisor_b = await _create_user(
        db_session,
        email="supervisor-b@example.com",
        username="supervisor-b",
        full_name="Supervisor B",
        role=UserRole.supervisor,
        sub_team_id=team_b.id,
    )
    member_a = await _create_user(
        db_session,
        email="member-a@example.com",
        username="member-a",
        full_name="Member A",
        role=UserRole.member,
        sub_team_id=team_a.id,
    )
    member_b = await _create_user(
        db_session,
        email="member-b@example.com",
        username="member-b",
        full_name="Member B",
        role=UserRole.member,
        sub_team_id=team_b.id,
    )

    team_a.supervisor_id = supervisor_a.id
    team_b.supervisor_id = supervisor_b.id
    await db_session.commit()

    return {
        "team_a": team_a,
        "team_a_id": team_a.id,
        "team_b": team_b,
        "team_b_id": team_b.id,
        "manager": manager,
        "manager_id": manager.id,
        "manager_username": manager.username,
        "supervisor_a": supervisor_a,
        "supervisor_a_id": supervisor_a.id,
        "supervisor_a_username": supervisor_a.username,
        "supervisor_b": supervisor_b,
        "supervisor_b_id": supervisor_b.id,
        "supervisor_b_username": supervisor_b.username,
        "member_a": member_a,
        "member_a_id": member_a.id,
        "member_a_username": member_a.username,
        "member_b": member_b,
        "member_b_id": member_b.id,
        "member_b_username": member_b.username,
    }


@pytest.mark.asyncio
async def test_manager_org_wide_session_defaults_presenter_and_scope(
    async_client: AsyncClient, db_session
):
    graph = await _build_scope_graph(db_session)
    token = await _login(db_session, graph["manager_username"])
    now = datetime.now(timezone.utc).replace(tzinfo=None)

    response = await async_client.post(
        "/api/knowledge-sessions/",
        json={
            "topic": "Org-wide kickoff",
            "duration_minutes": 45,
            "start_time": (now + timedelta(days=1)).isoformat(),
            "tags": ["ops", "Ops", " ", "team"],
            "offset_minutes_list": [30],
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["presenter_id"] == data["created_by_id"]
    assert data["sub_team_id"] is None
    assert data["tags"] == ["ops", "team"]


@pytest.mark.asyncio
async def test_supervisor_session_forces_team_scope_and_rejects_foreign_presenter(
    async_client: AsyncClient, db_session
):
    graph = await _build_scope_graph(db_session)
    supervisor_username = graph["supervisor_a_username"]
    member_a_id = graph["member_a_id"]
    member_b_id = graph["member_b_id"]
    team_a_id = graph["team_a_id"]
    token = await _login(db_session, supervisor_username)
    now = datetime.now(timezone.utc).replace(tzinfo=None)

    bad_response = await async_client.post(
        "/api/knowledge-sessions/",
        json={
            "topic": "Team session",
            "presenter_id": member_b_id,
            "duration_minutes": 30,
            "start_time": (now + timedelta(days=1)).isoformat(),
            "offset_minutes_list": [],
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert bad_response.status_code == 403

    good_response = await async_client.post(
        "/api/knowledge-sessions/",
        json={
            "topic": "Team session",
            "presenter_id": member_a_id,
            "duration_minutes": 30,
            "start_time": (now + timedelta(days=1)).isoformat(),
            "offset_minutes_list": [15, 30],
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert good_response.status_code == 201
    assert good_response.json()["sub_team_id"] == team_a_id


@pytest.mark.asyncio
async def test_member_visibility_includes_org_wide_and_own_team_only(
    async_client: AsyncClient, db_session
):
    graph = await _build_scope_graph(db_session)
    manager_username = graph["manager_username"]
    member_username = graph["member_a_username"]
    supervisor_username = graph["supervisor_a_username"]
    team_b_id = graph["team_b_id"]
    member_a_id = graph["member_a_id"]
    member_b_id = graph["member_b_id"]
    manager_token = await _login(db_session, manager_username)
    member_token = await _login(db_session, member_username)
    now = datetime.now(timezone.utc).replace(tzinfo=None)

    await async_client.post(
        "/api/knowledge-sessions/",
        json={
            "topic": "Org-wide",
            "duration_minutes": 30,
            "start_time": (now + timedelta(days=1)).isoformat(),
            "offset_minutes_list": [],
        },
        headers={"Authorization": f"Bearer {manager_token}"},
    )
    supervisor_token = await _login(db_session, supervisor_username)
    await async_client.post(
        "/api/knowledge-sessions/",
        json={
            "topic": "Team A",
            "presenter_id": member_a_id,
            "duration_minutes": 30,
            "start_time": (now + timedelta(days=2)).isoformat(),
            "offset_minutes_list": [],
        },
        headers={"Authorization": f"Bearer {supervisor_token}"},
    )
    await async_client.post(
        "/api/knowledge-sessions/",
        json={
            "topic": "Team B",
            "presenter_id": member_b_id,
            "duration_minutes": 30,
            "start_time": (now + timedelta(days=3)).isoformat(),
            "offset_minutes_list": [],
        },
        headers={
            "Authorization": f"Bearer {manager_token}",
            "X-SubTeam-ID": str(team_b_id),
        },
    )

    response = await async_client.get(
        "/api/knowledge-sessions/",
        headers={"Authorization": f"Bearer {member_token}"},
    )
    assert response.status_code == 200
    titles = [session["topic"] for session in response.json()]
    assert "Org-wide" in titles
    assert "Team A" in titles
    assert "Team B" not in titles


@pytest.mark.asyncio
async def test_creation_and_reminder_notifications_follow_scope_and_patch_replaces_pending_rows(
    async_client: AsyncClient, db_session
):
    graph = await _build_scope_graph(db_session)
    manager_username = graph["manager_username"]
    manager_token = await _login(db_session, manager_username)
    manager_id = graph["manager_id"]
    team_a_id = graph["team_a_id"]
    team_b_id = graph["team_b_id"]
    supervisor_a_id = graph["supervisor_a_id"]
    supervisor_b_id = graph["supervisor_b_id"]
    member_a_id = graph["member_a_id"]
    member_b_id = graph["member_b_id"]
    now = datetime.now(timezone.utc).replace(tzinfo=None)

    response = await async_client.post(
        "/api/knowledge-sessions/",
        json={
            "topic": "Reminder session",
            "duration_minutes": 30,
            "start_time": (now + timedelta(days=2)).isoformat(),
            "offset_minutes_list": [60, 30],
        },
        headers={"Authorization": f"Bearer {manager_token}"},
    )
    assert response.status_code == 201
    session_id = response.json()["id"]

    result = await db_session.execute(
        select(EventNotification).where(
            EventNotification.event_type == NotificationEventType.knowledge_session,
            EventNotification.event_ref_id == session_id,
        )
    )
    rows = result.scalars().all()
    assert rows
    assert all(row.status == NotificationStatus.sent for row in rows if row.offset_minutes == 0)
    assert all(row.status == NotificationStatus.pending for row in rows if row.offset_minutes != 0)

    response = await async_client.patch(
        f"/api/knowledge-sessions/{session_id}",
        json={"offset_minutes_list": [15]},
        headers={"Authorization": f"Bearer {manager_token}"},
    )
    assert response.status_code == 200

    result = await db_session.execute(
        select(EventNotification).where(
            EventNotification.event_type == NotificationEventType.knowledge_session,
            EventNotification.event_ref_id == session_id,
        )
    )
    rows = result.scalars().all()
    assert len([row for row in rows if row.offset_minutes == 0]) == len(
        [row for row in rows if row.status == NotificationStatus.sent and row.offset_minutes == 0]
    )
    nonzero_rows = [row for row in rows if row.offset_minutes != 0]
    assert {row.offset_minutes for row in nonzero_rows} == {15}
    assert len(nonzero_rows) == len(
        {
            manager_id,
            supervisor_a_id,
            supervisor_b_id,
            member_a_id,
            member_b_id,
        }
    )


@pytest.mark.asyncio
async def test_notification_resolver_enforces_visibility(
    async_client: AsyncClient, db_session
):
    graph = await _build_scope_graph(db_session)
    manager_username = graph["manager_username"]
    member_username = graph["member_a_username"]
    supervisor_username = graph["supervisor_a_username"]
    member_b_username = graph["member_b_username"]
    member_a_id = graph["member_a_id"]
    member_b_id = graph["member_b_id"]
    manager_token = await _login(db_session, manager_username)
    member_token = await _login(db_session, member_username)
    now = datetime.now(timezone.utc).replace(tzinfo=None)

    response = await async_client.post(
        "/api/knowledge-sessions/",
        json={
            "topic": "Visible session",
            "duration_minutes": 30,
            "start_time": (now + timedelta(days=1)).isoformat(),
            "offset_minutes_list": [15],
        },
        headers={"Authorization": f"Bearer {manager_token}"},
    )
    assert response.status_code == 201, response.text
    visible_session_id = response.json()["id"]

    supervisor_token = await _login(db_session, supervisor_username)
    hidden_session_response = await async_client.post(
        "/api/knowledge-sessions/",
        json={
            "topic": "Hidden session",
            "presenter_id": member_a_id,
            "duration_minutes": 30,
            "start_time": (now + timedelta(days=2)).isoformat(),
            "offset_minutes_list": [15],
        },
        headers={"Authorization": f"Bearer {supervisor_token}"},
    )
    assert hidden_session_response.status_code == 201, hidden_session_response.text
    hidden_session_id = hidden_session_response.json()["id"]

    visible = await async_client.get(
        "/api/notifications/by-event",
        params={"event_type": "knowledge_session", "event_ref_id": visible_session_id},
        headers={"Authorization": f"Bearer {member_token}"},
    )
    assert visible.status_code == 200

    member_b_token = await _login(db_session, member_b_username)
    hidden = await async_client.get(
        "/api/notifications/by-event",
        params={"event_type": "knowledge_session", "event_ref_id": hidden_session_id},
        headers={"Authorization": f"Bearer {member_b_token}"},
    )
    assert hidden.status_code in (403, 404)
