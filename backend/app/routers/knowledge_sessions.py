from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.database import get_db
from app.models import (
    EventNotification,
    KnowledgeSession,
    NotificationEventType,
    NotificationStatus,
    SubTeam,
    User,
    UserRole,
)
from app.schemas import (
    KnowledgeSessionCreate,
    KnowledgeSessionOut,
    KnowledgeSessionUpdate,
)
from app.services.knowledge_sessions import (
    clear_pending_knowledge_session_notifications,
    recipient_user_ids_for_scope,
    resolve_presenter_scope,
    serialize_tags,
    sync_knowledge_session_notifications,
    visible_knowledge_session_query,
)
from app.utils.auth import get_current_user, get_sub_team, require_supervisor_or_admin

router = APIRouter(prefix="/api/knowledge-sessions", tags=["knowledge-sessions"])


def _now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _naive_utc(value: Optional[datetime]) -> Optional[datetime]:
    if isinstance(value, datetime) and value.tzinfo is not None:
        return value.astimezone(timezone.utc).replace(tzinfo=None)
    return value


async def _load_visible_session(
    db: AsyncSession,
    current_user: User,
    sub_team: Optional[SubTeam],
    session_id: int,
) -> KnowledgeSession | None:
    stmt = (
        visible_knowledge_session_query(current_user, sub_team)
        .options(selectinload(KnowledgeSession.presenter))
        .where(KnowledgeSession.id == session_id)
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def _get_scope_recipient_ids(
    db: AsyncSession, current_user: User, sub_team: Optional[SubTeam]
) -> list[int]:
    return await recipient_user_ids_for_scope(db, current_user, sub_team)


@router.get("/", response_model=List[KnowledgeSessionOut])
async def list_knowledge_sessions(
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    sub_team: Optional[SubTeam] = Depends(get_sub_team),
):
    stmt = visible_knowledge_session_query(current_user, sub_team)
    if start is not None:
        stmt = stmt.where(KnowledgeSession.start_time >= _naive_utc(start))
    if end is not None:
        stmt = stmt.where(KnowledgeSession.start_time <= _naive_utc(end))
    stmt = stmt.options(selectinload(KnowledgeSession.presenter)).order_by(
        KnowledgeSession.start_time
    )
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post("/", response_model=KnowledgeSessionOut, status_code=201)
async def create_knowledge_session(
    payload: KnowledgeSessionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_supervisor_or_admin),
    sub_team: Optional[SubTeam] = Depends(get_sub_team),
):
    if current_user.role == UserRole.supervisor and sub_team is None:
        raise HTTPException(status_code=400, detail="Sub-team context required")

    if current_user.role == UserRole.admin and sub_team is None:
        target_sub_team_id = None
    elif current_user.role == UserRole.admin:
        target_sub_team_id = sub_team.id
    else:
        target_sub_team_id = sub_team.id if sub_team else None

    presenter = await resolve_presenter_scope(
        db, current_user, sub_team, payload.presenter_id
    )

    session_obj = KnowledgeSession(
        topic=payload.topic,
        description=payload.description,
        references=payload.references,
        session_type=payload.session_type,
        start_time=payload.start_time,
        duration_minutes=payload.duration_minutes,
        tags=serialize_tags(payload.tags),
        presenter_id=presenter.id,
        sub_team_id=target_sub_team_id,
        created_by_id=current_user.id,
    )
    db.add(session_obj)
    await db.flush()

    recipient_ids = await _get_scope_recipient_ids(db, current_user, sub_team)
    await sync_knowledge_session_notifications(
        db,
        session_obj,
        recipient_ids,
        payload.offset_minutes_list,
        broadcast_creation=True,
    )

    result = await db.execute(
        select(KnowledgeSession)
        .options(selectinload(KnowledgeSession.presenter))
        .where(KnowledgeSession.id == session_obj.id)
    )
    return result.scalar_one()


@router.get("/{session_id}", response_model=KnowledgeSessionOut)
async def get_knowledge_session(
    session_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    sub_team: Optional[SubTeam] = Depends(get_sub_team),
):
    session_obj = await _load_visible_session(db, current_user, sub_team, session_id)
    if session_obj is None:
        raise HTTPException(status_code=404, detail="Knowledge session not found")
    return session_obj


@router.patch("/{session_id}", response_model=KnowledgeSessionOut)
async def update_knowledge_session(
    session_id: int,
    payload: KnowledgeSessionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_supervisor_or_admin),
    sub_team: Optional[SubTeam] = Depends(get_sub_team),
):
    session_obj = await _load_visible_session(db, current_user, sub_team, session_id)
    if session_obj is None:
        raise HTTPException(status_code=404, detail="Knowledge session not found")

    data = payload.model_dump(exclude_unset=True)
    start_time_changed = "start_time" in data
    offsets_changed = "offset_minutes_list" in data

    if "presenter_id" in data:
        presenter_id = data["presenter_id"] if data["presenter_id"] is not None else current_user.id
        presenter = await resolve_presenter_scope(db, current_user, sub_team, presenter_id)
        session_obj.presenter_id = presenter.id

    for field in ("topic", "description", "references", "session_type", "duration_minutes"):
        if field in data:
            setattr(session_obj, field, data[field])
    if start_time_changed:
        session_obj.start_time = data["start_time"]
    if "tags" in data:
        session_obj.tags = serialize_tags(data["tags"])

    await db.flush()

    if start_time_changed or offsets_changed:
        if offsets_changed:
            target_offsets = data.get("offset_minutes_list") or []
        else:
            result = await db.execute(
                select(EventNotification.offset_minutes)
                .where(
                    EventNotification.event_type == NotificationEventType.knowledge_session,
                    EventNotification.event_ref_id == session_obj.id,
                    EventNotification.status == NotificationStatus.pending,
                )
                .order_by(EventNotification.offset_minutes)
            )
            target_offsets = [offset for (offset,) in result.all()]

        recipient_ids = await _get_scope_recipient_ids(db, current_user, sub_team)
        await sync_knowledge_session_notifications(
            db,
            session_obj,
            recipient_ids,
            target_offsets,
            broadcast_creation=False,
        )

    result = await db.execute(
        select(KnowledgeSession)
        .options(selectinload(KnowledgeSession.presenter))
        .where(KnowledgeSession.id == session_obj.id)
    )
    return result.scalar_one()


@router.delete("/{session_id}", status_code=204)
async def delete_knowledge_session(
    session_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_supervisor_or_admin),
    sub_team: Optional[SubTeam] = Depends(get_sub_team),
):
    session_obj = await _load_visible_session(db, current_user, sub_team, session_id)
    if session_obj is None:
        raise HTTPException(status_code=404, detail="Knowledge session not found")

    await clear_pending_knowledge_session_notifications(db, session_obj.id)
    await db.delete(session_obj)
    await db.flush()
