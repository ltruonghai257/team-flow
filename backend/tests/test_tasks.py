from datetime import datetime, timedelta, timezone

import pytest
from httpx import AsyncClient
from sqlalchemy import select

from app.auth import hash_password
from app.models import (
    CustomStatus,
    Milestone,
    Project,
    Sprint,
    StatusSet,
    StatusSetScope,
    StatusTransition,
    SubTeam,
    Task,
    TaskPriority,
    TaskStatus,
    User,
    UserRole,
)
from app.auth import hash_password


def test_task_model_retains_legacy_status_and_custom_status_id():
    task = Task(title="Wire status", status=TaskStatus.todo, custom_status_id=42)

    assert task.status == TaskStatus.todo
    assert task.custom_status_id == 42


def test_created_task_can_resolve_custom_status_relationship():
    custom_status = CustomStatus(
        id=7,
        name="In Progress",
        slug="in_progress",
        color="#0ea5e9",
        position=1,
        is_done=False,
        legacy_status=TaskStatus.in_progress,
    )
    task = Task(
        title="Expose custom status",
        status=TaskStatus.in_progress,
        custom_status=custom_status,
    )

    assert task.custom_status_id is None
    assert task.custom_status.slug == "in_progress"


@pytest.mark.xfail(reason="Task update is_done transitions are implemented in 15-02.")
def test_moving_to_is_done_status_sets_completed_at():
    task = Task(title="Complete me", status=TaskStatus.in_progress)
    done_status = CustomStatus(
        id=4,
        name="Done",
        slug="done",
        color="#10b981",
        position=3,
        is_done=True,
        legacy_status=TaskStatus.done,
    )

    task.custom_status = done_status

    assert task.completed_at is not None


@pytest.mark.xfail(reason="Task update is_done transitions are implemented in 15-02.")
def test_moving_from_is_done_to_non_done_status_clears_completed_at():
    task = Task(
        title="Reopen me",
        status=TaskStatus.done,
        completed_at=datetime.now(timezone.utc).replace(tzinfo=None),
    )
    todo_status = CustomStatus(
        id=1,
        name="To Do",
        slug="todo",
        color="#64748b",
        position=0,
        is_done=False,
        legacy_status=TaskStatus.todo,
    )

    task.custom_status = todo_status

    assert task.completed_at is None


async def _login(async_client: AsyncClient, username: str) -> str:
    response = await async_client.post(
        "/api/auth/token",
        data={"username": username, "password": "password"},
    )
    assert response.status_code == 200
    return response.json()["access_token"]


async def _build_task_workflow_context(db_session, *, suffix: str = ""):
    sub_team = SubTeam(name=f"Task Team{suffix}", supervisor_id=None)
    db_session.add(sub_team)
    await db_session.commit()
    await db_session.refresh(sub_team)

    member = User(
        email=f"task-member{suffix}@example.com",
        username=f"task-member{suffix}".replace("_", "-"),
        full_name="Task Member",
        hashed_password=hash_password("password"),
        role=UserRole.member,
        sub_team_id=sub_team.id,
    )
    db_session.add(member)
    await db_session.commit()
    await db_session.refresh(member)

    status_set = StatusSet(
        scope=StatusSetScope.sub_team_default,
        sub_team_id=sub_team.id,
    )
    db_session.add(status_set)
    await db_session.commit()
    await db_session.refresh(status_set)

    todo = CustomStatus(
        status_set_id=status_set.id,
        name=f"To Do{suffix}",
        slug=f"todo{suffix}".strip("_"),
        color="#64748b",
        position=0,
        is_done=False,
        legacy_status=TaskStatus.todo,
    )
    review = CustomStatus(
        status_set_id=status_set.id,
        name=f"Review{suffix}",
        slug=f"review{suffix}".strip("_"),
        color="#f59e0b",
        position=1,
        is_done=False,
        legacy_status=TaskStatus.review,
    )
    done = CustomStatus(
        status_set_id=status_set.id,
        name=f"Done{suffix}",
        slug=f"done{suffix}".strip("_"),
        color="#10b981",
        position=2,
        is_done=True,
        legacy_status=TaskStatus.done,
    )
    db_session.add_all([todo, review, done])
    await db_session.commit()
    await db_session.refresh(todo)
    await db_session.refresh(review)
    await db_session.refresh(done)

    project = Project(name=f"Workflow Project{suffix}", sub_team_id=sub_team.id)
    db_session.add(project)
    await db_session.commit()
    await db_session.refresh(project)

    task = Task(
        title=f"Workflow Task{suffix}",
        status=TaskStatus.todo,
        priority=TaskPriority.medium,
        project_id=project.id,
        creator_id=member.id,
        custom_status_id=todo.id,
    )
    db_session.add(task)
    await db_session.commit()
    await db_session.refresh(task)

    return {
        "sub_team": sub_team,
        "member": member,
        "status_set": status_set,
        "todo": todo,
        "review": review,
        "done": done,
        "project": project,
        "task": task,
    }


