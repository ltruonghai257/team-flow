from datetime import datetime, timedelta, timezone

import pytest
from httpx import AsyncClient
from sqlalchemy import inspect as sa_inspect

from app.models import User
from app.utils.auth import create_access_token


def _auth_headers(user: User) -> dict[str, str]:
    token = create_access_token({"sub": str(sa_inspect(user).identity[0])})
    return {"Cookie": f"access_token={token}"}


def _future_iso(days: int) -> str:
    return (datetime.now(timezone.utc) + timedelta(days=days)).isoformat()


async def _create_project(async_client: AsyncClient, headers: dict[str, str], name: str) -> int:
    response = await async_client.post("/api/projects/", json={"name": name}, headers=headers)
    assert response.status_code == 201
    return response.json()["id"]


async def _create_milestone(
    async_client: AsyncClient,
    headers: dict[str, str],
    project_id: int,
    title: str,
    due_in_days: int = 30,
    start_in_days: int | None = None,
    status: str = "planned",
) -> int:
    payload = {
        "title": title,
        "project_id": project_id,
        "status": status,
        "due_date": _future_iso(due_in_days),
    }
    if start_in_days is not None:
        payload["start_date"] = _future_iso(start_in_days)
    response = await async_client.post("/api/milestones/", json=payload, headers=headers)
    assert response.status_code == 201
    return response.json()["id"]


async def _create_task(
    async_client: AsyncClient,
    headers: dict[str, str],
    project_id: int,
    title: str,
    milestone_id: int | None = None,
    status: str = "todo",
    assignee_id: int | None = None,
) -> int:
    payload: dict[str, object] = {
        "title": title,
        "project_id": project_id,
        "status": status,
    }
    if milestone_id is not None:
        payload["milestone_id"] = milestone_id
    if assignee_id is not None:
        payload["assignee_id"] = assignee_id
    response = await async_client.post("/api/tasks/", json=payload, headers=headers)
    assert response.status_code == 201
    return response.json()["id"]


@pytest.mark.asyncio
async def test_milestone_decision_crud_and_status_values(
    async_client: AsyncClient,
    user_with_sub_team,
):
    headers = _auth_headers(user_with_sub_team)
    project_id = await _create_project(async_client, headers, "Decision Test Project")
    milestone_id = await _create_milestone(
        async_client, headers, project_id, "Decision Test Milestone"
    )

    created = []
    for idx, status in enumerate(
        ["proposed", "approved", "rejected", "superseded"], start=1
    ):
        response = await async_client.post(
            f"/api/milestones/{milestone_id}/decisions",
            json={
                "title": f"Decision {idx}",
                "status": status,
                "note": f"Note {idx}",
            },
            headers=headers,
        )
        assert response.status_code == 201
        created.append(response.json())

    assert {item["status"] for item in created} == {
        "proposed",
        "approved",
        "rejected",
        "superseded",
    }

    listed = await async_client.get(
        f"/api/milestones/{milestone_id}/decisions",
        headers=headers,
    )
    assert listed.status_code == 200
    assert {item["status"] for item in listed.json()} == {
        "proposed",
        "approved",
        "rejected",
        "superseded",
    }

    decision_id = created[0]["id"]
    update_response = await async_client.patch(
        f"/api/milestones/{milestone_id}/decisions/{decision_id}",
        json={"title": "Decision 1 updated", "status": "approved"},
        headers=headers,
    )
    assert update_response.status_code == 200
    assert update_response.json()["title"] == "Decision 1 updated"
    assert update_response.json()["status"] == "approved"

    delete_response = await async_client.delete(
        f"/api/milestones/{milestone_id}/decisions/{created[1]['id']}",
        headers=headers,
    )
    assert delete_response.status_code == 204

    after_delete = await async_client.get(
        f"/api/milestones/{milestone_id}/decisions",
        headers=headers,
    )
    assert after_delete.status_code == 200
    assert len(after_delete.json()) == 3


