from datetime import datetime, timedelta, timezone
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select, extract, case, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.auth import require_supervisor
from app.database import get_db
from app.models import User, Task, TaskStatus, ChatMessage
from app.schemas import (
    PerformanceDashboard,
    TeamMemberPerformance,
    UserPerformanceDetail,
    TrendDataPoint,
    TaskOut
)

router = APIRouter(prefix="/api/performance", tags=["performance"])

@router.get("/team", response_model=PerformanceDashboard)
async def get_team_performance(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_supervisor),
):
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    thirty_days_ago = now - timedelta(days=30)
    forty_eight_hours_ahead = now + timedelta(hours=48)

    # 1. Main Metrics Query (Aggregate Filter Pattern)
    metrics_stmt = (
        select(
            User.id,
            User.full_name,
            User.avatar_url,
            # Active Tasks: all except 'done'
            func.count(Task.id).filter(Task.status != TaskStatus.done).label("active_tasks"),
            # Completed (30d)
            func.count(Task.id).filter(
                Task.status == TaskStatus.done,
                Task.completed_at >= thirty_days_ago
            ).label("completed_30d"),
            # Cycle Time (Hours)
            func.avg(
                extract("epoch", Task.completed_at - Task.created_at) / 3600
            ).filter(Task.status == TaskStatus.done).label("avg_cycle_time"),
            # On-Time Count
            func.count(Task.id).filter(
                Task.status == TaskStatus.done,
                Task.completed_at <= Task.due_date
            ).label("on_time_count"),
            # Total with Due Date (Completed)
            func.count(Task.id).filter(
                Task.status == TaskStatus.done,
                Task.due_date.is_not(None)
            ).label("total_completed_with_due_date"),
            # Overdue Count (Active tasks past due date)
            func.count(Task.id).filter(
                Task.status != TaskStatus.done,
                Task.due_date < now
            ).label("overdue_count"),
            # Due Soon (Active tasks due within 48h)
            func.count(Task.id).filter(
                Task.status != TaskStatus.done,
                Task.due_date >= now,
                Task.due_date <= forty_eight_hours_ahead
            ).label("due_soon_count")
        )
        .join(Task, User.id == Task.assignee_id, isouter=True)
        .group_by(User.id)
    )

    metrics_result = await db.execute(metrics_stmt)
    metrics_rows = metrics_result.all()

    # 2. Collaboration Score (Message count 30d)
    collab_stmt = (
        select(User.id, func.count(ChatMessage.id))
        .join(ChatMessage, User.id == ChatMessage.sender_id)
        .where(ChatMessage.created_at >= thirty_days_ago)
        .group_by(User.id)
    )
    collab_result = await db.execute(collab_stmt)
    collab_map = {row[0]: row[1] for row in collab_result.all()}

    team_metrics = []
    total_active = 0
    total_on_time = 0
    total_with_due = 0

    for row in metrics_rows:
        user_id = row.id
        active_tasks = row.active_tasks
        overdue_count = row.overdue_count
        due_soon_count = row.due_soon_count
        
        # Calculate On-Time Rate
        on_time_count = row.on_time_count
        with_due = row.total_completed_with_due_date
        on_time_rate = (on_time_count / with_due * 100) if with_due > 0 else 100.0

        # Collaboration Score
        collab_score = collab_map.get(user_id, 0)

        # Status Logic
        if overdue_count > 0 or active_tasks > 10:
            status = "red"
        elif due_soon_count > 0 or active_tasks > 7:
            status = "yellow"
        else:
            status = "green"

        team_metrics.append(TeamMemberPerformance(
            user_id=user_id,
            full_name=row.full_name,
            avatar_url=row.avatar_url,
            active_tasks=active_tasks,
            completed_30d=row.completed_30d,
            avg_cycle_time=round(row.avg_cycle_time, 1) if row.avg_cycle_time else None,
            on_time_rate=round(on_time_rate, 1),
            collaboration_score=collab_score,
            status=status
        ))

        total_active += active_tasks
        total_on_time += on_time_count
        total_with_due += with_due

    overall_on_time = (total_on_time / total_with_due * 100) if total_with_due > 0 else 100.0

    return PerformanceDashboard(
        team_metrics=team_metrics,
        overall_on_time_rate=round(overall_on_time, 1),
        total_active_tasks=total_active
    )

