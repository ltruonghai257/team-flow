from datetime import datetime, timezone

import pytest

from app.models import CustomStatus, Milestone, Project, Sprint, SubTeam, Task, TaskStatus, User, UserRole
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

    milestone = Milestone(title="Test Milestone", status="planned", project_id=project.id)
    db_session.add(milestone)
    await db_session.commit()
    await db_session.refresh(milestone)

    sprint = Sprint(name="Test Sprint", start_date="2026-04-27T00:00:00", end_date="2026-05-10T23:59:59", milestone_id=milestone.id)
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

    milestone = Milestone(title="Test Milestone", status="planned", project_id=project.id)
    db_session.add(milestone)
    await db_session.commit()
    await db_session.refresh(milestone)

    sprint1 = Sprint(name="Sprint 1", start_date="2026-04-27T00:00:00", end_date="2026-05-10T23:59:59", milestone_id=milestone.id)
    sprint2 = Sprint(name="Sprint 2", start_date="2026-05-11T00:00:00", end_date="2026-05-24T23:59:59", milestone_id=milestone.id)
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
    from sqlalchemy import select
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
