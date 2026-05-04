---
id: 08-02
wave: 2
title: Invite/Accept API Endpoints & Email Service
depends_on: [08-01]
files_modified:
  - backend/app/email_service.py
  - backend/app/routers/invites.py
  - backend/app/main.py
  - backend/.env.example
autonomous: true
requirements:
  - REQ-08
---

# Plan 08-02: Invite/Accept API Endpoints & Email Service

## Goal

Implement the email sending service and all backend API endpoints for the invite flow: send invite email, direct-add user, validate token, accept invite, list pending invites, and cancel invite.

## must_haves

- `backend/app/email_service.py` created with `send_invite_email()` that sends HTML invite email
- `backend/app/routers/invites.py` created with all 6 endpoints
- All endpoints registered in `backend/app/main.py`
- `POST /api/teams/invite` requires supervisor/admin, sends email, returns `InviteOut`
- `POST /api/teams/add` requires supervisor/admin, returns `UserOut`
- `GET /api/invites/validate?token=…` is public, returns `InviteValidateOut`
- `POST /api/invites/accept` is public, creates user, sets auth cookie, returns `UserOut`
- `GET /api/invites/pending` requires supervisor/admin, returns list of `InviteOut`
- `DELETE /api/invites/{invite_id}` requires supervisor/admin, cancels invite
- Email sending degrades gracefully when `MAIL_USERNAME` is empty (logs warning, skips send)

---

## Tasks

<task id="08-02-T1">
<title>Create email_service.py with invite email sender</title>
<type>execute</type>
<priority>blocking</priority>

<read_first>
- `backend/app/config.py` — Settings fields just added: MAIL_USERNAME, MAIL_PASSWORD, MAIL_FROM, MAIL_FROM_NAME, MAIL_SERVER, MAIL_PORT, MAIL_STARTTLS, MAIL_SSL_TLS, FRONTEND_URL
- `backend/requirements.txt` — fastapi-mail>=1.4.1 (just added)
</read_first>

<action>
Create `backend/app/email_service.py` with the following content:

```python
import logging
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from app.config import settings

logger = logging.getLogger(__name__)

_conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_STARTTLS=settings.MAIL_STARTTLS,
    MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
    USE_CREDENTIALS=bool(settings.MAIL_USERNAME),
    VALIDATE_CERTS=True,
)


def _build_invite_html(invited_by_name: str, role: str, validation_code: str, accept_url: str) -> str:
    return f"""
<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><title>TeamFlow Invite</title></head>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #0f172a; color: #e2e8f0; margin: 0; padding: 40px 20px;">
  <div style="max-width: 480px; margin: 0 auto; background: #1e293b; border-radius: 12px; padding: 32px; border: 1px solid #334155;">
    <div style="margin-bottom: 24px;">
      <div style="width: 40px; height: 40px; background: #6366f1; border-radius: 8px; display: inline-flex; align-items: center; justify-content: center; color: white; font-weight: bold; font-size: 18px;">T</div>
      <span style="font-size: 20px; font-weight: 600; color: white; margin-left: 10px; vertical-align: middle;">TeamFlow</span>
    </div>
    <h1 style="font-size: 22px; font-weight: 600; color: white; margin: 0 0 8px;">You've been invited</h1>
    <p style="color: #94a3b8; margin: 0 0 24px;">{invited_by_name} has invited you to join TeamFlow as a <strong style="color: #a5b4fc;">{role}</strong>.</p>
    <div style="background: #0f172a; border-radius: 8px; padding: 20px; text-align: center; margin-bottom: 24px; border: 1px solid #334155;">
      <p style="color: #94a3b8; font-size: 13px; margin: 0 0 8px; text-transform: uppercase; letter-spacing: 0.05em;">Your Validation Code</p>
      <p style="color: white; font-size: 36px; font-weight: 700; letter-spacing: 0.15em; margin: 0; font-family: monospace;">{validation_code}</p>
    </div>
    <a href="{accept_url}" style="display: block; background: #6366f1; color: white; text-decoration: none; text-align: center; padding: 14px 24px; border-radius: 8px; font-weight: 600; font-size: 15px; margin-bottom: 20px;">Accept Invitation</a>
    <p style="color: #64748b; font-size: 12px; margin: 0;">This invitation expires in 72 hours. If you did not expect this email, you can safely ignore it.</p>
  </div>
</body>
</html>
"""


async def send_invite_email(
    to_email: str,
    invited_by_name: str,
    role: str,
    validation_code: str,
    token: str,
) -> None:
    if not settings.MAIL_USERNAME:
        logger.warning("MAIL_USERNAME not configured — skipping invite email to %s (code: %s)", to_email, validation_code)
        return

    accept_url = f"{settings.FRONTEND_URL}/invite/accept?token={token}"
    html_body = _build_invite_html(invited_by_name, role, validation_code, accept_url)

    message = MessageSchema(
        subject="You've been invited to join TeamFlow",
        recipients=[to_email],
        body=html_body,
        subtype=MessageType.html,
    )
    fm = FastMail(_conf)
    await fm.send_message(message)
    logger.info("Invite email sent to %s", to_email)
```
</action>

