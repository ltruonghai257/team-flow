from datetime import datetime, timedelta, timezone

import pytest
from httpx import AsyncClient
from sqlalchemy import select

from app.utils.auth import hash_password
from app.models import (
    EventNotification,
    Milestone,
    MilestoneStatus,
    NotificationEventType,
    NotificationStatus,
    Project,
    Schedule,
    Sprint,
    SprintStatus,
    SubTeam,
    Task,
    TaskStatus,
    User,
    UserRole,
)
from app.services.reminder_notifications import (
    get_or_create_reminder_settings,
    rebuild_milestone_reminders,
    rebuild_sprint_reminders,
    reconcile_generated_reminders,
)


async def _create_user(
    db_session,
    *,
    email: str,
    username: str,
    full_name: str,
    role: UserRole,
    sub_team_id: int,
) -> User:
    user = User(
        email=email,
        username=username,
        full_name=full_name,
        hashed_password=hash_password("password"),
        role=role,
        sub_team_id=sub_team_id,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


async def _build_team_graph(db_session, *, sprint_hours: int = 48, milestone_hours: int = 72):
    sub_team = SubTeam(name="Reminder Team", supervisor_id=None)
    db_session.add(sub_team)
    await db_session.commit()
    await db_session.refresh(sub_team)

    supervisor = await _create_user(
        db_session,
        email="lead@example.com",
        username="lead",
        full_name="Lead User",
        role=UserRole.supervisor,
        sub_team_id=sub_team.id,
    )
    participant = await _create_user(
        db_session,
        email="member@example.com",
        username="member",
        full_name="Member User",
        role=UserRole.member,
        sub_team_id=sub_team.id,
    )

    sub_team.supervisor_id = supervisor.id
    await db_session.commit()
    await db_session.refresh(sub_team)

    project = Project(name="Reminder Project", sub_team_id=sub_team.id)
    db_session.add(project)
    await db_session.commit()
    await db_session.refresh(project)

    milestone = Milestone(
        title="Launch",
        status=MilestoneStatus.planned,
        due_date=datetime.now(timezone.utc).replace(tzinfo=None)
        + timedelta(hours=milestone_hours),
        project_id=project.id,
    )
    db_session.add(milestone)
    await db_session.commit()
    await db_session.refresh(milestone)

    sprint = Sprint(
        name="Sprint 1",
        status=SprintStatus.planned,
        end_date=datetime.now(timezone.utc).replace(tzinfo=None)
        + timedelta(hours=sprint_hours),
        milestone_id=milestone.id,
    )
    db_session.add(sprint)
    await db_session.commit()
    await db_session.refresh(sprint)

    supervisor_task = Task(
        title="Lead task",
        status=TaskStatus.todo,
        project_id=project.id,
        milestone_id=milestone.id,
        sprint_id=sprint.id,
        assignee_id=supervisor.id,
        creator_id=supervisor.id,
    )
    participant_task = Task(
        title="Member task",
        status=TaskStatus.todo,
        project_id=project.id,
        milestone_id=milestone.id,
        sprint_id=sprint.id,
        assignee_id=participant.id,
        creator_id=supervisor.id,
    )
    db_session.add_all([supervisor_task, participant_task])
    await db_session.commit()
    return {
        "sub_team": sub_team,
        "supervisor": supervisor,
        "participant": participant,
        "project": project,
        "milestone": milestone,
        "sprint": sprint,
    }


@pytest.mark.asyncio
async def test_generated_sprint_reminders_include_participants_and_supervisors(db_session):
    data = await _build_team_graph(db_session)
    created = await rebuild_sprint_reminders(db_session, data["sprint"].id)
    assert created == 2

    result = await db_session.execute(
        select(EventNotification)
        .where(
            EventNotification.event_type == NotificationEventType.sprint_end,
            EventNotification.event_ref_id == data["sprint"].id,
        )
        .order_by(EventNotification.user_id)
    )
    rows = result.scalars().all()
    assert len(rows) == 2
    assert {row.user_id for row in rows} == {
        data["supervisor"].id,
        data["participant"].id,
    }
    supervisor_row = next(row for row in rows if row.user_id == data["supervisor"].id)
    participant_row = next(row for row in rows if row.user_id == data["participant"].id)
    assert "Review your remaining tasks" in supervisor_row.title_cache
    assert "Review your remaining tasks" in participant_row.title_cache


@pytest.mark.asyncio
async def test_generated_milestone_reminders_use_now_for_past_offsets(db_session):
    data = await _build_team_graph(db_session, sprint_hours=4, milestone_hours=6)
    before = datetime.now(timezone.utc).replace(tzinfo=None)
    created = await rebuild_milestone_reminders(db_session, data["milestone"].id)
    after = datetime.now(timezone.utc).replace(tzinfo=None)
    assert created == 2

    result = await db_session.execute(
        select(EventNotification)
        .where(
            EventNotification.event_type == NotificationEventType.milestone_due,
            EventNotification.event_ref_id == data["milestone"].id,
        )
        .order_by(EventNotification.user_id)
    )
    rows = result.scalars().all()
    assert len(rows) == 2
    for row in rows:
        assert before <= row.remind_at <= after
        assert row.status == NotificationStatus.pending


@pytest.mark.asyncio
async def test_disabled_reminder_settings_skip_generation(db_session):
    data = await _build_team_graph(db_session)
    settings = await get_or_create_reminder_settings(
        db_session, data["sub_team"].id
    )
    settings.sprint_reminders_enabled = False
    settings.milestone_reminders_enabled = False
    await db_session.commit()

    sprint_created = await rebuild_sprint_reminders(db_session, data["sprint"].id)
    milestone_created = await rebuild_milestone_reminders(db_session, data["milestone"].id)

    assert sprint_created == 0
    assert milestone_created == 0

    result = await db_session.execute(
        select(EventNotification).where(
            EventNotification.event_type.in_(
                [
                    NotificationEventType.sprint_end,
                    NotificationEventType.milestone_due,
                ]
            ),
            EventNotification.event_ref_id.in_(
                [data["sprint"].id, data["milestone"].id]
            ),
            EventNotification.status == NotificationStatus.pending,
        )
    )
    assert result.scalars().all() == []


@pytest.mark.asyncio
async def test_reconcile_generated_reminders_is_idempotent(db_session):
    data = await _build_team_graph(db_session, sprint_hours=48, milestone_hours=72)
    first = await reconcile_generated_reminders(db_session)
    second = await reconcile_generated_reminders(db_session)

    assert first >= 2
    assert second == 0

    result = await db_session.execute(
        select(EventNotification).where(
            EventNotification.event_type.in_(
                [
                    NotificationEventType.sprint_end,
                    NotificationEventType.milestone_due,
                ]
            ),
            EventNotification.event_ref_id.in_(
                [data["sprint"].id, data["milestone"].id]
            ),
            EventNotification.status == NotificationStatus.pending,
        )
    )
    rows = result.scalars().all()
    assert len(rows) == 4


@pytest.mark.asyncio
async def test_notification_bulk_multi_offset_still_works_for_schedule_reminders(
    async_client: AsyncClient, db_session
):
    sub_team = SubTeam(name="Schedule Team", supervisor_id=None)
    db_session.add(sub_team)
    await db_session.commit()
    await db_session.refresh(sub_team)

    user = await _create_user(
        db_session,
        email="schedule@example.com",
        username="scheduleuser",
        full_name="Schedule User",
        role=UserRole.member,
        sub_team_id=sub_team.id,
    )

    now = datetime.now(timezone.utc).replace(tzinfo=None)
    schedule = Schedule(
        title="Planning",
        start_time=now + timedelta(days=1),
        end_time=now + timedelta(days=1, hours=1),
        user_id=user.id,
    )
    db_session.add(schedule)
    await db_session.commit()
    await db_session.refresh(schedule)

    response = await async_client.post(
        "/api/auth/token",
        data={"username": user.username, "password": "password"},
    )
    token = response.json()["access_token"]

    response = await async_client.post(
        "/api/notifications/bulk",
        json={
            "event_type": "schedule",
            "event_ref_id": schedule.id,
            "offset_minutes_list": [15, 30],
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert len(response.json()) == 2

    result = await db_session.execute(
        select(EventNotification).where(
            EventNotification.user_id == user.id,
            EventNotification.event_type == NotificationEventType.schedule,
            EventNotification.event_ref_id == schedule.id,
        )
    )
    rows = result.scalars().all()
    assert len(rows) == 2


@pytest.mark.asyncio
async def test_sprint_date_change_rebuild_preserves_sent_dismissed(db_session):
    """Test that sent/dismissed reminders remain historical when sprint end_date changes."""
    data = await _build_team_graph(db_session, sprint_hours=48, milestone_hours=72)
    
    # Create initial reminders
    created = await rebuild_sprint_reminders(db_session, data["sprint"].id)
    assert created == 2
    
    # Mark one as sent, one as dismissed
    result = await db_session.execute(
        select(EventNotification).where(
            EventNotification.event_type == NotificationEventType.sprint_end,
            EventNotification.event_ref_id == data["sprint"].id,
        )
    )
    rows = result.scalars().all()
    rows[0].status = NotificationStatus.sent
    rows[1].status = NotificationStatus.dismissed
    await db_session.commit()
    
    # Change sprint end date
    data["sprint"].end_date = datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(hours=96)
    await db_session.commit()
    
    # Rebuild reminders - should delete pending only
    await rebuild_sprint_reminders(db_session, data["sprint"].id)
    
    # Verify sent/dismissed rows still exist
    result = await db_session.execute(
        select(EventNotification).where(
            EventNotification.event_type == NotificationEventType.sprint_end,
            EventNotification.event_ref_id == data["sprint"].id,
        )
    )
    rows = result.scalars().all()
    assert len(rows) == 2
    assert {row.status for row in rows} == {NotificationStatus.sent, NotificationStatus.dismissed}


@pytest.mark.asyncio
async def test_milestone_date_change_rebuild_preserves_sent_dismissed(db_session):
    """Test that sent/dismissed reminders remain historical when milestone due_date changes."""
    data = await _build_team_graph(db_session, sprint_hours=48, milestone_hours=72)
    
    # Create initial reminders
    created = await rebuild_milestone_reminders(db_session, data["milestone"].id)
    assert created == 2
    
    # Mark one as sent, one as dismissed
    result = await db_session.execute(
        select(EventNotification).where(
            EventNotification.event_type == NotificationEventType.milestone_due,
            EventNotification.event_ref_id == data["milestone"].id,
        )
    )
    rows = result.scalars().all()
    rows[0].status = NotificationStatus.sent
    rows[1].status = NotificationStatus.dismissed
    await db_session.commit()
    
    # Change milestone due date
    data["milestone"].due_date = datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(hours=120)
    await db_session.commit()
    
    # Rebuild reminders - should delete pending only
    await rebuild_milestone_reminders(db_session, data["milestone"].id)
    
    # Verify sent/dismissed rows still exist
    result = await db_session.execute(
        select(EventNotification).where(
            EventNotification.event_type == NotificationEventType.milestone_due,
            EventNotification.event_ref_id == data["milestone"].id,
        )
    )
    rows = result.scalars().all()
    assert len(rows) == 2
    assert {row.status for row in rows} == {NotificationStatus.sent, NotificationStatus.dismissed}
