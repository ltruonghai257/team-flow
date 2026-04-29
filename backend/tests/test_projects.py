import pytest
from httpx import AsyncClient
from sqlalchemy import select

from app.models import Milestone, Project, SubTeam, User, UserRole
from app.utils.auth import create_access_token, hash_password


async def _create_user(db_session, *, username: str, role: UserRole, sub_team_id=None):
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
async def test_project_sub_team_scoping(async_client: AsyncClient, db_session):
    """TEAM-03: Projects are scoped to sub-team"""
    sub_team = SubTeam(name="Projects Team")
    db_session.add(sub_team)
    manager = await _create_user(db_session, username="project_manager", role=UserRole.manager)
    await db_session.commit()
    token = create_access_token({"sub": str(manager.id)})

    response = await async_client.post(
        "/api/projects/",
        json={"name": "Test Project", "sub_team_id": sub_team.id},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 201
    project = response.json()
    assert project["sub_team_id"] == sub_team.id


@pytest.mark.asyncio
async def test_milestone_requires_project_id(db_session, async_client: AsyncClient):
    """SPRINT-02: Milestone must have project_id; API enforces project selection"""
    sub_team = SubTeam(name="Milestone Project Team")
    db_session.add(sub_team)
    manager = await _create_user(db_session, username="milestone_manager", role=UserRole.manager)
    await db_session.commit()
    token = create_access_token({"sub": str(manager.id)})

    project_response = await async_client.post(
        "/api/projects/",
        json={"name": "Test Project", "sub_team_id": sub_team.id},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert project_response.status_code == 201
    project = project_response.json()

    # Create milestone with valid project_id
    milestone_response = await async_client.post(
        "/api/milestones/",
        json={
            "title": "Test Milestone",
            "status": "planned",
            "project_id": project["id"],
            "due_date": "2026-05-01T00:00:00"
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    assert milestone_response.status_code == 201
    milestone = milestone_response.json()
    assert milestone["project_id"] == project["id"]

    # Verify milestone in database has project_id
    result = await db_session.execute(select(Milestone).where(Milestone.id == milestone["id"]))
    db_milestone = result.scalar_one_or_none()
    assert db_milestone is not None
    assert db_milestone.project_id == project["id"]
