import re
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.auth import get_current_user, get_sub_team
from app.database import get_db
from app.models import (
    CustomStatus,
    Project,
    StatusSet,
    StatusSetScope,
    SubTeam,
    Task,
    User,
    UserRole,
)
from app.schemas import (
    CustomStatusCreate,
    CustomStatusOut,
    CustomStatusUpdate,
    ProjectStatusRevertPayload,
    StatusDeletePayload,
    StatusReorderPayload,
    StatusSetOut,
)

router = APIRouter(prefix="/api/status-sets", tags=["status-sets"])


def _status_slug(name: str) -> str:
    slug = name.strip().lower()
    slug = re.sub(r"[^a-z0-9]+", "_", slug)
    return slug.strip("_")


async def _get_default_set(db: AsyncSession, sub_team_id: int) -> Optional[StatusSet]:
    result = await db.execute(
        select(StatusSet)
        .options(selectinload(StatusSet.statuses))
        .where(
            StatusSet.scope == StatusSetScope.sub_team_default,
            StatusSet.sub_team_id == sub_team_id,
        )
    )
    return result.scalar_one_or_none()


async def _get_project_or_404(db: AsyncSession, project_id: int) -> Project:
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


async def _get_effective_set(
    db: AsyncSession, project_id: Optional[int], sub_team_id: Optional[int]
) -> Optional[StatusSet]:
    if project_id:
        result = await db.execute(
            select(StatusSet)
            .options(selectinload(StatusSet.statuses))
            .where(
                StatusSet.scope == StatusSetScope.project,
                StatusSet.project_id == project_id,
            )
        )
        project_set = result.scalar_one_or_none()
        if project_set:
            return project_set
    if sub_team_id:
        return await _get_default_set(db, sub_team_id)
    result = await db.execute(
        select(StatusSet)
        .options(selectinload(StatusSet.statuses))
        .where(
            StatusSet.scope == StatusSetScope.sub_team_default,
            StatusSet.sub_team_id.is_(None),
        )
    )
    return result.scalar_one_or_none()


async def _copy_statuses(
    db: AsyncSession, source_set: StatusSet, target_set: StatusSet
) -> None:
    for s in source_set.statuses:
        copy = CustomStatus(
            status_set_id=target_set.id,
            name=s.name,
            slug=s.slug,
            color=s.color,
            position=s.position,
            is_done=s.is_done,
            is_archived=s.is_archived,
            legacy_status=s.legacy_status,
        )
        db.add(copy)


async def _status_task_count(db: AsyncSession, status_id: int) -> int:
    result = await db.execute(select(Task).where(Task.custom_status_id == status_id))
    return len(result.scalars().all())


def _require_status_write_scope(current_user: User, sub_team: Optional[SubTeam]) -> None:
    if current_user.role == UserRole.member:
        raise HTTPException(status_code=403, detail="Supervisor or admin access required")
    if current_user.role == UserRole.admin and sub_team is None:
        raise HTTPException(
            status_code=400,
            detail="Select a sub-team before editing default statuses",
        )


def _enrich_statuses(status_set: StatusSet, task_counts: dict) -> StatusSetOut:
    statuses_out = []
    for s in status_set.statuses:
        statuses_out.append(
            CustomStatusOut(
                id=s.id,
                status_set_id=s.status_set_id,
                name=s.name,
                slug=s.slug,
                color=s.color,
                position=s.position,
                is_done=s.is_done,
                is_archived=s.is_archived,
                legacy_status=s.legacy_status,
                task_count=task_counts.get(s.id, 0),
                created_at=s.created_at,
                updated_at=s.updated_at,
            )
        )
    return StatusSetOut(
        id=status_set.id,
        scope=status_set.scope,
        sub_team_id=status_set.sub_team_id,
        project_id=status_set.project_id,
        created_at=status_set.created_at,
        updated_at=status_set.updated_at,
        statuses=statuses_out,
    )


@router.get("/default", response_model=StatusSetOut)
async def get_default_set(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    sub_team: Optional[SubTeam] = Depends(get_sub_team),
):
    sub_team_id = sub_team.id if sub_team else None
    status_set = await _get_effective_set(db, None, sub_team_id)
    if not status_set:
        raise HTTPException(status_code=404, detail="No default status set found")
    task_counts = {}
    for s in status_set.statuses:
        task_counts[s.id] = await _status_task_count(db, s.id)
    return _enrich_statuses(status_set, task_counts)


