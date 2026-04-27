from typing import List, Optional, Dict

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.utils.auth import get_current_user, get_sub_team
from app.db.database import get_db
from app.models import Milestone, Project, Sprint, SubTeam, Task, User, SprintStatus
from app.schemas import SprintCreate, SprintOut, SprintUpdate, SprintClosePayload
from app.services.reminder_notifications import rebuild_sprint_reminders

router = APIRouter(prefix="/api/sprints", tags=["sprints"])


@router.get("/", response_model=List[SprintOut])
async def list_sprints(
    project_id: Optional[int] = None,
    milestone_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    sub_team: Optional[SubTeam] = Depends(get_sub_team),
):
    query = select(Sprint).join(Milestone, Sprint.milestone_id == Milestone.id)
    
    # Apply sub-team filter (admin may have None = all teams)
    if sub_team or project_id:
        query = query.join(Project, Milestone.project_id == Project.id)
        
    if sub_team:
        query = query.where(Project.sub_team_id == sub_team.id)
    
    if project_id:
        query = query.where(Project.id == project_id)
        
    if milestone_id:
        query = query.where(Sprint.milestone_id == milestone_id)
        
    query = query.order_by(Sprint.start_date.desc().nulls_last())
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/", response_model=SprintOut, status_code=201)
async def create_sprint(
    payload: SprintCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    # Verify milestone exists
    milestone_result = await db.execute(select(Milestone).where(Milestone.id == payload.milestone_id))
    if not milestone_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Milestone not found")
        
    sprint = Sprint(**payload.model_dump())
    db.add(sprint)
    await db.flush()
    await db.refresh(sprint)
    
    # Rebuild reminders if sprint has an end date
    if sprint.end_date is not None:
        await rebuild_sprint_reminders(db, sprint.id)
    
    return sprint


@router.get("/{sprint_id}", response_model=SprintOut)
async def get_sprint(
    sprint_id: int, 
    db: AsyncSession = Depends(get_db), 
    _: User = Depends(get_current_user)
):
    result = await db.execute(select(Sprint).where(Sprint.id == sprint_id))
    sprint = result.scalar_one_or_none()
    if not sprint:
        raise HTTPException(status_code=404, detail="Sprint not found")
    return sprint


@router.patch("/{sprint_id}", response_model=SprintOut)
async def update_sprint(
    sprint_id: int,
    payload: SprintUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    result = await db.execute(select(Sprint).where(Sprint.id == sprint_id))
    sprint = result.scalar_one_or_none()
    if not sprint:
        raise HTTPException(status_code=404, detail="Sprint not found")
    
    # Track if end_date changed
    old_end_date = sprint.end_date
    
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(sprint, field, value)
        
    await db.flush()
    await db.refresh(sprint)
    
    # Rebuild reminders if end_date changed
    if old_end_date != sprint.end_date:
        await rebuild_sprint_reminders(db, sprint.id)
    
    return sprint


@router.delete("/{sprint_id}", status_code=204)
async def delete_sprint(
    sprint_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    result = await db.execute(select(Sprint).where(Sprint.id == sprint_id))
    sprint = result.scalar_one_or_none()
    if not sprint:
        raise HTTPException(status_code=404, detail="Sprint not found")
    
    await db.delete(sprint)
    await db.flush()


@router.post("/{sprint_id}/close", status_code=200)
async def close_sprint(
    sprint_id: int,
    payload: SprintClosePayload,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    result = await db.execute(select(Sprint).where(Sprint.id == sprint_id))
    sprint = result.scalar_one_or_none()
    if not sprint:
        raise HTTPException(status_code=404, detail="Sprint not found")
    
    sprint.status = SprintStatus.closed
    
    # Bulk update tasks
    for task_id, next_sprint_id in payload.task_mapping.items():
        await db.execute(
            update(Task)
            .where(Task.id == task_id)
            .values(sprint_id=next_sprint_id)
        )
        
    await db.flush()
    return {"message": "Sprint closed and tasks reassigned"}