@pytest.mark.asyncio
async def test_task_sprint_id_persistence(db_session):
    """SPRINT-03: Task create/edit accepts and persists sprint_id"""
    # Create test data
    sub_team = SubTeam(name="Test Team", supervisor_id=None)
    db_session.add(sub_team)
    await db_session.commit()
    await db_session.refresh(sub_team)

    user = User(
        email="test@example.com",
        username="testuser",
        full_name="Test User",
        hashed_password=hash_password("password"),
        role=UserRole.member,
        sub_team_id=sub_team.id
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    project = Project(name="Test Project", sub_team_id=sub_team.id)
    db_session.add(project)
    await db_session.commit()
    await db_session.refresh(project)

    milestone = Milestone(
        title="Test Milestone",
        status="planned",
        due_date=datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(days=7),
        project_id=project.id,
    )
    db_session.add(milestone)
    await db_session.commit()
    await db_session.refresh(milestone)

    sprint = Sprint(
        name="Test Sprint",
        start_date=datetime(2026, 4, 27, 0, 0, 0),
        end_date=datetime(2026, 5, 10, 23, 59, 59),
        milestone_id=milestone.id,
    )
    db_session.add(sprint)
    await db_session.commit()
    await db_session.refresh(sprint)

    # Create task with sprint_id
    task = Task(
        title="Test Task",
        status=TaskStatus.todo,
        project_id=project.id,
        milestone_id=milestone.id,
        sprint_id=sprint.id,
        creator_id=user.id
    )
    db_session.add(task)
    await db_session.commit()
    await db_session.refresh(task)

    # Verify sprint_id is persisted
    assert task.sprint_id == sprint.id

    # Edit task to remove sprint_id
    task.sprint_id = None
    await db_session.commit()
    await db_session.refresh(task)

    # Verify sprint_id is nullable
    assert task.sprint_id is None


@pytest.mark.asyncio
async def test_task_sprint_filtering(db_session):
    """SPRINT-04: Task API filters by sprint_id and unassigned tasks"""
    # Create test data
    sub_team = SubTeam(name="Test Team", supervisor_id=None)
    db_session.add(sub_team)
    await db_session.commit()
    await db_session.refresh(sub_team)

    user = User(
        email="test@example.com",
        username="testuser",
        full_name="Test User",
        hashed_password=hash_password("password"),
        role=UserRole.member,
        sub_team_id=sub_team.id
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    project = Project(name="Test Project", sub_team_id=sub_team.id)
    db_session.add(project)
    await db_session.commit()
    await db_session.refresh(project)

    milestone = Milestone(
        title="Test Milestone",
        status="planned",
        due_date=datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(days=7),
        project_id=project.id,
    )
    db_session.add(milestone)
    await db_session.commit()
    await db_session.refresh(milestone)

    sprint1 = Sprint(
        name="Sprint 1",
        start_date=datetime(2026, 4, 27, 0, 0, 0),
        end_date=datetime(2026, 5, 10, 23, 59, 59),
        milestone_id=milestone.id,
    )
    sprint2 = Sprint(
        name="Sprint 2",
        start_date=datetime(2026, 5, 11, 0, 0, 0),
        end_date=datetime(2026, 5, 24, 23, 59, 59),
        milestone_id=milestone.id,
    )
    db_session.add_all([sprint1, sprint2])
    await db_session.commit()
    await db_session.refresh(sprint1)
    await db_session.refresh(sprint2)

    # Create tasks in different sprints
    task1 = Task(title="Task in Sprint 1", status=TaskStatus.todo, project_id=project.id, milestone_id=milestone.id, sprint_id=sprint1.id, creator_id=user.id)
    task2 = Task(title="Task in Sprint 2", status=TaskStatus.todo, project_id=project.id, milestone_id=milestone.id, sprint_id=sprint2.id, creator_id=user.id)
    task3 = Task(title="Backlog Task", status=TaskStatus.todo, project_id=project.id, milestone_id=milestone.id, sprint_id=None, creator_id=user.id)
    db_session.add_all([task1, task2, task3])
    await db_session.commit()

    # Query tasks by sprint_id
    result = await db_session.execute(
        select(Task).where(Task.sprint_id == sprint1.id)
    )
    sprint1_tasks = result.scalars().all()
    assert len(sprint1_tasks) == 1
    assert sprint1_tasks[0].id == task1.id

    # Query unassigned tasks (backlog)
    result = await db_session.execute(
        select(Task).where(Task.sprint_id.is_(None))
    )
    backlog_tasks = result.scalars().all()
    assert len(backlog_tasks) == 1
    assert backlog_tasks[0].id == task3.id


@pytest.mark.asyncio
async def test_task_update_allows_free_movement_when_transition_graph_is_empty(
    async_client: AsyncClient, db_session
):
    data = await _build_task_workflow_context(db_session, suffix="_free")
    task_id = data["task"].id
    review_id = data["review"].id
    token = await _login(async_client, data["member"].username)
    headers = {"Authorization": f"Bearer {token}"}

    response = await async_client.patch(
        f"/api/tasks/{task_id}",
        json={"custom_status_id": review_id},
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json()["custom_status_id"] == review_id


@pytest.mark.asyncio
async def test_task_update_blocks_non_listed_transition_with_structured_detail(
    async_client: AsyncClient, db_session
):
    data = await _build_task_workflow_context(db_session, suffix="_blocked")
    status_set_id = data["status_set"].id
    todo_id = data["todo"].id
    review_id = data["review"].id
    done_id = data["done"].id
    task_id = data["task"].id
    db_session.add(
        StatusTransition(
            status_set_id=status_set_id,
            from_status_id=todo_id,
            to_status_id=review_id,
        )
    )
    await db_session.commit()

    token = await _login(async_client, data["member"].username)
    headers = {"Authorization": f"Bearer {token}"}
    response = await async_client.patch(
        f"/api/tasks/{task_id}",
        json={"custom_status_id": done_id},
        headers=headers,
    )

    assert response.status_code == 422
    detail = response.json()["detail"]
    assert detail["code"] == "status_transition_blocked"
    assert detail["current_status_id"] == todo_id
    assert detail["target_status_id"] == done_id
    assert detail["allowed_status_ids"] == [review_id]


@pytest.mark.asyncio
async def test_task_update_uses_legacy_status_mapping_before_enforcement(
    async_client: AsyncClient, db_session
):
    data = await _build_task_workflow_context(db_session, suffix="_legacy")
    task_id = data["task"].id
    status_set_id = data["status_set"].id
    todo_id = data["todo"].id
    review_id = data["review"].id
    data["task"].custom_status_id = None
    await db_session.commit()
    db_session.add(
        StatusTransition(
            status_set_id=status_set_id,
            from_status_id=todo_id,
            to_status_id=review_id,
        )
    )
    await db_session.commit()

    token = await _login(async_client, data["member"].username)
    headers = {"Authorization": f"Bearer {token}"}
    response = await async_client.patch(
        f"/api/tasks/{task_id}",
        json={"status": "review"},
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json()["custom_status_id"] == review_id
    assert response.json()["status"] == "review"


@pytest.mark.asyncio
async def test_task_update_does_not_block_ordinary_field_edits(
    async_client: AsyncClient, db_session
):
    data = await _build_task_workflow_context(db_session, suffix="_ordinary")
    task_id = data["task"].id
    db_session.add(
        StatusTransition(
            status_set_id=data["status_set"].id,
            from_status_id=data["todo"].id,
            to_status_id=data["review"].id,
        )
    )
    await db_session.commit()

    token = await _login(async_client, data["member"].username)
    headers = {"Authorization": f"Bearer {token}"}
    response = await async_client.patch(
        f"/api/tasks/{task_id}",
        json={"title": "Renamed task", "priority": "high"},
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json()["title"] == "Renamed task"
    assert response.json()["priority"] == "high"
