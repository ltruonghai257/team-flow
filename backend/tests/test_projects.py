import pytest
from httpx import AsyncClient

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
