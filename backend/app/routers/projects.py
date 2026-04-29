from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.utils.auth import get_current_user, get_sub_team
from app.db.database import get_db
from app.models import Project, SubTeam, User
from app.schemas import ProjectCreate, ProjectOut, ProjectUpdate
from app.services.visibility import (
    require_visible_sub_team_id,
    scoped_sub_team_filter,
    visible_sub_team_ids,
)

router = APIRouter(prefix="/api/projects", tags=["projects"])


@router.get("/", response_model=List[ProjectOut])
async def list_projects(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    sub_team: Optional[SubTeam] = Depends(get_sub_team),
):
    allowed_ids = await visible_sub_team_ids(
        db, current_user, requested_sub_team_id=sub_team.id if sub_team else None
    )
    stmt = select(Project)
    stmt = stmt.where(scoped_sub_team_filter(Project.sub_team_id, current_user, allowed_ids))
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post("/", response_model=ProjectOut, status_code=201)
async def create_project(
    payload: ProjectCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    sub_team: Optional[SubTeam] = Depends(get_sub_team),
):
    target_sub_team_id = payload.sub_team_id
    if target_sub_team_id is None:
        target_sub_team_id = sub_team.id if sub_team else current_user.sub_team_id
    target_sub_team_id = await require_visible_sub_team_id(
        db, current_user, target_sub_team_id
    )

    project = Project(
        name=payload.name,
        description=payload.description,
        color=payload.color,
        sub_team_id=target_sub_team_id,
    )
    db.add(project)
    await db.flush()
    await db.refresh(project)
    return project


@router.get("/{project_id}", response_model=ProjectOut)
async def get_project(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    allowed_ids = await visible_sub_team_ids(db, current_user)
    result = await db.execute(
        select(Project).where(
            Project.id == project_id,
            scoped_sub_team_filter(Project.sub_team_id, current_user, allowed_ids),
        )
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.patch("/{project_id}", response_model=ProjectOut)
async def update_project(
    project_id: int,
    payload: ProjectUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    allowed_ids = await visible_sub_team_ids(db, current_user)
    result = await db.execute(
        select(Project).where(
            Project.id == project_id,
            scoped_sub_team_filter(Project.sub_team_id, current_user, allowed_ids),
        )
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    update_data = payload.model_dump(exclude_unset=True)
    if "sub_team_id" in update_data:
        update_data["sub_team_id"] = await require_visible_sub_team_id(
            db, current_user, update_data["sub_team_id"]
        )
    for field, value in update_data.items():
        setattr(project, field, value)
    await db.flush()
    await db.refresh(project)
    return project


@router.delete("/{project_id}", status_code=204)
async def delete_project(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    allowed_ids = await visible_sub_team_ids(db, current_user)
    result = await db.execute(
        select(Project).where(
            Project.id == project_id,
            scoped_sub_team_filter(Project.sub_team_id, current_user, allowed_ids),
        )
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    await db.delete(project)
    await db.flush()
