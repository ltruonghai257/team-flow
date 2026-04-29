import pytest
from httpx import AsyncClient
from datetime import datetime, timedelta

from app.models import Milestone, MilestoneDecision, Project, Task, User
from app.models.enums import MilestoneDecisionStatus
from app.utils.auth import create_access_token
from sqlalchemy import inspect as sa_inspect

def _auth_headers(user: User) -> dict[str, str]:
    token = create_access_token({"sub": str(sa_inspect(user).identity[0])})
    return {"Cookie": f"access_token={token}"}

@pytest.mark.asyncio
async def test_milestone_decision_crud(async_client: AsyncClient, user_with_sub_team, db_session):
    """Phase 28: Milestone decision CRUD and scope validation"""
    headers = _auth_headers(user_with_sub_team)
    
    # 1. Setup: Create Project and Milestone
    project_response = await async_client.post(
        "/api/projects/",
        json={"name": "Decision Test Project"},
        headers=headers
    )
    assert project_response.status_code == 201
    project_id = project_response.json()["id"]

    milestone_response = await async_client.post(
        "/api/milestones/",
        json={
            "title": "Decision Test Milestone",
            "project_id": project_id,
            "due_date": (datetime.now() + timedelta(days=30)).isoformat()
        },
        headers=headers
    )
    assert milestone_response.status_code == 201
    milestone_id = milestone_response.json()["id"]

    # 2. Create Decision
    decision_payload = {
        "milestone_id": milestone_id,
        "title": "Decision 1",
        "status": "proposed",
        "note": "Initial note"
    }
    response = await async_client.post(
        f"/api/milestones/{milestone_id}/decisions",
        json=decision_payload,
        headers=headers
    )
    assert response.status_code == 201
    decision = response.json()
    assert decision["title"] == "Decision 1"
    assert decision["status"] == "proposed"
    assert decision["milestone_id"] == milestone_id
    decision_id = decision["id"]

    # 3. List Decisions
    response = await async_client.get(
        f"/api/milestones/{milestone_id}/decisions",
        headers=headers
    )
    assert response.status_code == 200
    decisions = response.json()
    assert len(decisions) == 1
    assert decisions[0]["id"] == decision_id

    # 4. Update Decision
    update_payload = {
        "title": "Updated Decision 1",
        "status": "approved"
    }
    response = await async_client.patch(
        f"/api/milestones/decisions/{decision_id}",
        json=update_payload,
        headers=headers
    )
    assert response.status_code == 200
    updated_decision = response.json()
    assert updated_decision["title"] == "Updated Decision 1"
    assert updated_decision["status"] == "approved"

    # 5. Delete Decision
    response = await async_client.delete(
        f"/api/milestones/decisions/{decision_id}",
        headers=headers
    )
    assert response.status_code == 204

    # Verify deleted
    response = await async_client.get(
        f"/api/milestones/{milestone_id}/decisions",
        headers=headers
    )
    assert response.status_code == 200
    assert len(response.json()) == 0


@pytest.mark.asyncio
async def test_milestone_decision_task_scoping(async_client: AsyncClient, user_with_sub_team, db_session):
    """D-10/ML-04: Decisions can link to tasks, but only if they belong to the same milestone"""
    headers = _auth_headers(user_with_sub_team)
    
    # 1. Setup: Create Project, Milestone 1, Milestone 2
    project_response = await async_client.post(
        "/api/projects/",
        json={"name": "Scoping Test Project"},
        headers=headers
    )
    project_id = project_response.json()["id"]

    m1_response = await async_client.post(
        "/api/milestones/",
        json={
            "title": "Milestone 1",
            "project_id": project_id,
            "due_date": (datetime.now() + timedelta(days=30)).isoformat()
        },
        headers=headers
    )
    m1_id = m1_response.json()["id"]

    m2_response = await async_client.post(
        "/api/milestones/",
        json={
            "title": "Milestone 2",
            "project_id": project_id,
            "due_date": (datetime.now() + timedelta(days=30)).isoformat()
        },
        headers=headers
    )
    m2_id = m2_response.json()["id"]

    # 2. Create Task in Milestone 2
    task_response = await async_client.post(
        "/api/tasks/",
        json={
            "title": "Task in M2",
            "project_id": project_id,
            "milestone_id": m2_id
        },
        headers=headers
    )
    task_id = task_response.json()["id"]

    # 3. Try to create decision in Milestone 1 linked to Task in Milestone 2 (SHOULD FAIL)
    decision_payload = {
        "milestone_id": m1_id,
        "task_id": task_id,
        "title": "Invalid Link"
    }
    response = await async_client.post(
        f"/api/milestones/{m1_id}/decisions",
        json=decision_payload,
        headers=headers
    )
    assert response.status_code == 400
    assert "Task not found or not linked to this milestone" in response.json()["detail"]

    # 4. Create Task in Milestone 1
    task1_response = await async_client.post(
        "/api/tasks/",
        json={
            "title": "Task in M1",
            "project_id": project_id,
            "milestone_id": m1_id
        },
        headers=headers
    )
    task1_id = task1_response.json()["id"]

    # 5. Create decision in Milestone 1 linked to Task in Milestone 1 (SHOULD SUCCEED)
    decision_payload = {
        "milestone_id": m1_id,
        "task_id": task1_id,
        "title": "Valid Link"
    }
    response = await async_client.post(
        f"/api/milestones/{m1_id}/decisions",
        json=decision_payload,
        headers=headers
    )
    assert response.status_code == 201
    assert response.json()["task_id"] == task1_id


