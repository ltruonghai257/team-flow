from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Iterable, Sequence

from fastapi import HTTPException
from sqlalchemy import delete, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    EventNotification,
    KnowledgeSession,
    NotificationEventType,
    NotificationStatus,
    SubTeam,
    User,
    UserRole,
)


def _now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _normalize_tags(tags: Sequence[str] | None) -> list[str]:
    normalized: list[str] = []
    seen: set[str] = set()
    if not tags:
        return normalized
    for tag in tags:
        value = str(tag).strip()
        if not value:
            continue
        key = value.lower()
        if key in seen:
            continue
        seen.add(key)
        normalized.append(value)
    return normalized


def serialize_tags(tags: list[str] | None) -> str | None:
    normalized = _normalize_tags(tags)
    return ",".join(normalized) if normalized else None


def deserialize_tags(tags: str | None) -> list[str]:
    if not tags:
        return []
    return _normalize_tags(tags.split(","))


def visible_knowledge_session_query(
    current_user: User, sub_team: SubTeam | None
):
    stmt = select(KnowledgeSession)
    if current_user.role == UserRole.admin and sub_team is None:
        return stmt

    target_sub_team_id = sub_team.id if sub_team else current_user.sub_team_id
    return stmt.where(
        or_(
            KnowledgeSession.sub_team_id.is_(None),
            KnowledgeSession.sub_team_id == target_sub_team_id,
        )
    )


async def resolve_presenter_scope(
    session: AsyncSession,
    current_user: User,
    sub_team: SubTeam | None,
    presenter_id: int | None,
) -> User:
    target_presenter_id = presenter_id if presenter_id is not None else current_user.id
    result = await session.execute(
        select(User).where(
            User.id == target_presenter_id,
            User.is_active.is_(True),
        )
    )
    presenter = result.scalar_one_or_none()
    if presenter is None:
        raise HTTPException(status_code=404, detail="Presenter not found")

    if current_user.role == UserRole.admin and sub_team is None:
        return presenter

    target_sub_team_id = sub_team.id if sub_team else current_user.sub_team_id
    if target_sub_team_id is None or presenter.sub_team_id != target_sub_team_id:
        raise HTTPException(
            status_code=403,
            detail="Presenter must belong to the session scope",
        )
    return presenter


async def recipient_user_ids_for_scope(
    session: AsyncSession, current_user: User, sub_team: SubTeam | None
) -> list[int]:
    stmt = select(User.id).where(User.is_active.is_(True))
    if current_user.role == UserRole.admin and sub_team is None:
        result = await session.execute(stmt)
        return [user_id for (user_id,) in result.all()]

    target_sub_team_id = sub_team.id if sub_team else current_user.sub_team_id
    if target_sub_team_id is None:
        return []
    result = await session.execute(stmt.where(User.sub_team_id == target_sub_team_id))
    return [user_id for (user_id,) in result.all()]


async def clear_pending_knowledge_session_notifications(
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


async def sync_knowledge_session_notifications(
    session: AsyncSession,
    knowledge_session: KnowledgeSession,
    recipient_user_ids: Iterable[int],
    offset_minutes_list: Sequence[int],
    *,
    broadcast_creation: bool = True,
) -> int:
    now = _now()
    recipient_ids = [user_id for user_id in recipient_user_ids if user_id is not None]
    created = 0

    if broadcast_creation:
        for user_id in recipient_ids:
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
            created += 1

    await clear_pending_knowledge_session_notifications(session, knowledge_session.id)

    for user_id in recipient_ids:
        for offset in offset_minutes_list:
            remind_at = knowledge_session.start_time - timedelta(minutes=offset)
            session.add(
                EventNotification(
                    user_id=user_id,
                    event_type=NotificationEventType.knowledge_session,
                    event_ref_id=knowledge_session.id,
                    title_cache=knowledge_session.topic,
                    start_at_cache=knowledge_session.start_time,
                    remind_at=remind_at if remind_at > now else now,
                    offset_minutes=offset,
                    status=(
                        NotificationStatus.sent
                        if remind_at <= now
                        else NotificationStatus.pending
                    ),
                )
            )
            created += 1

    await session.flush()
    return created

