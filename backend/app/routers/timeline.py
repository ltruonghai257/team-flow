from typing import List, Optional

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.utils.auth import get_current_user, get_sub_team
from app.db.database import get_db
from app.models import Milestone, Project, SubTeam, Task, User, UserRole
from app.schemas import TimelineProjectOut, TimelineTaskOut, TimelineMilestoneOut

router = APIRouter(prefix="/api/timeline", tags=["timeline"])


@router.get("/", response_model=List[TimelineProjectOut])
async def get_timeline(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    sub_team: Optional[SubTeam] = Depends(get_sub_team),
):
    # Fetch projects with eager-loaded milestones -> tasks -> assignee
    stmt = select(Project).options(
        selectinload(Project.milestones)
        .selectinload(Milestone.tasks)
        .selectinload(Task.assignee)
    )

    # Apply sub-team filter (admin may have None = all teams)
    if sub_team:
        stmt = stmt.where(Project.sub_team_id == sub_team.id)

    # Apply role-specific filtering per D-22/D-23/D-24
    if current_user.role == UserRole.member:
        # Members see only projects where they have assigned tasks
        stmt = (
            stmt.join(Task, Project.id == Task.project_id)
            .where(Task.assignee_id == current_user.id)
            .distinct()
        )
    # Supervisors and admins see all projects in their scoped view (already filtered by sub_team above)

    stmt = stmt.order_by(Project.name)
    result = await db.execute(stmt)
    projects = result.scalars().unique().all()

    response = []
    for project in projects:
        # Separate milestone-grouped tasks from unassigned (D-04: no milestone = catch-all)
        milestones_out = []

        for milestone in project.milestones:
            milestone_tasks = [
                TimelineTaskOut.model_validate(t)
                for t in milestone.tasks
                if t.project_id == project.id
            ]
            milestones_out.append(
                TimelineMilestoneOut(
                    id=milestone.id,
                    title=milestone.title,
                    status=milestone.status,
                    start_date=milestone.start_date,
                    due_date=milestone.due_date,
                    tasks=milestone_tasks,
                )
            )

        # Fetch unassigned tasks: belong to this project but have no milestone_id
        unassigned_stmt = (
            select(Task)
            .where(Task.project_id == project.id, Task.milestone_id.is_(None))
            .options(selectinload(Task.assignee))
        )
        unassigned_result = await db.execute(unassigned_stmt)
        unassigned_tasks = [
            TimelineTaskOut.model_validate(t) for t in unassigned_result.scalars().all()
        ]

        response.append(
            TimelineProjectOut(
                id=project.id,
                name=project.name,
                color=project.color,
                milestones=milestones_out,
                unassigned_tasks=unassigned_tasks,
            )
        )

    return response
