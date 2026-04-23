---
id: 08-01
wave: 1
title: TeamInvite Model, Migration & Auth Guard
depends_on: []
files_modified:
  - backend/app/models.py
  - backend/app/auth.py
  - backend/app/config.py
  - backend/app/schemas.py
  - backend/requirements.txt
  - backend/alembic/versions/<new_migration>.py
autonomous: true
requirements:
  - REQ-08
---

# Plan 08-01: TeamInvite Model, Migration & Auth Guard

## Goal

Add the `TeamInvite` ORM model and `InviteStatus` enum to `models.py`, generate the Alembic migration, add email config fields to `config.py`, add `require_supervisor_or_admin` to `auth.py`, and add `fastapi-mail` to `requirements.txt`. This is the foundational data layer that all invite endpoints depend on.

## must_haves

- `TeamInvite` model with all fields exists in `models.py`
- `InviteStatus` enum defined in `models.py`
- Alembic migration file created and applies cleanly (`alembic upgrade head` succeeds)
- `require_supervisor_or_admin` dependency exists in `auth.py`
- Email config fields added to `config.py` `Settings` class
- `fastapi-mail>=1.4.1` in `requirements.txt`
- All invite schemas (`InviteCreate`, `InviteOut`, `InviteValidateOut`, `InviteAcceptRequest`) in `schemas.py`

---

## Tasks

<task id="08-01-T1">
<title>Add InviteStatus enum and TeamInvite model to models.py</title>
<type>execute</type>
<priority>blocking</priority>

<read_first>
- `backend/app/models.py` — see existing enum pattern (UserRole, TaskStatus, MilestoneStatus), existing Column/relationship patterns, datetime default pattern
- `backend/app/database.py` — Base import
</read_first>

<action>
Add the following to `backend/app/models.py` immediately after the `NotificationEventType` enum class (around line 57) and before the `User` class:

1. Add `InviteStatus` enum:
```python
class InviteStatus(str, enum.Enum):
    pending = "pending"
    accepted = "accepted"
    expired = "expired"
    cancelled = "cancelled"
```

2. Add `TeamInvite` model at the END of the file (after all existing models):
```python
class TeamInvite(Base):
    __tablename__ = "team_invites"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, nullable=False, index=True)
    role = Column(Enum(UserRole), default=UserRole.member)
    token = Column(String, unique=True, nullable=False, index=True)
    validation_code = Column(String, nullable=False)
    status = Column(Enum(InviteStatus), default=InviteStatus.pending, index=True)
    invited_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    accepted_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))

    invited_by = relationship("User", foreign_keys=[invited_by_id])
```
</action>

<acceptance_criteria>
- `backend/app/models.py` contains `class InviteStatus(str, enum.Enum):` with values `pending`, `accepted`, `expired`, `cancelled`
- `backend/app/models.py` contains `class TeamInvite(Base):` with `__tablename__ = "team_invites"`
- `backend/app/models.py` contains `token = Column(String, unique=True, nullable=False, index=True)`
- `backend/app/models.py` contains `validation_code = Column(String, nullable=False)`
- `backend/app/models.py` contains `expires_at = Column(DateTime, nullable=False)`
- `backend/app/models.py` contains `invited_by = relationship("User", foreign_keys=[invited_by_id])`
</acceptance_criteria>
</task>

<task id="08-01-T2">
<title>Add fastapi-mail to requirements.txt</title>
<type>execute</type>
<priority>blocking</priority>

<read_first>
- `backend/requirements.txt` — see existing format (package>=version, one per line)
</read_first>

<action>
Add the following line to `backend/requirements.txt`:
```
fastapi-mail>=1.4.1
```
</action>

<acceptance_criteria>
- `backend/requirements.txt` contains `fastapi-mail>=1.4.1`
</acceptance_criteria>
</task>

<task id="08-01-T3">
<title>Add email config fields to config.py Settings</title>
<type>execute</type>
<priority>blocking</priority>

<read_first>
- `backend/app/config.py` — see existing Settings class fields, pydantic-settings pattern
</read_first>

<action>
Add the following fields to the `Settings` class in `backend/app/config.py`, after the `ANTHROPIC_API_KEY` field:

```python
    MAIL_USERNAME: str = ""
    MAIL_PASSWORD: str = ""
    MAIL_FROM: str = "noreply@teamflow.app"
    MAIL_FROM_NAME: str = "TeamFlow"
    MAIL_SERVER: str = "smtp.gmail.com"
    MAIL_PORT: int = 587
    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False
    FRONTEND_URL: str = "http://localhost:5173"
```
</action>

<acceptance_criteria>
- `backend/app/config.py` contains `MAIL_USERNAME: str = ""`
- `backend/app/config.py` contains `MAIL_PASSWORD: str = ""`
- `backend/app/config.py` contains `MAIL_FROM: str = "noreply@teamflow.app"`
- `backend/app/config.py` contains `MAIL_SERVER: str = "smtp.gmail.com"`
- `backend/app/config.py` contains `FRONTEND_URL: str = "http://localhost:5173"`
</acceptance_criteria>
</task>

