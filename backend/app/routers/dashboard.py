from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.auth import get_current_user
from app.database import get_db
from app.models import Milestone, MilestoneStatus, Task, TaskStatus, User
from app.schemas import DashboardStats

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/", response_model=DashboardStats)
async def get_dashboard(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    next_30 = now + timedelta(days=30)

    total = (await db.execute(select(func.count()).select_from(Task))).scalar()
    todo = (await db.execute(select(func.count()).select_from(Task).where(Task.status == TaskStatus.todo))).scalar()
    in_progress = (await db.execute(select(func.count()).select_from(Task).where(Task.status == TaskStatus.in_progress))).scalar()
    done = (await db.execute(select(func.count()).select_from(Task).where(Task.status == TaskStatus.done))).scalar()
    overdue = (
        await db.execute(
            select(func.count()).select_from(Task).where(
                Task.due_date < now, Task.status != TaskStatus.done
            )
        )
    ).scalar()

    team_count = (await db.execute(select(func.count()).select_from(User).where(User.is_active == True))).scalar()

    upcoming_milestones_result = await db.execute(
        select(Milestone)
        .where(Milestone.due_date <= next_30, Milestone.status != MilestoneStatus.completed)
        .order_by(Milestone.due_date)
        .limit(5)
    )
    upcoming_milestones = upcoming_milestones_result.scalars().all()

    recent_tasks_result = await db.execute(
        select(Task).options(selectinload(Task.assignee)).order_by(Task.updated_at.desc()).limit(10)
    )
    recent_tasks = recent_tasks_result.scalars().all()

    return DashboardStats(
        total_tasks=total,
        todo_tasks=todo,
        in_progress_tasks=in_progress,
        done_tasks=done,
        overdue_tasks=overdue,
        total_team_members=team_count,
        upcoming_milestones=upcoming_milestones,
        recent_tasks=recent_tasks,
    )
