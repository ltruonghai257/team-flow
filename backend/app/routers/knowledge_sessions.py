from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.models import KnowledgeSession, SubTeam, User, UserRole
from app.schemas import (
    KnowledgeSessionCreate,
    KnowledgeSessionOut,
    KnowledgeSessionUpdate,
)
from app.services.knowledge_sessions import (
    delete_pending_knowledge_session_notifications,
    deserialize_tags,
    resolve_presenter_scope,
    serialize_tags,
    sync_knowledge_session_notifications,
    visible_knowledge_session_query,
)
from app.utils.auth import get_current_user, get_sub_team, require_supervisor_or_admin

router = APIRouter(prefix="/api/knowledge-sessions", tags=["knowledge-sessions"])


def _scope_sub_team_id(current_user: User, sub_team: SubTeam | None) -> Optional[int]:
    if current_user.role == UserRole.admin:
        return sub_team.id if sub_team is not None else None
    if current_user.role == UserRole.supervisor:
        return sub_team.id if sub_team is not None else current_user.sub_team_id
    return current_user.sub_team_id


async def _visible_session_or_404(
    db: AsyncSession, current_user: User, sub_team: SubTeam | None, session_id: int
) -> KnowledgeSession:
    stmt = visible_knowledge_session_query(current_user, sub_team).where(
        KnowledgeSession.id == session_id
    )
    result = await db.execute(stmt)
    session = result.scalar_one_or_none()
    if session is None:
        raise HTTPException(status_code=404, detail="Knowledge session not found")
    return session


async def _recipient_ids(db: AsyncSession, scope_sub_team_id: Optional[int]) -> list[int]:
    if scope_sub_team_id is None:
        result = await db.execute(select(User.id))
        return [row[0] for row in result.all()]
    result = await db.execute(select(User.id).where(User.sub_team_id == scope_sub_team_id))
    return [row[0] for row in result.all()]


def _to_out(session: KnowledgeSession) -> KnowledgeSessionOut:
    return KnowledgeSessionOut(
        id=session.id,
        topic=session.topic,
        description=session.description,
        references=session.references,
        presenter_id=session.presenter_id,
        session_type=session.session_type,
        start_time=session.start_time,
        duration_minutes=session.duration_minutes,
        tags=deserialize_tags(session.tags),
        sub_team_id=session.sub_team_id,
        created_by_id=session.created_by_id,
        created_at=session.created_at,
        updated_at=session.updated_at,
        presenter=None,
    )


@router.get("/", response_model=list[KnowledgeSessionOut])
async def list_knowledge_sessions(
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    sub_team: SubTeam | None = Depends(get_sub_team),
):
    query = visible_knowledge_session_query(current_user, sub_team)
    if start is not None:
        query = query.where(KnowledgeSession.start_time >= start)
    if end is not None:
        query = query.where(KnowledgeSession.start_time <= end)
    result = await db.execute(query.order_by(KnowledgeSession.start_time))
    return [_to_out(session) for session in result.scalars().all()]


@router.post("/", response_model=KnowledgeSessionOut, status_code=status.HTTP_201_CREATED)
async def create_knowledge_session(
    payload: KnowledgeSessionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_supervisor_or_admin),
    sub_team: SubTeam | None = Depends(get_sub_team),
):
    scope_sub_team_id = _scope_sub_team_id(current_user, sub_team)
    try:
        presenter = await resolve_presenter_scope(
            db, current_user, sub_team, payload.presenter_id
        )
    except ValueError:
        raise HTTPException(status_code=404, detail="Presenter not found")
    except PermissionError:
        raise HTTPException(status_code=403, detail="Presenter out of scope")

    knowledge_session = KnowledgeSession(
        topic=payload.topic,
        description=payload.description,
        references=payload.references,
        session_type=payload.session_type,
        start_time=payload.start_time,
        duration_minutes=payload.duration_minutes,
        tags=serialize_tags(payload.tags),
        presenter_id=presenter.id,
        sub_team_id=scope_sub_team_id,
        created_by_id=current_user.id,
    )
    db.add(knowledge_session)
    await db.flush()
    await db.refresh(knowledge_session)
    await sync_knowledge_session_notifications(
        db,
        knowledge_session,
        await _recipient_ids(db, scope_sub_team_id),
        payload.offset_minutes_list,
    )
    await db.refresh(knowledge_session)
    return _to_out(knowledge_session)


@router.get("/{session_id}", response_model=KnowledgeSessionOut)
async def get_knowledge_session(
    session_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    sub_team: SubTeam | None = Depends(get_sub_team),
):
    session = await _visible_session_or_404(db, current_user, sub_team, session_id)
    return _to_out(session)


@router.patch("/{session_id}", response_model=KnowledgeSessionOut)
async def update_knowledge_session(
    session_id: int,
    payload: KnowledgeSessionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_supervisor_or_admin),
    sub_team: SubTeam | None = Depends(get_sub_team),
):
    knowledge_session = await _visible_session_or_404(db, current_user, sub_team, session_id)
    scope_sub_team_id = _scope_sub_team_id(current_user, sub_team)
    updates = payload.model_dump(exclude_unset=True)
    offset_minutes_list = updates.pop("offset_minutes_list", None)
    presenter_id = updates.pop("presenter_id", None)
    if presenter_id is not None:
        try:
            presenter = await resolve_presenter_scope(
                db, current_user, sub_team, presenter_id
            )
        except ValueError:
            raise HTTPException(status_code=404, detail="Presenter not found")
        except PermissionError:
            raise HTTPException(status_code=403, detail="Presenter out of scope")
        knowledge_session.presenter_id = presenter.id
    if "tags" in updates:
        updates["tags"] = serialize_tags(updates["tags"] or [])
    for field, value in updates.items():
        setattr(knowledge_session, field, value)
    if current_user.role == UserRole.admin and sub_team is not None:
        knowledge_session.sub_team_id = scope_sub_team_id
    elif current_user.role != UserRole.admin:
        knowledge_session.sub_team_id = scope_sub_team_id
    if offset_minutes_list is not None:
        await delete_pending_knowledge_session_notifications(db, knowledge_session.id)
        await sync_knowledge_session_notifications(
            db,
            knowledge_session,
            await _recipient_ids(db, scope_sub_team_id),
            offset_minutes_list,
        )
    await db.flush()
    await db.refresh(knowledge_session)
    return _to_out(knowledge_session)


@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_knowledge_session(
    session_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_supervisor_or_admin),
    sub_team: SubTeam | None = Depends(get_sub_team),
):
    knowledge_session = await _visible_session_or_404(db, current_user, sub_team, session_id)
    await delete_pending_knowledge_session_notifications(db, knowledge_session.id)
    await db.delete(knowledge_session)
    await db.flush()