<task id="08-01-T4">
<title>Add require_supervisor_or_admin dependency to auth.py</title>
<type>execute</type>
<priority>blocking</priority>

<read_first>
- `backend/app/auth.py` — see existing `require_supervisor` (lines 63-66) and `require_admin` (lines 69-72) dependency patterns
</read_first>

<action>
Add the following function to `backend/app/auth.py` immediately after the existing `require_admin` function (after line 72):

```python
async def require_supervisor_or_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role not in (UserRole.admin, UserRole.supervisor):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Supervisor or admin access required")
    return current_user
```
</action>

<acceptance_criteria>
- `backend/app/auth.py` contains `async def require_supervisor_or_admin(`
- `backend/app/auth.py` contains `detail="Supervisor or admin access required"`
</acceptance_criteria>
</task>

<task id="08-01-T5">
<title>Add invite schemas to schemas.py</title>
<type>execute</type>
<priority>blocking</priority>

<read_first>
- `backend/app/schemas.py` — see end of file, existing schema patterns (BaseModel, Optional, EmailStr)
- `backend/app/models.py` — `InviteStatus`, `UserRole` enums (just added)
</read_first>

<action>
1. In `backend/app/schemas.py`, update the import line for models to include `InviteStatus`:
```python
from app.models import InviteStatus, MilestoneStatus, NotificationEventType, NotificationStatus, TaskPriority, TaskStatus, UserRole
```

2. Add the following schemas at the END of `backend/app/schemas.py`:

```python
# ── Invites ───────────────────────────────────────────────────────────────────

class InviteCreate(BaseModel):
    email: EmailStr
    role: UserRole = UserRole.member


class InviteOut(BaseModel):
    id: int
    email: str
    role: str
    status: InviteStatus
    invited_by_id: int
    expires_at: datetime
    accepted_at: Optional[datetime]
    created_at: datetime

    model_config = {"from_attributes": True}


class InviteValidateOut(BaseModel):
    id: int
    email: str
    role: str
    invited_by_name: str
    expires_at: datetime
    valid: bool


class InviteAcceptRequest(BaseModel):
    token: str
    validation_code: str
    username: str
    full_name: str
    password: str


class DirectAddRequest(BaseModel):
    user_id: int
    role: Optional[UserRole] = None
```
</action>

<acceptance_criteria>
- `backend/app/schemas.py` contains `class InviteCreate(BaseModel):`
- `backend/app/schemas.py` contains `class InviteOut(BaseModel):`
- `backend/app/schemas.py` contains `class InviteValidateOut(BaseModel):`
- `backend/app/schemas.py` contains `class InviteAcceptRequest(BaseModel):`
- `backend/app/schemas.py` contains `class DirectAddRequest(BaseModel):`
- `backend/app/schemas.py` import line contains `InviteStatus`
</acceptance_criteria>
</task>

<task id="08-01-T6">
<title>Generate Alembic migration for team_invites table</title>
<type>execute</type>
<priority>blocking</priority>
<autonomous>false</autonomous>

<read_first>
- `backend/alembic/env.py` — confirms `import app.models` ensures all models in Base.metadata
- `backend/alembic/versions/` — existing migration files for naming convention
- `backend/app/models.py` — TeamInvite model (just added)
</read_first>

<action>
Run the following command from the `backend/` directory to generate the migration:

```bash
cd backend && alembic revision --autogenerate -m "add_team_invites_table"
```

This produces a new file in `backend/alembic/versions/`. Review the generated migration to confirm:
- `op.create_table('team_invites', ...)` is present
- The `invitestatus` PostgreSQL enum type is created: `sa.Enum('pending', 'accepted', 'expired', 'cancelled', name='invitestatus')`
- `downgrade()` drops the table and the type

If `invitestatus` enum conflicts with existing DB types, the migration may need `checkfirst=True` on the enum create. Review and adjust if necessary.
</action>

<acceptance_criteria>
- A new file exists in `backend/alembic/versions/` with `_add_team_invites_table` in its name
- That file contains `op.create_table('team_invites'`
- That file contains `'invitestatus'` or `InviteStatus` enum reference
- Running `alembic upgrade head` from `backend/` exits 0
</acceptance_criteria>
</task>

---

## Verification

```bash
# Confirm model additions
grep -n "class InviteStatus" backend/app/models.py
grep -n "class TeamInvite" backend/app/models.py
grep -n "team_invites" backend/app/models.py

# Confirm auth guard
grep -n "require_supervisor_or_admin" backend/app/auth.py

# Confirm config fields
grep -n "MAIL_USERNAME" backend/app/config.py
grep -n "FRONTEND_URL" backend/app/config.py

# Confirm schemas
grep -n "class InviteCreate" backend/app/schemas.py
grep -n "class InviteAcceptRequest" backend/app/schemas.py

# Confirm dependency
grep -n "fastapi-mail" backend/requirements.txt

# Confirm migration file exists
ls backend/alembic/versions/ | grep team_invites
```
