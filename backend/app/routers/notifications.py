from datetime import datetime, timedelta
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user
from app.database import get_db
from app.models import (
    EventNotification,
    NotificationEventType,
    NotificationStatus,
    Schedule,
    Task,
    User,
)
from app.schemas import (
    NotificationBulkCreate,
    NotificationCreate,
    NotificationOut,
)

router = APIRouter(prefix="/api/notifications", tags=["notifications"])


async def _resolve_event(
    db: AsyncSession,
    user_id: int,
    event_type: NotificationEventType,
    event_ref_id: int,
) -> tuple[str, datetime]:
    """Return (title, start_at) for a schedule or task event owned/visible by user."""
    if event_type == NotificationEventType.schedule:
        result = await db.execute(
            select(Schedule).where(Schedule.id == event_ref_id, Schedule.user_id == user_id)
        )
        obj = result.scalar_one_or_none()
        if not obj:
            raise HTTPException(status_code=404, detail="Schedule event not found")
        return obj.title, obj.start_time
    else:
        result = await db.execute(select(Task).where(Task.id == event_ref_id))
        obj = result.scalar_one_or_none()
        if not obj or not obj.due_date:
            raise HTTPException(status_code=404, detail="Task with due_date not found")
        return obj.title, obj.due_date


@router.post("", response_model=NotificationOut, status_code=201)
async def create_notification(
    payload: NotificationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    title, start_at = await _resolve_event(
        db, current_user.id, payload.event_type, payload.event_ref_id
    )
    remind_at = start_at - timedelta(minutes=payload.offset_minutes)
    status = (
        NotificationStatus.sent if remind_at <= datetime.utcnow() else NotificationStatus.pending
    )
    n = EventNotification(
        user_id=current_user.id,
        event_type=payload.event_type,
        event_ref_id=payload.event_ref_id,
        title_cache=title,
        start_at_cache=start_at,
        remind_at=remind_at,
        offset_minutes=payload.offset_minutes,
        status=status,
    )
    db.add(n)
    await db.flush()
    await db.refresh(n)
    return n


@router.post("/bulk", response_model=List[NotificationOut])
async def bulk_set_notifications(
    payload: NotificationBulkCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Replace all reminders for (event_type, event_ref_id) owned by user with the given offsets."""
    title, start_at = await _resolve_event(
        db, current_user.id, payload.event_type, payload.event_ref_id
    )
    # Delete existing reminders for this event
    result = await db.execute(
        select(EventNotification).where(
            EventNotification.user_id == current_user.id,
            EventNotification.event_type == payload.event_type,
            EventNotification.event_ref_id == payload.event_ref_id,
        )
    )
    for existing in result.scalars().all():
        await db.delete(existing)
    await db.flush()

    created: List[EventNotification] = []
    now = datetime.utcnow()
    for offset in payload.offset_minutes_list:
        remind_at = start_at - timedelta(minutes=offset)
        n = EventNotification(
            user_id=current_user.id,
            event_type=payload.event_type,
            event_ref_id=payload.event_ref_id,
            title_cache=title,
            start_at_cache=start_at,
            remind_at=remind_at,
            offset_minutes=offset,
            status=NotificationStatus.sent if remind_at <= now else NotificationStatus.pending,
        )
        db.add(n)
        created.append(n)
    await db.flush()
    for n in created:
        await db.refresh(n)
    return created


@router.get("/pending", response_model=List[NotificationOut])
async def list_pending(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return sent-but-not-dismissed notifications for the current user (bell + toasts)."""
    result = await db.execute(
        select(EventNotification)
        .where(
            EventNotification.user_id == current_user.id,
            EventNotification.status == NotificationStatus.sent,
        )
        .order_by(EventNotification.remind_at.desc())
    )
    return result.scalars().all()


@router.get("/by-event", response_model=List[NotificationOut])
async def list_by_event(
    event_type: NotificationEventType = Query(...),
    event_ref_id: int = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(EventNotification)
        .where(
            EventNotification.user_id == current_user.id,
            EventNotification.event_type == event_type,
            EventNotification.event_ref_id == event_ref_id,
        )
        .order_by(EventNotification.offset_minutes)
    )
    return result.scalars().all()


async def _get_owned(db: AsyncSession, notification_id: int, user_id: int) -> EventNotification:
    result = await db.execute(
        select(EventNotification).where(EventNotification.id == notification_id)
    )
    n = result.scalar_one_or_none()
    if not n:
        raise HTTPException(status_code=404, detail="Notification not found")
    if n.user_id != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    return n


@router.patch("/{notification_id}/dismiss", response_model=NotificationOut)
async def dismiss_notification(
    notification_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    n = await _get_owned(db, notification_id, current_user.id)
    n.status = NotificationStatus.dismissed
    await db.flush()
    await db.refresh(n)
    return n


@router.post("/dismiss-all", status_code=204)
async def dismiss_all(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(EventNotification).where(
            EventNotification.user_id == current_user.id,
            EventNotification.status == NotificationStatus.sent,
        )
    )
    for n in result.scalars().all():
        n.status = NotificationStatus.dismissed
    await db.flush()


@router.delete("/{notification_id}", status_code=204)
async def delete_notification(
    notification_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    n = await _get_owned(db, notification_id, current_user.id)
    await db.delete(n)
    await db.flush()