@router.get("/user/{user_id}", response_model=UserPerformanceDetail)
async def get_user_performance_detail(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_supervisor),
):
    user_result = await db.execute(select(User).where(User.id == user_id))
    user = user_result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    now = datetime.now(timezone.utc).replace(tzinfo=None)
    thirty_days_ago = now - timedelta(days=30)
    eight_weeks_ago = (now - timedelta(weeks=8)).date()

    # 1. Fetch Metrics (Similar to team query but for single user)
    # We can reuse the logic or run a simpler version
    metrics_stmt = (
        select(
            func.count(Task.id).filter(Task.status != TaskStatus.done).label("active_tasks"),
            func.count(Task.id).filter(
                Task.status == TaskStatus.done,
                Task.completed_at >= thirty_days_ago
            ).label("completed_30d"),
            func.avg(
                extract("epoch", Task.completed_at - Task.created_at) / 3600
            ).filter(Task.status == TaskStatus.done).label("avg_cycle_time"),
            func.count(Task.id).filter(
                Task.status == TaskStatus.done,
                Task.completed_at <= Task.due_date
            ).label("on_time_count"),
            func.count(Task.id).filter(
                Task.status == TaskStatus.done,
                Task.due_date.is_not(None)
            ).label("total_completed_with_due_date"),
            func.count(Task.id).filter(
                Task.status != TaskStatus.done,
                Task.due_date < now
            ).label("overdue_count"),
            func.count(Task.id).filter(
                Task.status != TaskStatus.done,
                Task.due_date >= now,
                Task.due_date <= now + timedelta(hours=48)
            ).label("due_soon_count")
        )
        .where(Task.assignee_id == user_id)
    )
    metrics_result = await db.execute(metrics_stmt)
    m = metrics_result.one()

    # 2. Collaboration Score
    collab_stmt = (
        select(func.count(ChatMessage.id))
        .where(ChatMessage.sender_id == user_id, ChatMessage.created_at >= thirty_days_ago)
    )
    collab_score = (await db.execute(collab_stmt)).scalar() or 0

    # 3. Trend Data (8 weeks)
    # Group by date of completed_at
    trend_stmt = (
        select(
            func.date(Task.completed_at).label("date"),
            func.count(Task.id).label("count")
        )
        .where(
            Task.assignee_id == user_id,
            Task.status == TaskStatus.done,
            Task.completed_at >= eight_weeks_ago
        )
        .group_by(func.date(Task.completed_at))
        .order_by(func.date(Task.completed_at))
    )
    trend_result = await db.execute(trend_stmt)
    trend_data = [TrendDataPoint(date=str(row[0]), completed_count=row[1]) for row in trend_result.all()]

    # 4. Recent Completed Tasks
    recent_tasks_stmt = (
        select(Task)
        .where(Task.assignee_id == user_id, Task.status == TaskStatus.done)
        .order_by(desc(Task.completed_at))
        .limit(5)
    )
    recent_tasks_result = await db.execute(recent_tasks_stmt)
    recent_tasks = recent_tasks_result.scalars().all()

    # Status Logic
    active_tasks = m.active_tasks
    if m.overdue_count > 0 or active_tasks > 10:
        status = "red"
    elif m.due_soon_count > 0 or active_tasks > 7:
        status = "yellow"
    else:
        status = "green"

    on_time_rate = (m.on_time_count / m.total_completed_with_due_date * 100) if m.total_completed_with_due_date > 0 else 100.0

    performance = TeamMemberPerformance(
        user_id=user.id,
        full_name=user.full_name,
        avatar_url=user.avatar_url,
        active_tasks=active_tasks,
        completed_30d=m.completed_30d,
        avg_cycle_time=round(m.avg_cycle_time, 1) if m.avg_cycle_time else None,
        on_time_rate=round(on_time_rate, 1),
        collaboration_score=collab_score,
        status=status
    )

    return UserPerformanceDetail(
        user_id=user.id,
        full_name=user.full_name,
        metrics=performance,
        trend_data=trend_data,
        recent_completed_tasks=recent_tasks
    )