<acceptance_criteria>
- File `backend/app/email_service.py` exists
- `backend/app/email_service.py` contains `async def send_invite_email(`
- `backend/app/email_service.py` contains `if not settings.MAIL_USERNAME:`
- `backend/app/email_service.py` contains `logger.warning("MAIL_USERNAME not configured`
- `backend/app/email_service.py` contains `FastMail(_conf)`
- `backend/app/email_service.py` contains `accept_url = f"{settings.FRONTEND_URL}/invite/accept?token={token}"`
</acceptance_criteria>
</task>

<task id="08-02-T2">
<title>Create invites router with all 6 endpoints</title>
<type>execute</type>
<priority>blocking</priority>

<read_first>
- `backend/app/routers/auth.py` — cookie-setting pattern in login endpoint (lines 60-71), `_COOKIE_NAME`, `response.set_cookie(...)` pattern
- `backend/app/routers/users.py` — existing router structure, `APIRouter(prefix=...)`, dependency pattern
- `backend/app/auth.py` — `require_supervisor_or_admin` (just added), `get_current_user`, `hash_password`, `create_access_token`
- `backend/app/models.py` — `TeamInvite`, `InviteStatus`, `User`, `UserRole`
- `backend/app/schemas.py` — `InviteCreate`, `InviteOut`, `InviteValidateOut`, `InviteAcceptRequest`, `DirectAddRequest`, `UserOut`
- `backend/app/config.py` — `settings.ACCESS_TOKEN_EXPIRE_MINUTES`, `settings.COOKIE_SECURE`
- `backend/app/email_service.py` — `send_invite_email()`
</read_first>

<action>
Create `backend/app/routers/invites.py` with the following content:

```python
import secrets
from datetime import datetime, timedelta, timezone
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import (
    create_access_token,
    get_current_user,
    hash_password,
    require_supervisor_or_admin,
)
from app.config import settings
from app.database import get_db
from app.email_service import send_invite_email
from app.limiter import limiter
from app.models import InviteStatus, TeamInvite, User, UserRole
from app.schemas import (
    DirectAddRequest,
    InviteAcceptRequest,
    InviteCreate,
    InviteOut,
    InviteValidateOut,
    UserOut,
)

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
):
    # Check for existing active invite
    result = await db.execute(
        select(TeamInvite).where(
            TeamInvite.email == payload.email,
            TeamInvite.status == InviteStatus.pending,
        )
    )
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="A pending invite already exists for this email")

    # Check email not already registered
    result = await db.execute(select(User).where(User.email == payload.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="User with this email is already registered")

    token = _generate_token()
    code = _generate_validation_code()
    expires_at = datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(hours=_INVITE_TTL_HOURS)

    invite = TeamInvite(
        email=payload.email,
        role=payload.role,
        token=token,
        validation_code=code,
        status=InviteStatus.pending,
        invited_by_id=current_user.id,
        expires_at=expires_at,
    )
    db.add(invite)
    await db.flush()
    await db.refresh(invite)

    await send_invite_email(
        to_email=payload.email,
        invited_by_name=current_user.full_name,
        role=payload.role.value,
        validation_code=code,
        token=token,
    )

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
            raise HTTPException(status_code=403, detail="Only admins can assign non-member roles")
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

    # Eagerly load invited_by name
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
    result = await db.execute(select(TeamInvite).where(TeamInvite.token == payload.token))
    invite = result.scalar_one_or_none()
    if not invite:
        raise HTTPException(status_code=404, detail="Invite not found")
    if invite.status != InviteStatus.pending:
        raise HTTPException(status_code=400, detail="Invite has already been used or cancelled")

    now = datetime.now(timezone.utc).replace(tzinfo=None)
    if now > invite.expires_at:
        invite.status = InviteStatus.expired
        await db.flush()
        raise HTTPException(status_code=400, detail="Invite has expired")

    if payload.validation_code != invite.validation_code:
        raise HTTPException(status_code=400, detail="Invalid validation code")

    # Check email not already registered
    result = await db.execute(select(User).where(User.email == invite.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="An account with this email already exists")

    # Check username not taken
    result = await db.execute(select(User).where(User.username == payload.username))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Username already taken")

    user = User(
        email=invite.email,
        username=payload.username,
        full_name=payload.full_name,
        hashed_password=hash_password(payload.password),
        role=invite.role,
        is_active=True,
    )
    db.add(user)

    invite.status = InviteStatus.accepted
    invite.accepted_at = now

    await db.flush()
    await db.refresh(user)

    # Auto-login: set auth cookie
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
        raise HTTPException(status_code=400, detail="Only pending invites can be cancelled")
    invite.status = InviteStatus.cancelled
    await db.flush()
```
</action>

