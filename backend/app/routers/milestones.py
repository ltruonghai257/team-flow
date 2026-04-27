from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.utils.auth import get_current_user
from app.db.database import get_db
from app.models import Milestone, User
from app.schemas import MilestoneCreate, MilestoneOut, MilestoneUpdate
from app.services.reminder_notifications import rebuild_milestone_reminders

router = APIRouter(prefix="/api/milestones", tags=["milestones"])


@router.get("/", response_model=List[MilestoneOut])
async def list_milestones(
    project_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    query = select(Milestone)
    if project_id:
        query = query.where(Milestone.project_id == project_id)
    query = query.order_by(Milestone.due_date)
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/", response_model=MilestoneOut, status_code=201)
async def create_milestone(
    payload: MilestoneCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    milestone = Milestone(**payload.model_dump())
    db.add(milestone)
    await db.flush()
    await db.refresh(milestone)
    
    # Rebuild reminders for milestone
    await rebuild_milestone_reminders(db, milestone.id)
    
    return milestone


@router.get("/{milestone_id}", response_model=MilestoneOut)
async def get_milestone(milestone_id: int, db: AsyncSession = Depends(get_db), _: User = Depends(get_current_user)):
    result = await db.execute(select(Milestone).where(Milestone.id == milestone_id))
    milestone = result.scalar_one_or_none()
    if not milestone:
        raise HTTPException(status_code=404, detail="Milestone not found")
    return milestone


@router.patch("/{milestone_id}", response_model=MilestoneOut)
async def update_milestone(
    milestone_id: int,
    payload: MilestoneUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    result = await db.execute(select(Milestone).where(Milestone.id == milestone_id))
    milestone = result.scalar_one_or_none()
    if not milestone:
        raise HTTPException(status_code=404, detail="Milestone not found")
    
    # Track if due_date changed
    old_due_date = milestone.due_date
    
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(milestone, field, value)
    await db.flush()
    await db.refresh(milestone)
    
    # Rebuild reminders if due_date changed
    if old_due_date != milestone.due_date:
        await rebuild_milestone_reminders(db, milestone.id)
    
    return milestone


@router.delete("/{milestone_id}", status_code=204)
async def delete_milestone(
    milestone_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    result = await db.execute(select(Milestone).where(Milestone.id == milestone_id))
    milestone = result.scalar_one_or_none()
    if not milestone:
        raise HTTPException(status_code=404, detail="Milestone not found")
    await db.delete(milestone)
    await db.flush()
