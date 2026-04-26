from datetime import datetime, timezone

import pytest

from app.models import CustomStatus, Task, TaskStatus


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
