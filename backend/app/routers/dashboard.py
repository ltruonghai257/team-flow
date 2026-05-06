from datetime import date, datetime, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.utils.auth import get_current_user, get_sub_team
from app.db.database import get_db
from app.models import CustomStatus, Project, SubTeam, Task, TaskStatus, User
from app.models.updates import StandupPost
from app.schemas.dashboard import (
    DashboardActivityItem,
    DashboardKpiSummary,
    DashboardPayload,
    DashboardTaskItem,
    DashboardTeamHealthMember,
)
from app.services.kpi import compute_kpi_overview
from app.services.visibility import is_leader, is_manager

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/", response_model=DashboardPayload, response_model_exclude_none=True)
async def get_dashboard(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    sub_team: Optional[SubTeam] = Depends(get_sub_team),
) -> DashboardPayload:
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    due_soon_cutoff = now + timedelta(hours=48)

    # Section 1 — my_tasks (all roles, D-02 to D-05)
    task_result = await db.execute(
        select(Task)
        .outerjoin(CustomStatus, Task.custom_status_id == CustomStatus.id)
        .where(
            Task.assignee_id == current_user.id,
            Task.status != TaskStatus.done,
            (Task.custom_status_id.is_(None)) | (CustomStatus.is_done.is_(False)),
        )
        .options(selectinload(Task.custom_status), selectinload(Task.project))
    )
    tasks = task_result.scalars().all()

    task_items = []
    for t in tasks:
        is_overdue = t.due_date is not None and t.due_date < now.date()
        is_due_soon = (
            not is_overdue
            and t.due_date is not None
            and now.date() <= t.due_date <= due_soon_cutoff.date()
        )
        project_name = t.project.name if t.project else None
        task_items.append(
            DashboardTaskItem(
                id=t.id,
                title=t.title,
                project_name=project_name,
                status=t.status,
                priority=t.priority,
                due_date=t.due_date,
                is_overdue=is_overdue,
                is_due_soon=is_due_soon,
            )
        )

    # Sort: overdue first (due_date ASC), then upcoming (due_date ASC), then no due_date
    overdue = sorted(
        [x for x in task_items if x.is_overdue], key=lambda x: x.due_date or date.min
    )
    upcoming = sorted(
        [x for x in task_items if not x.is_overdue and x.due_date is not None],
        key=lambda x: x.due_date,
    )
    no_date = [x for x in task_items if x.due_date is None]
    my_tasks = (overdue + upcoming + no_date)[:20]

    # Section 2 — team_health and kpi_summary (supervisor/assistant_manager/manager only)
    team_health = None
    kpi_summary = None

    if is_leader(current_user) or is_manager(current_user):
        kpi_result = await compute_kpi_overview(db, sub_team)

        team_health = [
            DashboardTeamHealthMember(
                user_id=m.user_id,
                full_name=m.full_name,
                avatar_url=m.avatar_url,
                status=(
                    "red"
                    if m.active_tasks > 10
                    else ("yellow" if m.active_tasks > 7 else "green")
                ),
                active_tasks=m.active_tasks,
                completed_30d=m.completed_30d,
                overdue_tasks=m.overdue_tasks,
            )
            for m in kpi_result.per_member
        ]

        kpi_summary = DashboardKpiSummary(
            avg_score=kpi_result.avg_score,
            completion_rate=kpi_result.completion_rate,
            needs_attention_count=kpi_result.needs_attention_count,
        )

    # Section 3 — recent_activity (all roles, D-13 to D-15)
    activity_query = select(StandupPost).order_by(StandupPost.id.desc()).limit(5)
    if sub_team is not None:
        activity_query = activity_query.where(StandupPost.sub_team_id == sub_team.id)

    activity_result = await db.execute(activity_query)
    posts = activity_result.scalars().all()

    # Load author relationship for each post
    for post in posts:
        await db.refresh(post, attribute_names=["author"])

    recent_activity = [
        DashboardActivityItem(
            post_id=post.id,
            author_id=post.author_id,
            author_name=post.author.full_name if post.author else "Unknown",
            created_at=post.created_at,
            field_values=post.field_values or {},
        )
        for post in posts
    ]

    return DashboardPayload(
        my_tasks=my_tasks,
        team_health=team_health,
        kpi_summary=kpi_summary,
        recent_activity=recent_activity,
    )
