import pytest
from httpx import AsyncClient
from sqlalchemy import select

@pytest.mark.asyncio
async def test_admin_crud_sub_team(async_client: AsyncClient, db_session, admin_user):
    """TEAM-01: Admin can create, list, update, delete sub-teams"""
    # Create sub-team
    response = await async_client.post(
        "/api/sub-teams",
        json={"name": "Engineering", "supervisor_id": None},
        headers={"Cookie": f"access_token={admin_user.token}"}
    )
    assert response.status_code == 200
    sub_team = response.json()
    assert sub_team["name"] == "Engineering"
    
    # List sub-teams
    response = await async_client.get(
        "/api/sub-teams",
        headers={"Cookie": f"access_token={admin_user.token}"}
    )
    assert response.status_code == 200
    sub_teams = response.json()
    assert len(sub_teams) >= 1
    
    # Update sub-team
    response = await async_client.put(
        f"/api/sub-teams/{sub_team['id']}",
        json={"name": "Engineering Team"},
        headers={"Cookie": f"access_token={admin_user.token}"}
    )
    assert response.status_code == 200
    
    # Delete sub-team
    response = await async_client.delete(
        f"/api/sub-teams/{sub_team['id']}",
        headers={"Cookie": f"access_token={admin_user.token}"}
    )
    assert response.status_code == 200
