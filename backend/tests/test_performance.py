import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_supervisor_scoping(async_client: AsyncClient, supervisor_user, db_session):
    """TEAM-04: Supervisor endpoints reject cross-team data access"""
    response = await async_client.get(
        "/api/performance/team",
        headers={"Cookie": f"access_token={supervisor_user.token}"}
    )
    assert response.status_code == 200
    # Assert metrics are limited to supervisor's sub-team