@router.get("/effective", response_model=StatusSetOut)
async def get_effective_set(
    project_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    sub_team: Optional[SubTeam] = Depends(get_sub_team),
):
    sub_team_id = sub_team.id if sub_team else None
    if project_id:
        project = await _get_project_or_404(db, project_id)
        if not sub_team_id:
            sub_team_id = project.sub_team_id
    status_set = await _get_effective_set(db, project_id, sub_team_id)
    if not status_set:
        raise HTTPException(status_code=404, detail="No effective status set found")
    task_counts = {}
    for s in status_set.statuses:
        task_counts[s.id] = await _status_task_count(db, s.id)
    return _enrich_statuses(status_set, task_counts)


@router.post("/default/statuses", response_model=CustomStatusOut, status_code=201)
async def create_default_status(
    payload: CustomStatusCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    sub_team: Optional[SubTeam] = Depends(get_sub_team),
):
    _require_status_write_scope(current_user, sub_team)
    sub_team_id = sub_team.id if sub_team else None
    status_set = await _get_default_set(db, sub_team_id)
    if not status_set:
        raise HTTPException(status_code=404, detail="No default status set found")

    position = payload.position
    if position is None:
        active = [s for s in status_set.statuses if not s.is_archived]
        position = max((s.position for s in active), default=-1) + 1

    status = CustomStatus(
        status_set_id=status_set.id,
        name=payload.name,
        slug=_status_slug(payload.name),
        color=payload.color,
        position=position,
        is_done=payload.is_done,
        is_archived=False,
    )
    db.add(status)
    await db.flush()
    await db.refresh(status)
    return CustomStatusOut(
        id=status.id,
        status_set_id=status.status_set_id,
        name=status.name,
        slug=status.slug,
        color=status.color,
        position=status.position,
        is_done=status.is_done,
        is_archived=status.is_archived,
        legacy_status=status.legacy_status,
        task_count=0,
        created_at=status.created_at,
        updated_at=status.updated_at,
    )


@router.patch("/statuses/{status_id}", response_model=CustomStatusOut)
async def update_status(
    status_id: int,
    payload: CustomStatusUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    sub_team: Optional[SubTeam] = Depends(get_sub_team),
):
    _require_status_write_scope(current_user, sub_team)
    result = await db.execute(select(CustomStatus).where(CustomStatus.id == status_id))
    status = result.scalar_one_or_none()
    if not status:
        raise HTTPException(status_code=404, detail="Status not found")

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(status, field, value)
    await db.flush()
    await db.refresh(status)
    task_count = await _status_task_count(db, status.id)
    return CustomStatusOut(
        id=status.id,
        status_set_id=status.status_set_id,
        name=status.name,
        slug=status.slug,
        color=status.color,
        position=status.position,
        is_done=status.is_done,
        is_archived=status.is_archived,
        legacy_status=status.legacy_status,
        task_count=task_count,
        created_at=status.created_at,
        updated_at=status.updated_at,
    )


@router.post("/{status_set_id}/reorder", response_model=StatusSetOut)
async def reorder_statuses(
    status_set_id: int,
    payload: StatusReorderPayload,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    sub_team: Optional[SubTeam] = Depends(get_sub_team),
):
    _require_status_write_scope(current_user, sub_team)
    result = await db.execute(
        select(StatusSet)
        .options(selectinload(StatusSet.statuses))
        .where(StatusSet.id == status_set_id)
    )
    status_set = result.scalar_one_or_none()
    if not status_set:
        raise HTTPException(status_code=404, detail="Status set not found")

    status_map = {s.id: s for s in status_set.statuses}
    for position, sid in enumerate(payload.status_ids):
        if sid not in status_map:
            raise HTTPException(
                status_code=400, detail=f"Status {sid} not in this status set"
            )
        status_map[sid].position = position
    await db.flush()
    await db.refresh(status_set)
    task_counts = {}
    for s in status_set.statuses:
        task_counts[s.id] = await _status_task_count(db, s.id)
    return _enrich_statuses(status_set, task_counts)


