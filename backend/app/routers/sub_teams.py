from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user, require_admin, require_supervisor_or_admin
from app.database import get_db
from app.models import SubTeam, User
from app.schemas import SubTeamCreate, SubTeamOut, SubTeamUpdate

router = APIRouter(prefix="/api/sub-teams", tags=["sub-teams"])


@router.post("/", response_model=SubTeamOut, status_code=201)
async def create_sub_team(
    sub_team: SubTeamCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_supervisor_or_admin),
):
    new_sub_team = SubTeam(**sub_team.model_dump())
    db.add(new_sub_team)
    await db.commit()
    await db.refresh(new_sub_team)
    return new_sub_team


@router.get("/", response_model=List[SubTeamOut])
async def list_sub_teams(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_supervisor_or_admin),
):
    result = await db.execute(select(SubTeam))
    return result.scalars().all()


@router.put("/{sub_team_id}", response_model=SubTeamOut)
async def update_sub_team(
    sub_team_id: int,
    sub_team_update: SubTeamUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_supervisor_or_admin),
):
    result = await db.execute(select(SubTeam).where(SubTeam.id == sub_team_id))
    sub_team = result.scalar_one_or_none()
    if not sub_team:
        raise HTTPException(status_code=404, detail="Sub-team not found")
    for field, value in sub_team_update.model_dump(exclude_unset=True).items():
        setattr(sub_team, field, value)
    await db.commit()
    await db.refresh(sub_team)
    return sub_team


@router.delete("/{sub_team_id}", status_code=204)
async def delete_sub_team(
    sub_team_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    result = await db.execute(select(SubTeam).where(SubTeam.id == sub_team_id))
    sub_team = result.scalar_one_or_none()
    if not sub_team:
        raise HTTPException(status_code=404, detail="Sub-team not found")
    await db.delete(sub_team)
    await db.commit()
