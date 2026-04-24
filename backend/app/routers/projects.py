from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user, get_sub_team
from app.database import get_db
from app.models import Project, SubTeam, User, UserRole
from app.schemas import ProjectCreate, ProjectOut, ProjectUpdate

router = APIRouter(prefix="/api/projects", tags=["projects"])


@router.get("/", response_model=List[ProjectOut])
async def list_projects(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    sub_team: Optional[SubTeam] = Depends(get_sub_team),
):
    stmt = select(Project)
    if sub_team:
        stmt = stmt.where(Project.sub_team_id == sub_team.id)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post("/", response_model=ProjectOut, status_code=201)
async def create_project(
    payload: ProjectCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    sub_team: Optional[SubTeam] = Depends(get_sub_team),
):
    # Determine target sub_team_id per D-13/D-14
    target_sub_team_id = payload.sub_team_id
    if target_sub_team_id is None:
        if current_user.role == UserRole.admin:
            target_sub_team_id = sub_team.id if sub_team else None
        elif current_user.role == UserRole.supervisor:
            target_sub_team_id = current_user.sub_team_id
        else:
            target_sub_team_id = current_user.sub_team_id

    # Per D-15: Reject supervisors creating projects outside their sub-team
    if current_user.role == UserRole.supervisor:
        if target_sub_team_id != current_user.sub_team_id:
            raise HTTPException(
                status_code=403,
                detail="Supervisors can only create projects for their own sub-team",
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
    _: User = Depends(get_current_user),
):
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.patch("/{project_id}", response_model=ProjectOut)
async def update_project(
    project_id: int,
    payload: ProjectUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(project, field, value)
    await db.flush()
    await db.refresh(project)
    return project


@router.delete("/{project_id}", status_code=204)
async def delete_project(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    await db.delete(project)
    await db.flush()
