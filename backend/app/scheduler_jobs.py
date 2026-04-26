"""Background jobs for event notifications.

Runs periodically and transitions EventNotification rows from `pending` -> `sent`
once their `remind_at` time has passed.
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import select, update

from app.database import AsyncSessionLocal
from app.models import EventNotification, NotificationStatus
from app.services.reminder_notifications import reconcile_generated_reminders

logger = logging.getLogger(__name__)

_scheduler: AsyncIOScheduler | None = None


async def process_due_notifications() -> int:
    """Flip pending notifications whose remind_at <= now to sent. Returns count."""
    async with AsyncSessionLocal() as session:
        async with session.begin():
            result = await session.execute(
                select(EventNotification).where(
                    EventNotification.status == NotificationStatus.pending,
                    EventNotification.remind_at <= datetime.now(timezone.utc).replace(tzinfo=None),
                )
            )
            due = result.scalars().all()
            for n in due:
                n.status = NotificationStatus.sent
        count = len(due)
        if count:
            logger.info("Flipped %d notifications pending -> sent", count)
        return count


async def reconcile_generated_reminders_job() -> int:
    async with AsyncSessionLocal() as session:
        async with session.begin():
            count = await reconcile_generated_reminders(session)
        if count:
            logger.info("Reconciled %d generated reminders", count)
        return count


def start_scheduler() -> AsyncIOScheduler:
    global _scheduler
    if _scheduler is not None:
        return _scheduler
    sched = AsyncIOScheduler()
    sched.add_job(
        process_due_notifications,
        trigger="interval",
        seconds=60,
        id="process_due_notifications",
        replace_existing=True,
    )
    sched.add_job(
        reconcile_generated_reminders_job,
        trigger="interval",
        minutes=5,
        id="reconcile_generated_reminders",
        replace_existing=True,
    )
    sched.start()
    _scheduler = sched
    return sched


def shutdown_scheduler() -> None:
    global _scheduler
    if _scheduler is not None:
        _scheduler.shutdown(wait=False)
        _scheduler = None
