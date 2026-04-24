from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.auth import get_current_user, get_sub_team
from app.database import get_db
from app.models import (
    Milestone,
    MilestoneStatus,
    Project,
    SubTeam,
    Task,
    TaskStatus,
    User,
)
from app.schemas import DashboardStats

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/", response_model=DashboardStats)
async def get_dashboard(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    sub_team: Optional[SubTeam] = Depends(get_sub_team),
):
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    next_30 = now + timedelta(days=30)

    # Apply sub-team filter to task queries
    task_query = select(Task)
    if sub_team:
        task_query = task_query.join(Project, Task.project_id == Project.id).where(
            Project.sub_team_id == sub_team.id
        )

    total = (
        await db.execute(select(func.count()).select_from(task_query.subquery()))
    ).scalar()
    todo = (
        await db.execute(
            select(func.count()).select_from(
                task_query.where(Task.status == TaskStatus.todo).subquery()
            )
        )
    ).scalar()
    in_progress = (
        await db.execute(
            select(func.count()).select_from(
                task_query.where(Task.status == TaskStatus.in_progress).subquery()
            )
        )
    ).scalar()
    done = (
        await db.execute(
            select(func.count()).select_from(
                task_query.where(Task.status == TaskStatus.done).subquery()
            )
        )
    ).scalar()
    overdue = (
        await db.execute(
            select(func.count()).select_from(
                task_query.where(
                    Task.due_date < now, Task.status != TaskStatus.done
                ).subquery()
            )
        )
    ).scalar()

    # Apply sub-team filter to user query
    user_query = select(User).where(User.is_active == True)
    if sub_team:
        user_query = user_query.where(User.sub_team_id == sub_team.id)
    team_count = (
        await db.execute(select(func.count()).select_from(user_query))
    ).scalar()

    upcoming_milestones_result = await db.execute(
        select(Milestone)
        .where(
            Milestone.due_date <= next_30, Milestone.status != MilestoneStatus.completed
        )
        .order_by(Milestone.due_date)
        .limit(5)
    )
    upcoming_milestones = upcoming_milestones_result.scalars().all()

    recent_tasks_result = await db.execute(
        select(Task)
        .options(selectinload(Task.assignee))
        .order_by(Task.updated_at.desc())
        .limit(10)
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
