from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Iterable, Optional

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    EventNotification,
    KnowledgeSession,
    NotificationEventType,
    NotificationStatus,
    SubTeam,
    User,
)
from app.services.visibility import is_manager, is_leader


def _now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def serialize_tags(tags: list[str]) -> str | None:
    normalized = deserialize_tags(",".join(tags) if tags else None)
    return ",".join(normalized) if normalized else None


def deserialize_tags(tags: str | None) -> list[str]:
    if not tags:
        return []
    result: list[str] = []
    seen: set[str] = set()
    for tag in tags.split(","):
        cleaned = tag.strip()
        if not cleaned:
            continue
        key = cleaned.lower()
        if key in seen:
            continue
        seen.add(key)
        result.append(cleaned)
    return result


def _scope_sub_team_id(current_user: User, sub_team: SubTeam | None) -> Optional[int]:
    if is_manager(current_user):
        return sub_team.id if sub_team is not None else None
    if is_leader(current_user):
        return sub_team.id if sub_team is not None else current_user.sub_team_id
    return current_user.sub_team_id


def visible_knowledge_session_query(
    current_user: User, sub_team: SubTeam | None
):
    stmt = select(KnowledgeSession)
    if is_manager(current_user) and sub_team is None:
        return stmt
    if is_manager(current_user) and sub_team is not None:
        return stmt.where(
            (KnowledgeSession.sub_team_id.is_(None))
            | (KnowledgeSession.sub_team_id == sub_team.id)
        )
    if is_leader(current_user):
        scope_sub_team_id = sub_team.id if sub_team is not None else current_user.sub_team_id
        return stmt.where(
            (KnowledgeSession.sub_team_id.is_(None))
            | (KnowledgeSession.sub_team_id == scope_sub_team_id)
        )
    return stmt.where(
        (KnowledgeSession.sub_team_id.is_(None))
        | (KnowledgeSession.sub_team_id == current_user.sub_team_id)
    )


async def resolve_presenter_scope(
    session: AsyncSession,
    current_user: User,
    sub_team: SubTeam | None,
    presenter_id: int | None,
) -> User:
    if presenter_id is None:
        return current_user
    result = await session.execute(select(User).where(User.id == presenter_id))
    presenter = result.scalar_one_or_none()
    if presenter is None:
        raise ValueError("presenter_not_found")
    if is_manager(current_user) and sub_team is None:
        return presenter
    scope_sub_team_id = _scope_sub_team_id(current_user, sub_team)
    if presenter.sub_team_id != scope_sub_team_id:
        raise PermissionError("presenter_out_of_scope")
    return presenter


async def sync_knowledge_session_notifications(
    session: AsyncSession,
    knowledge_session: KnowledgeSession,
    recipient_user_ids: Iterable[int],
    offset_minutes_list: list[int],
) -> None:
    now = _now()
    recipient_ids = sorted({user_id for user_id in recipient_user_ids if user_id is not None})
    if not recipient_ids:
        return

    for user_id in recipient_ids:
        existing = await session.execute(
            select(EventNotification).where(
                EventNotification.user_id == user_id,
                EventNotification.event_type == NotificationEventType.knowledge_session,
                EventNotification.event_ref_id == knowledge_session.id,
            )
        )
        if existing.scalar_one_or_none() is None:
            session.add(
                EventNotification(
                    user_id=user_id,
                    event_type=NotificationEventType.knowledge_session,
                    event_ref_id=knowledge_session.id,
                    title_cache=knowledge_session.topic,
                    start_at_cache=knowledge_session.start_time,
                    remind_at=now,
                    offset_minutes=0,
                    status=NotificationStatus.sent,
                )
            )

    await session.execute(
        delete(EventNotification).where(
            EventNotification.event_type == NotificationEventType.knowledge_session,
            EventNotification.event_ref_id == knowledge_session.id,
            EventNotification.user_id.in_(recipient_ids),
            EventNotification.status == NotificationStatus.pending,
            EventNotification.offset_minutes != 0,
        )
    )

    for user_id in recipient_ids:
        for offset in offset_minutes_list:
            remind_at = knowledge_session.start_time - timedelta(minutes=offset)
            status = (
                NotificationStatus.sent
                if remind_at <= now
                else NotificationStatus.pending
            )
            existing = await session.execute(
                select(EventNotification.id).where(
                    EventNotification.user_id == user_id,
                    EventNotification.event_type == NotificationEventType.knowledge_session,
                    EventNotification.event_ref_id == knowledge_session.id,
                    EventNotification.offset_minutes == offset,
                )
            )
            if existing.first() is not None:
                continue
            session.add(
                EventNotification(
                    user_id=user_id,
                    event_type=NotificationEventType.knowledge_session,
                    event_ref_id=knowledge_session.id,
                    title_cache=knowledge_session.topic,
                    start_at_cache=knowledge_session.start_time,
                    remind_at=remind_at,
                    offset_minutes=offset,
                    status=status,
                )
            )

    await session.flush()


async def delete_pending_knowledge_session_notifications(
    session: AsyncSession, knowledge_session_id: int
) -> None:
    await session.execute(
        delete(EventNotification).where(
            EventNotification.event_type == NotificationEventType.knowledge_session,
            EventNotification.event_ref_id == knowledge_session_id,
            EventNotification.status == NotificationStatus.pending,
        )
    )
    await session.flush()
