import pytest
from httpx import AsyncClient

from app.models import Milestone, Project
from app.utils.auth import hash_password

@pytest.mark.asyncio
async def test_project_sub_team_scoping(async_client: AsyncClient, admin_user, db_session):
    """TEAM-03: Projects are scoped to sub-team"""
    response = await async_client.post(
        "/api/projects",
        json={"name": "Test Project", "sub_team_id": 1},
        headers={"Cookie": f"access_token={admin_user.token}"}
    )
    assert response.status_code == 200
    project = response.json()
    assert project["sub_team_id"] == 1


@pytest.mark.asyncio
async def test_milestone_requires_project_id(db_session, async_client: AsyncClient, admin_user):
    """SPRINT-02: Milestone must have project_id; API enforces project selection"""
    # Create a project first
    project_response = await async_client.post(
        "/api/projects",
        json={"name": "Test Project", "sub_team_id": 1},
        headers={"Cookie": f"access_token={admin_user.token}"}
    )
    assert project_response.status_code == 200
    project = project_response.json()

    # Create milestone with valid project_id
    milestone_response = await async_client.post(
        "/api/milestones",
        json={
            "title": "Test Milestone",
            "status": "planned",
            "project_id": project["id"],
            "due_date": "2026-05-01T00:00:00"
        },
        headers={"Cookie": f"access_token={admin_user.token}"}
    )
    assert milestone_response.status_code == 200
    milestone = milestone_response.json()
    assert milestone["project_id"] == project["id"]

    # Verify milestone in database has project_id
    result = await db_session.execute(
        db_session.query(Milestone).filter(Milestone.id == milestone["id"])
    )
    db_milestone = result.scalar_one_or_none()
    assert db_milestone is not None
    assert db_milestone.project_id == project["id"]
