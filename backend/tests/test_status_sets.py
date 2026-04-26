from app.models import CustomStatus, StatusSet, StatusSetScope, TaskStatus


def test_default_status_set_model_includes_seeded_legacy_statuses():
    status_set = StatusSet(scope=StatusSetScope.sub_team_default, sub_team_id=1)
    status_set.statuses = [
        CustomStatus(
            name="To Do",
            slug="todo",
            color="#64748b",
            position=0,
            is_done=False,
            legacy_status=TaskStatus.todo,
        ),
        CustomStatus(
            name="In Progress",
            slug="in_progress",
            color="#0ea5e9",
            position=1,
            is_done=False,
            legacy_status=TaskStatus.in_progress,
        ),
        CustomStatus(
            name="Review",
            slug="review",
            color="#f59e0b",
            position=2,
            is_done=False,
            legacy_status=TaskStatus.review,
        ),
        CustomStatus(
            name="Done",
            slug="done",
            color="#10b981",
            position=3,
            is_done=True,
            legacy_status=TaskStatus.done,
        ),
        CustomStatus(
            name="Blocked",
            slug="blocked",
            color="#f43f5e",
            position=4,
            is_done=False,
            legacy_status=TaskStatus.blocked,
        ),
    ]

    assert [status.slug for status in status_set.statuses] == [
        "todo",
        "in_progress",
        "review",
        "done",
        "blocked",
    ]
    assert [status.legacy_status for status in status_set.statuses] == [
        TaskStatus.todo,
        TaskStatus.in_progress,
        TaskStatus.review,
        TaskStatus.done,
        TaskStatus.blocked,
    ]


def test_done_status_has_is_done_true():
    done_status = CustomStatus(
        name="Done",
        slug="done",
        color="#10b981",
        position=3,
        is_done=True,
        legacy_status=TaskStatus.done,
    )

    assert done_status.is_done is True
