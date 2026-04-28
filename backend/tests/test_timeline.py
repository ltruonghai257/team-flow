from datetime import datetime

import pytest
import pytest_asyncio
from httpx import AsyncClient

from app.models import (
    CustomStatus,
    Milestone,
    MilestoneStatus,
    Project,
    StatusSet,
    StatusSetScope,
    SubTeam,
    Task,
    TaskPriority,
    TaskStatus,
    TaskType,
    User,
    UserRole,
)
from app.utils.auth import hash_password


async def _login(async_client: AsyncClient, username: str, password: str = "password") -> str:
    response = await async_client.post(
        "/api/auth/token",
        data={"username": username, "password": password},
    )
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest_asyncio.fixture
async def timeline_graph(db_session):
    team_a = SubTeam(name="Alpha")
    team_b = SubTeam(name="Beta")
    db_session.add_all([team_a, team_b])
    await db_session.flush()

    admin = User(
        email="admin@example.com",
        username="admin",
        full_name="Admin User",
        hashed_password=hash_password("password"),
        role=UserRole.admin,
    )
    supervisor_a = User(
        email="sup-a@example.com",
        username="supervisor-a",
        full_name="Supervisor A",
        hashed_password=hash_password("password"),
        role=UserRole.supervisor,
        sub_team_id=team_a.id,
    )
    member_a = User(
        email="member-a@example.com",
        username="member-a",
        full_name="Member A",
        hashed_password=hash_password("password"),
        role=UserRole.member,
        sub_team_id=team_a.id,
    )
    member_b = User(
        email="member-b@example.com",
        username="member-b",
        full_name="Member B",
        hashed_password=hash_password("password"),
        role=UserRole.member,
        sub_team_id=team_b.id,
    )
    db_session.add_all([admin, supervisor_a, member_a, member_b])
    await db_session.flush()

    team_a.supervisor_id = supervisor_a.id

    project_a = Project(name="Project Alpha", color="#22c55e", sub_team_id=team_a.id)
    project_b = Project(name="Project Beta", color="#ef4444", sub_team_id=team_b.id)
    db_session.add_all([project_a, project_b])
    await db_session.flush()

    status_set = StatusSet(scope=StatusSetScope.project, project_id=project_a.id)
    db_session.add(status_set)
    await db_session.flush()

    blocked_status = CustomStatus(
        status_set_id=status_set.id,
        name="Blocked",
        slug="blocked",
        color="#ef4444",
        position=1,
        is_done=False,
    )
    done_status = CustomStatus(
        status_set_id=status_set.id,
        name="Done",
        slug="done",
        color="#22c55e",
        position=2,
        is_done=True,
    )
    db_session.add_all([blocked_status, done_status])
    await db_session.flush()

    milestone_a = Milestone(
        title="Alpha Milestone",
        description="Milestone for planning context",
        status=MilestoneStatus.in_progress,
        project_id=project_a.id,
        due_date=datetime(2026, 6, 10),
    )
    milestone_b = Milestone(
        title="Beta Milestone",
        description="Other team milestone",
        status=MilestoneStatus.planned,
        project_id=project_b.id,
        due_date=datetime(2026, 6, 20),
    )
    db_session.add_all([milestone_a, milestone_b])
    await db_session.flush()

    db_session.add_all(
        [
            Task(
                title="Alpha assigned task",
                description="Needs follow up",
                tags="timeline,risk",
                status=TaskStatus.blocked,
                priority=TaskPriority.critical,
                type=TaskType.task,
                project_id=project_a.id,
                milestone_id=milestone_a.id,
                assignee_id=member_a.id,
                creator_id=supervisor_a.id,
                custom_status_id=blocked_status.id,
            ),
            Task(
                title="Alpha unassigned task",
                description="Unassigned planning work",
                tags="planning",
                status=TaskStatus.todo,
                priority=TaskPriority.medium,
                type=TaskType.task,
                project_id=project_a.id,
                creator_id=supervisor_a.id,
                custom_status_id=done_status.id,
            ),
            Task(
                title="Beta assigned task",
                description="Other sub-team task",
                tags="beta",
                status=TaskStatus.todo,
                priority=TaskPriority.low,
                type=TaskType.task,
                project_id=project_b.id,
                milestone_id=milestone_b.id,
                assignee_id=member_b.id,
                creator_id=member_b.id,
            ),
        ]
    )
    await db_session.commit()

    return {
        "team_a_id": team_a.id,
        "admin_username": admin.username,
        "supervisor_a_username": supervisor_a.username,
        "member_a_username": member_a.username,
    }


@pytest.mark.asyncio
async def test_member_timeline_visibility_and_shape(
    async_client: AsyncClient, timeline_graph
):
    token = await _login(async_client, timeline_graph["member_a_username"])
    response = await async_client.get(
        "/api/timeline/",
        headers={"Cookie": f"access_token={token}"},
    )
    assert response.status_code == 200
    projects = response.json()
    assert [project["name"] for project in projects] == ["Project Alpha"]

    milestone = projects[0]["milestones"][0]
    assert milestone["description"] == "Milestone for planning context"
    assert milestone["completed_at"] is None

    task = milestone["tasks"][0]
    assert task["description"] == "Needs follow up"
    assert task["tags"] == "timeline,risk"
    assert task["custom_status"]["slug"] == "blocked"


@pytest.mark.asyncio
async def test_supervisor_timeline_visibility_and_shape(
    async_client: AsyncClient, timeline_graph
):
    token = await _login(async_client, timeline_graph["supervisor_a_username"])
    response = await async_client.get(
        "/api/timeline/",
        headers={"Cookie": f"access_token={token}"},
    )
    assert response.status_code == 200
    projects = response.json()
    assert [project["name"] for project in projects] == ["Project Alpha"]
    assert len(projects[0]["unassigned_tasks"]) == 1
    assert projects[0]["unassigned_tasks"][0]["custom_status"]["is_done"] is True


@pytest.mark.asyncio
async def test_admin_timeline_visibility_respects_sub_team_header(
    async_client: AsyncClient, timeline_graph
):
    token = await _login(async_client, timeline_graph["admin_username"])

    all_response = await async_client.get(
        "/api/timeline/",
        headers={"Cookie": f"access_token={token}"},
    )
    assert all_response.status_code == 200
    all_names = {project["name"] for project in all_response.json()}
    assert all_names == {"Project Alpha", "Project Beta"}

    filtered_response = await async_client.get(
        "/api/timeline/",
        headers={
            "Cookie": f"access_token={token}",
            "X-SubTeam-ID": str(timeline_graph["team_a_id"]),
        },
    )
    assert filtered_response.status_code == 200
    filtered_projects = filtered_response.json()
    assert [project["name"] for project in filtered_projects] == ["Project Alpha"]
