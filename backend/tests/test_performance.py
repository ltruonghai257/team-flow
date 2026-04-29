import pytest
from httpx import AsyncClient

from app.models import Project, SubTeam, Task, TaskStatus, User, UserRole
from app.utils.auth import create_access_token, hash_password


async def _user(db_session, *, username: str, role: UserRole, sub_team_id: int | None):
    user = User(
        email=f"{username}@example.com",
        username=username,
        full_name=username.replace("_", " ").title(),
        hashed_password=hash_password("password"),
        role=role,
        sub_team_id=sub_team_id,
    )
    db_session.add(user)
    await db_session.flush()
    return user


@pytest.mark.asyncio
async def test_supervisor_scoping(async_client: AsyncClient, db_session):
    """TEAM-04: Supervisor performance endpoints are limited to visible scope."""
    team_a = SubTeam(name="Performance A")
    team_b = SubTeam(name="Performance B")
    db_session.add_all([team_a, team_b])
    await db_session.flush()

    supervisor = await _user(
        db_session,
        username="performance_supervisor",
        role=UserRole.supervisor,
        sub_team_id=team_a.id,
    )
    member_a = await _user(
        db_session,
        username="performance_member_a",
        role=UserRole.member,
        sub_team_id=team_a.id,
    )
    member_b = await _user(
        db_session,
        username="performance_member_b",
        role=UserRole.member,
        sub_team_id=team_b.id,
    )
    team_a.supervisor_id = supervisor.id

    project_a = Project(name="Performance Project A", sub_team_id=team_a.id)
    project_b = Project(name="Performance Project B", sub_team_id=team_b.id)
    db_session.add_all([project_a, project_b])
    await db_session.flush()
    db_session.add_all(
        [
            Task(
                title="Visible performance task",
                status=TaskStatus.todo,
                project_id=project_a.id,
                assignee_id=member_a.id,
                creator_id=supervisor.id,
            ),
            Task(
                title="Hidden performance task",
                status=TaskStatus.todo,
                project_id=project_b.id,
                assignee_id=member_b.id,
                creator_id=member_b.id,
            ),
        ]
    )
    await db_session.commit()

    token = create_access_token({"sub": str(supervisor.id)})
    response = await async_client.get(
        "/api/performance/team",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    user_ids = {row["user_id"] for row in response.json()["team_metrics"]}
    assert member_a.id in user_ids
    assert member_b.id not in user_ids