@pytest.mark.asyncio
async def test_milestone_command_view(async_client: AsyncClient, user_with_sub_team, db_session):
    """Phase 28: Milestone command-view lane derivation, rollups, and risk signals"""
    headers = _auth_headers(user_with_sub_team)
    user_id = sa_inspect(user_with_sub_team).identity[0]
    
    # Setup Project
    project_response = await async_client.post(
        "/api/projects/",
        json={"name": "Command View Project"},
        headers=headers
    )
    assert project_response.status_code == 201
    project_id = project_response.json()["id"]

    # 1. Planned Milestone (no dates, no tasks)
    await async_client.post(
        "/api/milestones/",
        json={
            "title": "Planned MS",
            "project_id": project_id,
            "due_date": (datetime.now() + timedelta(days=60)).isoformat()
        },
        headers=headers
    )

    # 2. Committed Milestone (dates + 1 task)
    m2_resp = await async_client.post(
        "/api/milestones/",
        json={
            "title": "Committed MS",
            "project_id": project_id,
            "start_date": (datetime.now() - timedelta(days=5)).isoformat(),
            "due_date": (datetime.now() + timedelta(days=25)).isoformat()
        },
        headers=headers
    )
    m2_id = m2_resp.json()["id"]
    
    # Add task assigned to user to make project/milestone visible and milestone committed
    await async_client.post(
        "/api/tasks/",
        json={
            "title": "Task 1",
            "project_id": project_id,
            "milestone_id": m2_id,
            "assignee_id": user_id
        },
        headers=headers
    )

    # 3. Active Milestone (status in_progress)
    m3_resp = await async_client.post(
        "/api/milestones/",
        json={
            "title": "Active MS",
            "project_id": project_id,
            "status": "in_progress",
            "due_date": (datetime.now() + timedelta(days=10)).isoformat()
        },
        headers=headers
    )
    m3_id = m3_resp.json()["id"]
    
    # Add blocked task to m3
    await async_client.post(
        "/api/tasks/",
        json={
            "title": "Blocked Task",
            "project_id": project_id,
            "milestone_id": m3_id,
            "status": "blocked",
            "assignee_id": user_id
        },
        headers=headers
    )

    # 4. Completed Milestone (status completed)
    await async_client.post(
        "/api/milestones/",
        json={
            "title": "Completed MS",
            "project_id": project_id,
            "status": "completed",
            "due_date": (datetime.now() - timedelta(days=1)).isoformat()
        },
        headers=headers
    )

    # 5. Delayed Milestone (status delayed)
    m5_resp = await async_client.post(
        "/api/milestones/",
        json={
            "title": "Delayed MS",
            "project_id": project_id,
            "status": "delayed",
            "due_date": (datetime.now() + timedelta(days=5)).isoformat()
        },
        headers=headers
    )
    m5_id = m5_resp.json()["id"]
    
    # Add a proposed decision to m5
    dec_resp = await async_client.post(
        f"/api/milestones/{m5_id}/decisions",
        json={
            "milestone_id": m5_id,
            "title": "Proposed Decision",
            "status": "proposed"
        },
        headers=headers
    )
    assert dec_resp.status_code == 201

    # Call Command View
    response = await async_client.get("/api/milestones/command-view/", headers=headers)
    assert response.status_code == 200
    data = response.json()
    
    metrics = data["metrics"]
    lanes = data["lanes"]
    
    # Assert Metrics
    assert metrics["active_milestones"] == 1 # m3
    assert metrics["risky_milestones"] >= 2 # m3 (blocked), m5 (delayed)
    assert metrics["proposed_decisions"] == 1
    assert metrics["blocked_tasks"] == 1
    
    # Assert Lanes
    # m1: planned (no start_date/no tasks)
    # m5: planned (status delayed is not in_progress/completed, and no start_date/tasks)
    assert len(lanes["planned"]) >= 2 
    assert len(lanes["committed"]) == 1 # m2
    assert len(lanes["active"]) == 1 # m3
    assert len(lanes["completed"]) == 1 # m4
    
    # Assert Risk Overlay
    active_ms = next(m for m in lanes["active"] if m["title"] == "Active MS")
    assert active_ms["risk"] == "blocked"
    
    delayed_ms = next(m for m in lanes["planned"] if m["title"] == "Delayed MS")
    assert delayed_ms["risk"] == "delayed"
    
    # Assert Rollups
    assert active_ms["progress"]["total"] == 1
    assert active_ms["progress"]["blocked"] == 1
    assert active_ms["progress"]["done"] == 0
    
    # Assert Decisions
    assert delayed_ms["decision_summary"]["proposed"] == 1
    assert len(delayed_ms["decisions"]) == 1
    assert delayed_ms["decisions"][0]["title"] == "Proposed Decision"