@router.post("/statuses/{status_id}/delete", response_model=StatusSetOut)
async def delete_or_archive_status(
    status_id: int,
    payload: StatusDeletePayload,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    sub_team: Optional[SubTeam] = Depends(get_sub_team),
):
    _require_status_write_scope(current_user, sub_team)
    result = await db.execute(
        select(CustomStatus).where(CustomStatus.id == status_id)
    )
    status = result.scalar_one_or_none()
    if not status:
        raise HTTPException(status_code=404, detail="Status not found")

    task_count = await _status_task_count(db, status_id)

    if payload.mode == "archive":
        status.is_archived = True
        await db.flush()
    elif payload.mode == "move_delete":
        replacement_status_id = payload.replacement_status_id
        if not replacement_status_id:
            raise HTTPException(
                status_code=400,
                detail="replacement_status_id is required for move_delete mode",
            )
        result2 = await db.execute(
            select(CustomStatus).where(CustomStatus.id == replacement_status_id)
        )
        replacement = result2.scalar_one_or_none()
        if not replacement:
            raise HTTPException(status_code=404, detail="Replacement status not found")
        if replacement.status_set_id != status.status_set_id:
            raise HTTPException(
                status_code=400,
                detail="Replacement status must be in the same status set",
            )
        if replacement.is_archived:
            raise HTTPException(
                status_code=400, detail="Replacement status must not be archived"
            )
        tasks_result = await db.execute(
            select(Task).where(Task.custom_status_id == status_id)
        )
        for task in tasks_result.scalars().all():
            task.custom_status_id = replacement_status_id
        await db.flush()
        await db.delete(status)
        await db.flush()
    else:
        if task_count > 0:
            raise HTTPException(
                status_code=400,
                detail="Statuses with tasks must be moved or archived before they can be deleted.",
            )
        await db.delete(status)
        await db.flush()

    set_result = await db.execute(
        select(StatusSet)
        .options(selectinload(StatusSet.statuses))
        .where(StatusSet.id == status.status_set_id)
    )
    status_set = set_result.scalar_one_or_none()
    task_counts = {}
    if status_set:
        for s in status_set.statuses:
            task_counts[s.id] = await _status_task_count(db, s.id)
    return _enrich_statuses(status_set, task_counts)


@router.post("/projects/{project_id}/override", response_model=StatusSetOut, status_code=201)
async def create_project_override(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    sub_team: Optional[SubTeam] = Depends(get_sub_team),
):
    _require_status_write_scope(current_user, sub_team)
    project = await _get_project_or_404(db, project_id)

    existing = await db.execute(
        select(StatusSet).where(
            StatusSet.scope == StatusSetScope.project,
            StatusSet.project_id == project_id,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=409, detail="Project already has a status override"
        )

    sub_team_id = sub_team.id if sub_team else project.sub_team_id
    effective = await _get_effective_set(db, None, sub_team_id)

    project_set = StatusSet(
        scope=StatusSetScope.project,
        project_id=project_id,
        sub_team_id=sub_team_id,
    )
    db.add(project_set)
    await db.flush()
    await db.refresh(project_set)

    if effective:
        await _copy_statuses(db, effective, project_set)
        await db.flush()

    await db.refresh(project_set, ["statuses"])
    task_counts = {}
    for s in project_set.statuses:
        task_counts[s.id] = 0
    return _enrich_statuses(project_set, task_counts)


@router.delete("/projects/{project_id}/override", response_model=StatusSetOut)
async def revert_project_override(
    project_id: int,
    payload: ProjectStatusRevertPayload,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    sub_team: Optional[SubTeam] = Depends(get_sub_team),
):
    _require_status_write_scope(current_user, sub_team)
    project = await _get_project_or_404(db, project_id)

    result = await db.execute(
        select(StatusSet)
        .options(selectinload(StatusSet.statuses))
        .where(
            StatusSet.scope == StatusSetScope.project,
            StatusSet.project_id == project_id,
        )
    )
    project_set = result.scalar_one_or_none()
    if not project_set:
        raise HTTPException(status_code=404, detail="No project override found")

    sub_team_id = sub_team.id if sub_team else project.sub_team_id
    default_set = await _get_default_set(db, sub_team_id)
    if not default_set:
        raise HTTPException(status_code=404, detail="No default status set found")

    default_by_slug = {s.slug: s for s in default_set.statuses}
    fallback_mappings = payload.fallback_mappings

    unmatched = []
    slug_map: dict[int, int] = {}
    for project_status in project_set.statuses:
        if project_status.slug in default_by_slug:
            slug_map[project_status.id] = default_by_slug[project_status.slug].id
        elif project_status.id in fallback_mappings:
            slug_map[project_status.id] = fallback_mappings[project_status.id]
        else:
            task_count = await _status_task_count(db, project_status.id)
            if task_count > 0:
                unmatched.append(
                    {
                        "id": project_status.id,
                        "name": project_status.name,
                        "slug": project_status.slug,
                        "task_count": task_count,
                    }
                )

    if unmatched:
        raise HTTPException(
            status_code=400,
            detail={
                "message": "Unmatched project statuses require explicit fallback_mappings",
                "unmatched": unmatched,
            },
        )

    for project_status in project_set.statuses:
        target_id = slug_map.get(project_status.id)
        if target_id:
            tasks_result = await db.execute(
                select(Task).where(Task.custom_status_id == project_status.id)
            )
            for task in tasks_result.scalars().all():
                task.custom_status_id = target_id
    await db.flush()

    await db.delete(project_set)
    await db.flush()

    await db.refresh(default_set, ["statuses"])
    task_counts = {}
    for s in default_set.statuses:
        task_counts[s.id] = await _status_task_count(db, s.id)
    return _enrich_statuses(default_set, task_counts)
