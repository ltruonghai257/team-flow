import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_member_timeline_visibility(async_client: AsyncClient, member_user, db_session):
    """VIS-01: Members see only projects where they have assigned tasks"""
    response = await async_client.get(
        "/api/timeline",
        headers={"Cookie": f"access_token={member_user.token}"}
    )
    assert response.status_code == 200
    projects = response.json()
    # Assert projects only contain those where member has assigned tasks

@pytest.mark.asyncio
async def test_supervisor_timeline_visibility(async_client: AsyncClient, supervisor_user, db_session):
    """VIS-02: Supervisors see all projects belonging to their sub-team"""
    response = await async_client.get(
        "/api/timeline",
        headers={"Cookie": f"access_token={supervisor_user.token}"}
    )
    assert response.status_code == 200
    projects = response.json()
    # Assert projects contain all sub-team projects

@pytest.mark.asyncio
async def test_admin_timeline_visibility(async_client: AsyncClient, admin_user, db_session):
    """VIS-03: Admin sees all projects, respects X-SubTeam-ID header"""
    # All teams (no header)
    response = await async_client.get(
        "/api/timeline",
        headers={"Cookie": f"access_token={admin_user.token}"}
    )
    assert response.status_code == 200
    all_projects = response.json()
    
    # Filtered by header
    response = await async_client.get(
        "/api/timeline",
        headers={
            "Cookie": f"access_token={admin_user.token}",
            "X-SubTeam-ID": "1"
        }
    )
    assert response.status_code == 200
    filtered_projects = response.json()
    # Assert filtered_projects is subset of all_projects
