import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_admin_all_teams(async_client: AsyncClient, admin_user, db_session):
    """TEAM-05: Admin can switch sub-teams via header, sees org-wide aggregates"""
    response = await async_client.get(
        "/api/dashboard",
        headers={"Cookie": f"access_token={admin_user.token}"}
    )
    assert response.status_code == 200
    # Assert counts reflect all teams when no header
    
    response = await async_client.get(
        "/api/dashboard",
        headers={
            "Cookie": f"access_token={admin_user.token}",
            "X-SubTeam-ID": "1"
        }
    )
    assert response.status_code == 200
    # Assert counts reflect filtered sub-team
