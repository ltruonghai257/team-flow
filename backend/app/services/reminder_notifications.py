from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Dict, Iterable

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    EventNotification,
    Milestone,
    NotificationEventType,
    NotificationStatus,
    Project,
    Sprint,
    SubTeam,
    SubTeamReminderSettings,
    Task,
    User,
)


def _now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _format_exact_date(value: datetime) -> str:
    return value.strftime("%b %d, %Y").replace(" 0", " ")


def _lead_phrase(days: int) -> str:
    suffix = "day" if days == 1 else "days"
    return f"in {days} {suffix}"


def _reminder_title(
    kind: str,
    name: str,
    lead_time_days: int,
    event_date: datetime,
    participant: bool,
) -> str:
    lead = _lead_phrase(lead_time_days)
    exact = _format_exact_date(event_date)
    if participant:
        if kind == "sprint":
            return f"Sprint {name} ends {lead} on {exact}. Review your remaining tasks."
        return f"Milestone {name} is due {lead} on {exact}. Review your remaining tasks."
    if kind == "sprint":
        return f"Sprint {name} ends {lead} on {exact} for members you supervise."
    return f"Milestone {name} is due {lead} on {exact} for members you supervise."


async def get_or_create_reminder_settings(
    session: AsyncSession, sub_team_id: int
) -> SubTeamReminderSettings:
    result = await session.execute(
        select(SubTeamReminderSettings).where(
            SubTeamReminderSettings.sub_team_id == sub_team_id
        )
    )
    settings = result.scalar_one_or_none()
    if settings is None:
        settings = SubTeamReminderSettings(sub_team_id=sub_team_id)
        session.add(settings)
        await session.flush()
        await session.refresh(settings)
    return settings


async def _recipient_roles_for_user_ids(
    session: AsyncSession, participant_user_ids: Iterable[int]
) -> Dict[int, set[str]]:
    ids = sorted({user_id for user_id in participant_user_ids if user_id is not None})
    if not ids:
        return {}

    result = await session.execute(
        select(User.id, User.sub_team_id).where(User.id.in_(ids))
    )
    users = result.all()
    roles: Dict[int, set[str]] = defaultdict(set)
    sub_team_ids = set()
    for user_id, sub_team_id in users:
        roles[user_id].add("participant")
        if sub_team_id is not None:
            sub_team_ids.add(sub_team_id)

    if sub_team_ids:
        result = await session.execute(
            select(SubTeam.id, SubTeam.supervisor_id).where(SubTeam.id.in_(sub_team_ids))
        )
        supervisors = {sub_team_id: supervisor_id for sub_team_id, supervisor_id in result.all()}
        for user_id, sub_team_id in users:
            supervisor_id = supervisors.get(sub_team_id)
            if supervisor_id is not None:
                roles[supervisor_id].add("supervisor")
    return roles


async def _insert_generated_rows(
    session: AsyncSession,
    *,
    event_type: NotificationEventType,
    event_ref_id: int,
    kind: str,
    name: str,
    event_date: datetime,
    lead_time_days: int,
    recipient_roles: Dict[int, set[str]],
) -> int:
    if not recipient_roles:
        return 0

    remind_at = event_date - timedelta(days=lead_time_days)
    now = _now()
    if remind_at <= now:
        remind_at = now

    created = 0
    for user_id, roles in recipient_roles.items():
        existing = await session.execute(
            select(EventNotification.id).where(
                EventNotification.user_id == user_id,
                EventNotification.event_type == event_type,
                EventNotification.event_ref_id == event_ref_id,
            )
        )
        if existing.first() is not None:
            continue
        title = _reminder_title(kind, name, lead_time_days, event_date, "participant" in roles)
        notification = EventNotification(
            user_id=user_id,
            event_type=event_type,
            event_ref_id=event_ref_id,
            title_cache=title,
            start_at_cache=event_date,
            remind_at=remind_at,
            offset_minutes=lead_time_days * 24 * 60,
            status=NotificationStatus.pending,
        )
        session.add(notification)
        created += 1
    await session.flush()
    return created


async def rebuild_sprint_reminders(session: AsyncSession, sprint_id: int) -> int:
    result = await session.execute(select(Sprint).where(Sprint.id == sprint_id))
    sprint = result.scalar_one_or_none()
    if sprint is None or sprint.end_date is None:
        await session.execute(
            delete(EventNotification).where(
                EventNotification.event_type == NotificationEventType.sprint_end,
                EventNotification.event_ref_id == sprint_id,
                EventNotification.status == NotificationStatus.pending,
            )
        )
        await session.flush()
        return 0

    result = await session.execute(
        select(Task.assignee_id)
        .where(Task.sprint_id == sprint_id, Task.assignee_id.is_not(None))
        .distinct()
    )
    participant_ids = [row[0] for row in result.all()]
    recipient_roles = await _recipient_roles_for_user_ids(session, participant_ids)

    milestone = await session.get(Milestone, sprint.milestone_id)
    if milestone is None or milestone.project_id is None:
        return 0
    project = await session.get(Project, milestone.project_id)
    if project is None or project.sub_team_id is None:
        return 0
    settings = await get_or_create_reminder_settings(session, project.sub_team_id)
    if not settings.sprint_reminders_enabled:
        return 0
    if recipient_roles:
        return await _insert_generated_rows(
            session,
            event_type=NotificationEventType.sprint_end,
            event_ref_id=sprint_id,
            kind="sprint",
            name=sprint.name,
            event_date=sprint.end_date,
            lead_time_days=settings.lead_time_days,
            recipient_roles=recipient_roles,
        )
    return 0


async def rebuild_milestone_reminders(session: AsyncSession, milestone_id: int) -> int:
    result = await session.execute(select(Milestone).where(Milestone.id == milestone_id))
    milestone = result.scalar_one_or_none()
    if milestone is None:
        await session.execute(
            delete(EventNotification).where(
                EventNotification.event_type == NotificationEventType.milestone_due,
                EventNotification.event_ref_id == milestone_id,
                EventNotification.status == NotificationStatus.pending,
            )
        )
        await session.flush()
        return 0

    result = await session.execute(
        select(Task.assignee_id)
        .where(Task.project_id == milestone.project_id, Task.assignee_id.is_not(None))
        .distinct()
    )
    participant_ids = [row[0] for row in result.all()]
    recipient_roles = await _recipient_roles_for_user_ids(session, participant_ids)

    project = await session.get(Project, milestone.project_id)
    if project is None or project.sub_team_id is None:
        return 0
    settings = await get_or_create_reminder_settings(session, project.sub_team_id)
    if not settings.milestone_reminders_enabled:
        return 0

    if not recipient_roles:
        return 0

    return await _insert_generated_rows(
        session,
        event_type=NotificationEventType.milestone_due,
        event_ref_id=milestone_id,
        kind="milestone",
        name=milestone.title,
        event_date=milestone.due_date,
        lead_time_days=settings.lead_time_days,
        recipient_roles=recipient_roles,
    )


async def reconcile_generated_reminders(session: AsyncSession) -> int:
    now = _now()
    created = 0
    sprint_result = await session.execute(
        select(Sprint.id).where(Sprint.end_date.is_not(None), Sprint.end_date >= now)
    )
    for sprint_id in sprint_result.scalars().all():
        created += await rebuild_sprint_reminders(session, sprint_id)

    milestone_result = await session.execute(
        select(Milestone.id).where(Milestone.due_date >= now)
    )
    for milestone_id in milestone_result.scalars().all():
        created += await rebuild_milestone_reminders(session, milestone_id)

    return created
