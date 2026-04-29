from __future__ import annotations

from typing import Iterable, Optional

from fastapi import HTTPException, status
from sqlalchemy import false, or_, select, true
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.elements import ColumnElement

from app.models import SubTeam, User, UserRole

LEADERSHIP_ROLES = (UserRole.supervisor, UserRole.assistant_manager)
ACTIVE_ROLES = (
    UserRole.manager,
    UserRole.supervisor,
    UserRole.assistant_manager,
    UserRole.member,
)


def is_manager(user: User) -> bool:
    return user.role == UserRole.manager


def is_leader(user: User) -> bool:
    return user.role in LEADERSHIP_ROLES


def is_member(user: User) -> bool:
    return user.role == UserRole.member


def is_active_role(role: UserRole | str) -> bool:
    value = role.value if isinstance(role, UserRole) else role
    return value in {active_role.value for active_role in ACTIVE_ROLES}


def _unique_ids(ids: Iterable[int | None]) -> list[int]:
    return sorted({item for item in ids if item is not None})


async def leader_sub_team_ids(session: AsyncSession, user: User) -> list[int]:
    result = await session.execute(
        select(SubTeam.id).where(SubTeam.supervisor_id == user.id)
    )
    supervised_ids = [row[0] for row in result.all()]
    return _unique_ids([user.sub_team_id, *supervised_ids])


async def visible_sub_team_ids(
    session: AsyncSession,
    current_user: User,
    requested_sub_team_id: Optional[int] = None,
) -> Optional[list[int]]:
    if is_manager(current_user):
        if requested_sub_team_id is None:
            return None
        result = await session.execute(
            select(SubTeam.id).where(SubTeam.id == requested_sub_team_id)
        )
        if result.scalar_one_or_none() is None:
            raise HTTPException(status_code=403, detail="Invalid sub-team")
        return [requested_sub_team_id]

    if is_member(current_user):
        if current_user.sub_team_id is None:
            return []
        if requested_sub_team_id is not None and requested_sub_team_id != current_user.sub_team_id:
            raise HTTPException(status_code=403, detail="Invalid sub-team")
        return [current_user.sub_team_id]

    if is_leader(current_user):
        allowed_ids = await leader_sub_team_ids(session, current_user)
        if requested_sub_team_id is None:
            return allowed_ids
        if requested_sub_team_id not in allowed_ids:
            raise HTTPException(status_code=403, detail="Invalid sub-team")
        return [requested_sub_team_id]

    return []


async def resolve_visible_sub_team(
    session: AsyncSession,
    current_user: User,
    requested_sub_team_id: Optional[int] = None,
) -> Optional[SubTeam]:
    allowed_ids = await visible_sub_team_ids(
        session, current_user, requested_sub_team_id=requested_sub_team_id
    )
    if allowed_ids is None:
        return None
    if not allowed_ids:
        return None
    result = await session.execute(select(SubTeam).where(SubTeam.id == allowed_ids[0]))
    return result.scalar_one_or_none()


def visible_user_filter(
    current_user: User,
    allowed_sub_team_ids: Optional[list[int]] = None,
) -> ColumnElement[bool]:
    if is_manager(current_user):
        return true()
    if is_member(current_user):
        if current_user.sub_team_id is None:
            return false()
        return User.sub_team_id == current_user.sub_team_id
    if is_leader(current_user):
        ids = allowed_sub_team_ids or []
        if not ids:
            return false()
        return (User.sub_team_id.in_(ids)) & (
            (User.role == UserRole.member) | (User.role.in_(LEADERSHIP_ROLES))
        )
    return false()


async def visible_users_query(
    session: AsyncSession,
    current_user: User,
    requested_sub_team_id: Optional[int] = None,
):
    allowed_ids = await visible_sub_team_ids(
        session, current_user, requested_sub_team_id=requested_sub_team_id
    )
    return select(User).where(visible_user_filter(current_user, allowed_ids))


def scoped_sub_team_filter(
    sub_team_id_column,
    current_user: User,
    allowed_sub_team_ids: Optional[list[int]] = None,
) -> ColumnElement[bool]:
    if is_manager(current_user):
        if allowed_sub_team_ids is None:
            return true()
        return sub_team_id_column.in_(allowed_sub_team_ids)
    ids = allowed_sub_team_ids or []
    if not ids:
        return false()
    return sub_team_id_column.in_(ids)


async def visible_scoped_filter(
    session: AsyncSession,
    sub_team_id_column,
    current_user: User,
    requested_sub_team_id: Optional[int] = None,
) -> ColumnElement[bool]:
    allowed_ids = await visible_sub_team_ids(
        session, current_user, requested_sub_team_id=requested_sub_team_id
    )
    return scoped_sub_team_filter(sub_team_id_column, current_user, allowed_ids)


async def can_see_user(
    session: AsyncSession,
    current_user: User,
    target_user: User,
) -> bool:
    if is_manager(current_user):
        return True
    allowed_ids = await visible_sub_team_ids(session, current_user)
    if allowed_ids is None:
        return True
    if target_user.sub_team_id not in allowed_ids:
        return False
    if is_leader(current_user):
        return target_user.role == UserRole.member or target_user.role in LEADERSHIP_ROLES
    return is_member(current_user)


async def require_visible_user(
    session: AsyncSession,
    current_user: User,
    target_user: User,
) -> User:
    if not await can_see_user(session, current_user, target_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User outside visible scope",
        )
    return target_user


async def peer_leader_ids(session: AsyncSession, current_user: User) -> list[int]:
    if is_manager(current_user):
        result = await session.execute(
            select(User.id).where(User.role.in_(LEADERSHIP_ROLES))
        )
        return [row[0] for row in result.all()]
    if not is_leader(current_user):
        return []
    allowed_ids = await leader_sub_team_ids(session, current_user)
    if not allowed_ids:
        return []
    result = await session.execute(
        select(User.id).where(
            User.id != current_user.id,
            User.role.in_(LEADERSHIP_ROLES),
            User.sub_team_id.in_(allowed_ids),
        )
    )
    return [row[0] for row in result.all()]
