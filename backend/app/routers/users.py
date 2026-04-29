from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.utils.auth import get_current_user, get_sub_team, require_manager
from app.db.database import get_db
from app.models import SubTeam, User, UserRole
from app.schemas import UserOut, UserRoleUpdate, UserUpdate
from app.services.visibility import (
    can_see_user,
    is_leader,
    is_manager,
    require_visible_user,
    visible_sub_team_ids,
    visible_users_query,
)

router = APIRouter(prefix="/api/users", tags=["users"])


PROFILE_FIELDS = {"full_name", "avatar_url"}
LEADERSHIP_ROLES = {
    UserRole.manager,
    UserRole.supervisor,
    UserRole.assistant_manager,
}


def _payload_fields(payload: UserUpdate) -> set[str]:
    return set(payload.model_dump(exclude_unset=True).keys())


def _payload_role(payload: UserUpdate) -> Optional[UserRole]:
    if payload.role is None:
        return None
    return payload.role if isinstance(payload.role, UserRole) else UserRole(payload.role)


async def _require_update_allowed(
    db: AsyncSession,
    current_user: User,
    target_user: User,
    payload: UserUpdate,
) -> None:
    fields = _payload_fields(payload)
    role = _payload_role(payload)

    if is_manager(current_user):
        return

    if current_user.id == target_user.id:
        if fields - PROFILE_FIELDS:
            raise HTTPException(status_code=403, detail="Cannot change own role or scope")
        return

    if not is_leader(current_user):
        raise HTTPException(status_code=403, detail="Not allowed")

    if target_user.role != UserRole.member:
        raise HTTPException(status_code=403, detail="Leaders can manage members only")

    if not await can_see_user(db, current_user, target_user):
        raise HTTPException(status_code=403, detail="User outside visible scope")

    if role is not None and role != UserRole.member:
        raise HTTPException(
            status_code=403,
            detail="Only managers can assign leadership roles",
        )

    if payload.sub_team_id is not None:
        allowed_ids = await visible_sub_team_ids(db, current_user)
        if allowed_ids is None or payload.sub_team_id not in allowed_ids:
            raise HTTPException(status_code=403, detail="Invalid sub-team")


@router.get("/", response_model=List[UserOut])
async def list_users(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    sub_team: Optional[SubTeam] = Depends(get_sub_team),
):
    stmt = await visible_users_query(
        db,
        current_user,
        requested_sub_team_id=sub_team.id if sub_team else None,
    )
    stmt = stmt.where(User.is_active.is_(True))
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/{user_id}", response_model=UserOut)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(User).where(User.id == user_id, User.is_active.is_(True)))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return await require_visible_user(db, current_user, user)


@router.patch("/{user_id}", response_model=UserOut)
async def update_user(
    user_id: int,
    payload: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(User).where(User.id == user_id, User.is_active.is_(True)))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    await _require_update_allowed(db, current_user, user, payload)

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(user, field, value)
    await db.flush()
    await db.refresh(user)
    return user


@router.patch("/{user_id}/role", response_model=UserOut)
async def update_user_role(
    user_id: int,
    payload: UserRoleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_manager),
):
    result = await db.execute(select(User).where(User.id == user_id, User.is_active.is_(True)))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.role = payload.role
    await db.flush()
    await db.refresh(user)
    return user


@router.delete("/{user_id}", status_code=204)
async def deactivate_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not is_manager(current_user):
        raise HTTPException(status_code=403, detail="Manager only")
    result = await db.execute(select(User).where(User.id == user_id, User.is_active.is_(True)))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_active = False
    await db.flush()