<acceptance_criteria>
- File `backend/app/routers/invites.py` exists
- `backend/app/routers/invites.py` contains `async def send_invite(`
- `backend/app/routers/invites.py` contains `async def direct_add_member(`
- `backend/app/routers/invites.py` contains `async def validate_invite(`
- `backend/app/routers/invites.py` contains `async def accept_invite(`
- `backend/app/routers/invites.py` contains `async def list_pending_invites(`
- `backend/app/routers/invites.py` contains `async def cancel_invite(`
- `backend/app/routers/invites.py` contains `@limiter.limit("10/hour")` on `send_invite`
- `backend/app/routers/invites.py` contains `response.set_cookie(` in `accept_invite`
- `backend/app/routers/invites.py` contains `invite.status = InviteStatus.expired` on expiry check
</acceptance_criteria>
</task>

<task id="08-02-T3">
<title>Register invites router in main.py</title>
<type>execute</type>
<priority>blocking</priority>

<read_first>
- `backend/app/main.py` — existing router import pattern (line 15) and `app.include_router(...)` calls (lines 59-71)
</read_first>

<action>
1. In `backend/app/main.py`, update the router import line to include `invites`:
```python
from app.routers import ai, auth, chat, dashboard, invites, milestones, notifications, performance, projects, schedules, tasks, timeline, users, websocket as ws_router
```

2. Add `app.include_router(invites.router)` after the existing `app.include_router(users.router)` line:
```python
app.include_router(invites.router)
```
</action>

<acceptance_criteria>
- `backend/app/main.py` import line contains `invites`
- `backend/app/main.py` contains `app.include_router(invites.router)`
</acceptance_criteria>
</task>

<task id="08-02-T4">
<title>Update backend .env.example with email config fields</title>
<type>execute</type>
<priority>medium</priority>

<read_first>
- `backend/.env.example` — existing env var template format
</read_first>

<action>
Add the following block to `backend/.env.example` after the AI keys section:

```
# Email (SMTP) — leave blank to disable email sending in development
MAIL_USERNAME=
MAIL_PASSWORD=
MAIL_FROM=noreply@teamflow.app
MAIL_FROM_NAME=TeamFlow
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_STARTTLS=true
MAIL_SSL_TLS=false

# Frontend URL (for invite links)
FRONTEND_URL=http://localhost:5173
```
</action>

<acceptance_criteria>
- `backend/.env.example` contains `MAIL_USERNAME=`
- `backend/.env.example` contains `MAIL_SERVER=smtp.gmail.com`
- `backend/.env.example` contains `FRONTEND_URL=http://localhost:5173`
</acceptance_criteria>
</task>

---

## Verification

```bash
# Confirm email service
grep -n "async def send_invite_email" backend/app/email_service.py
grep -n "MAIL_USERNAME not configured" backend/app/email_service.py

# Confirm router endpoints
grep -n "async def " backend/app/routers/invites.py

# Confirm main.py registration
grep -n "invites" backend/app/main.py

# Confirm .env.example
grep -n "MAIL_USERNAME" backend/.env.example
grep -n "FRONTEND_URL" backend/.env.example

# Syntax check
cd backend && python -c "from app.routers import invites; print('OK')"
cd backend && python -c "from app.email_service import send_invite_email; print('OK')"
```
