import logging
import secrets
from datetime import datetime, timedelta, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import (
    create_access_token,
    get_current_user,
    get_sub_team,
    hash_password,
    require_supervisor_or_admin,
)
from app.config import settings
from app.database import get_db
from app.email_service import send_invite_email
from app.limiter import limiter
from app.models import InviteStatus, SubTeam, TeamInvite, User, UserRole
from app.schemas import (
    DirectAddRequest,
    InviteAcceptRequest,
    InviteCreate,
    InviteOut,
    InviteValidateOut,
    UserOut,
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["invites"])

_COOKIE_NAME = "access_token"
_INVITE_TTL_HOURS = 72


def _generate_token() -> str:
    return secrets.token_urlsafe(32)


def _generate_validation_code() -> str:
    return str(secrets.randbelow(900000) + 100000)


@router.post("/api/teams/invite", response_model=InviteOut, status_code=201)
@limiter.limit("10/hour")
async def send_invite(
    request: Request,
    payload: InviteCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_supervisor_or_admin),
    sub_team: Optional[SubTeam] = Depends(get_sub_team),
):
    result = await db.execute(
        select(TeamInvite).where(
            TeamInvite.email == payload.email,
            TeamInvite.status == InviteStatus.pending,
        )
    )
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(
            status_code=400, detail="A pending invite already exists for this email"
        )

    result = await db.execute(select(User).where(User.email == payload.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=400, detail="User with this email is already registered"
        )

    # Determine target sub_team_id from inviter's context per D-16/D-17
    target_sub_team_id = payload.sub_team_id
    if target_sub_team_id is None:
        # Use inviter's current sub-team context
        if current_user.role == UserRole.admin:
            target_sub_team_id = sub_team.id if sub_team else None
        elif current_user.role == UserRole.supervisor:
            target_sub_team_id = current_user.sub_team_id
        else:
            target_sub_team_id = current_user.sub_team_id

    token = _generate_token()
    code = _generate_validation_code()
    expires_at = datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(
        hours=_INVITE_TTL_HOURS
    )

    invite = TeamInvite(
        email=payload.email,
        role=payload.role,
        token=token,
        validation_code=code,
        status=InviteStatus.pending,
        invited_by_id=current_user.id,
        sub_team_id=target_sub_team_id,
        expires_at=expires_at,
    )
    db.add(invite)
    await db.flush()
    await db.refresh(invite)

    try:
        await send_invite_email(
            to_email=payload.email,
            invited_by_name=current_user.full_name,
            role=payload.role.value,
            validation_code=code,
            token=token,
        )
    except Exception as exc:
        logger.warning("Failed to send invite email to %s: %s", payload.email, exc)

    return invite


@router.post("/api/teams/add", response_model=UserOut)
async def direct_add_member(
    payload: DirectAddRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_supervisor_or_admin),
):
    result = await db.execute(select(User).where(User.id == payload.user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="User is not active")

    if payload.role is not None:
        if current_user.role != UserRole.admin and payload.role != UserRole.member:
            raise HTTPException(
                status_code=403, detail="Only admins can assign non-member roles"
            )
        user.role = payload.role
        await db.flush()
        await db.refresh(user)

    return user


@router.get("/api/invites/validate", response_model=InviteValidateOut)
async def validate_invite(
    token: str,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(TeamInvite).where(TeamInvite.token == token))
    invite = result.scalar_one_or_none()
    if not invite:
        raise HTTPException(status_code=404, detail="Invite not found")

    now = datetime.now(timezone.utc).replace(tzinfo=None)
    valid = invite.status == InviteStatus.pending and now <= invite.expires_at

    result = await db.execute(select(User).where(User.id == invite.invited_by_id))
    inviter = result.scalar_one_or_none()
    invited_by_name = inviter.full_name if inviter else "Unknown"

    return InviteValidateOut(
        id=invite.id,
        email=invite.email,
        role=invite.role.value,
        invited_by_name=invited_by_name,
        expires_at=invite.expires_at,
        valid=valid,
    )


@router.post("/api/invites/accept", response_model=UserOut, status_code=201)
async def accept_invite(
    payload: InviteAcceptRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(TeamInvite).where(TeamInvite.token == payload.token)
    )
    invite = result.scalar_one_or_none()
    if not invite:
        raise HTTPException(status_code=404, detail="Invite not found")
    if invite.status != InviteStatus.pending:
        raise HTTPException(
            status_code=400, detail="Invite has already been used or cancelled"
        )

    now = datetime.now(timezone.utc).replace(tzinfo=None)
    if now > invite.expires_at:
        invite.status = InviteStatus.expired
        await db.flush()
        raise HTTPException(status_code=400, detail="Invite has expired")

    if payload.validation_code != invite.validation_code:
        raise HTTPException(status_code=400, detail="Invalid validation code")

    result = await db.execute(select(User).where(User.email == invite.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=400, detail="An account with this email already exists"
        )

    result = await db.execute(select(User).where(User.username == payload.username))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Username already taken")

    user = User(
        email=invite.email,
        username=payload.username,
        full_name=payload.full_name,
        hashed_password=hash_password(payload.password),
        role=invite.role,
        sub_team_id=invite.sub_team_id,  # Per D-18: auto-assign to invite's sub-team
        is_active=True,
    )
    db.add(user)

    invite.status = InviteStatus.accepted
    invite.accepted_at = now

    await db.flush()
    await db.refresh(user)

    token = create_access_token({"sub": str(user.id)})
    max_age = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    response.set_cookie(
        key=_COOKIE_NAME,
        value=token,
        max_age=max_age,
        httponly=True,
        samesite="lax",
        secure=settings.COOKIE_SECURE,
        path="/",
    )

    return user


@router.get("/api/invites/pending", response_model=List[InviteOut])
async def list_pending_invites(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_supervisor_or_admin),
):
    result = await db.execute(
        select(TeamInvite)
        .where(TeamInvite.status == InviteStatus.pending)
        .order_by(TeamInvite.created_at.desc())
    )
    return result.scalars().all()


@router.delete("/api/invites/{invite_id}", status_code=204)
async def cancel_invite(
    invite_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_supervisor_or_admin),
):
    result = await db.execute(select(TeamInvite).where(TeamInvite.id == invite_id))
    invite = result.scalar_one_or_none()
    if not invite:
        raise HTTPException(status_code=404, detail="Invite not found")
    if invite.status != InviteStatus.pending:
        raise HTTPException(
            status_code=400, detail="Only pending invites can be cancelled"
        )
    invite.status = InviteStatus.cancelled
    await db.flush()