@pytest.mark.asyncio
async def test_milestone_decision_task_scope_allows_same_project_and_rejects_cross_project(
    async_client: AsyncClient,
    user_with_sub_team,
):
    headers = _auth_headers(user_with_sub_team)
    project_id = await _create_project(async_client, headers, "Scope Project")
    milestone_one_id = await _create_milestone(
        async_client, headers, project_id, "Milestone One"
    )
    milestone_two_id = await _create_milestone(
        async_client, headers, project_id, "Milestone Two"
    )
    same_project_task_id = await _create_task(
        async_client,
        headers,
        project_id,
        "Same project task",
        milestone_id=milestone_two_id,
    )

    other_project_id = await _create_project(async_client, headers, "Other Project")
    cross_project_task_id = await _create_task(
        async_client,
        headers,
        other_project_id,
        "Cross project task",
    )

    allowed_response = await async_client.post(
        f"/api/milestones/{milestone_one_id}/decisions",
        json={
            "title": "Allowed decision",
            "task_id": same_project_task_id,
            "status": "proposed",
        },
        headers=headers,
    )
    assert allowed_response.status_code == 201
    assert allowed_response.json()["task_id"] == same_project_task_id

    rejected_response = await async_client.post(
        f"/api/milestones/{milestone_one_id}/decisions",
        json={
            "title": "Rejected decision",
            "task_id": cross_project_task_id,
            "status": "proposed",
        },
        headers=headers,
    )
    assert rejected_response.status_code == 400
    assert "milestone project" in rejected_response.json()["detail"]

    created_decision_id = allowed_response.json()["id"]
    update_reject = await async_client.patch(
        f"/api/milestones/{milestone_one_id}/decisions/{created_decision_id}",
        json={"task_id": cross_project_task_id},
        headers=headers,
    )
    assert update_reject.status_code == 400
    assert "milestone project" in update_reject.json()["detail"]


@pytest.mark.asyncio
async def test_milestone_command_view(
    async_client: AsyncClient,
    user_with_sub_team,
):
    headers = _auth_headers(user_with_sub_team)

    project_id = await _create_project(async_client, headers, "Command View Project")

    await _create_milestone(async_client, headers, project_id, "Planned MS", due_in_days=60)

    committed_id = await _create_milestone(
        async_client,
        headers,
        project_id,
        "Committed MS",
        due_in_days=25,
        start_in_days=-5,
    )
    user_id = sa_inspect(user_with_sub_team).identity[0]
    await _create_task(
        async_client,
        headers,
        project_id,
        "Task 1",
        milestone_id=committed_id,
        assignee_id=user_id,
    )

    active_id = await _create_milestone(
        async_client,
        headers,
        project_id,
        "Active MS",
        due_in_days=10,
        status="in_progress",
    )
    await _create_task(
        async_client,
        headers,
        project_id,
        "Blocked Task",
        milestone_id=active_id,
        status="blocked",
        assignee_id=user_id,
    )

    await _create_milestone(
        async_client,
        headers,
        project_id,
        "Completed MS",
        due_in_days=-1,
        status="completed",
    )

    delayed_id = await _create_milestone(
        async_client,
        headers,
        project_id,
        "Delayed MS",
        due_in_days=5,
        status="delayed",
    )
    decision_response = await async_client.post(
        f"/api/milestones/{delayed_id}/decisions",
        json={
            "title": "Proposed Decision",
            "status": "proposed",
        },
        headers=headers,
    )
    assert decision_response.status_code == 201

    response = await async_client.get("/api/milestones/command-view/", headers=headers)
    assert response.status_code == 200
    data = response.json()

    metrics = data["metrics"]
    lanes = data["lanes"]

    assert metrics["active_milestones"] == 1
    assert metrics["risky_milestones"] >= 2
    assert metrics["proposed_decisions"] == 1
    assert metrics["blocked_tasks"] == 1

    assert len(lanes["planned"]) >= 2
    assert len(lanes["committed"]) == 1
    assert len(lanes["active"]) == 1
    assert len(lanes["completed"]) == 1

    active_ms = next(m for m in lanes["active"] if m["title"] == "Active MS")
    assert active_ms["risk"] == "blocked"
    assert active_ms["progress"]["total"] == 1
    assert active_ms["progress"]["blocked"] == 1
    assert active_ms["progress"]["done"] == 0

    delayed_ms = next(m for m in lanes["planned"] if m["title"] == "Delayed MS")
    assert delayed_ms["risk"] == "delayed"
    assert delayed_ms["decision_summary"]["proposed"] == 1
    assert len(delayed_ms["decisions"]) == 1
    assert delayed_ms["decisions"][0]["title"] == "Proposed Decision"
