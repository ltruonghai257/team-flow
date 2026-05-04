# Phase 8: User Invite & Team Management — Research

**Phase:** 8 — User Invite & Team Management
**Researched:** 2026-04-23

---

## RESEARCH COMPLETE

---

## 1. Email Sending: Library Decision

### Options Evaluated

| Library | Approach | Async | Fit |
|---------|----------|-------|-----|
| `fastapi-mail` | SMTP + template support, pydantic config | Yes (via aiosmtplib) | ✅ Best fit |
| `aiosmtplib` | Raw SMTP async | Yes | Needs manual templating |
| `sendgrid` / `resend` | HTTP API | Yes | Vendor lock-in, overkill |

**Decision: `fastapi-mail>=1.4.1`**

- Integrates with FastAPI's dependency injection
- Pydantic settings config (matches existing `Settings` pattern)
- `MessageSchema` + `FastMail` for sending
- Supports HTML templates via Jinja2
- Add `aiosmtplib>=3.0.0` as transitive dep (already pulled by fastapi-mail)

### Email Config additions to `backend/app/config.py`

```python
MAIL_USERNAME: str = ""
MAIL_PASSWORD: str = ""
MAIL_FROM: str = "noreply@teamflow.app"
MAIL_SERVER: str = "smtp.gmail.com"
MAIL_PORT: int = 587
MAIL_STARTTLS: bool = True
MAIL_SSL_TLS: bool = False
MAIL_FROM_NAME: str = "TeamFlow"
```

### Email Service pattern (`backend/app/email_service.py`)

```python
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from app.config import settings

conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_STARTTLS=settings.MAIL_STARTTLS,
    MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
    MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
    USE_CREDENTIALS=bool(settings.MAIL_USERNAME),
    VALIDATE_CERTS=True,
)

async def send_invite_email(to_email: str, invite_data: dict) -> None:
    message = MessageSchema(
        subject=f"You've been invited to join {invite_data['team_name']} on TeamFlow",
        recipients=[to_email],
        body=build_invite_html(invite_data),
        subtype=MessageType.html,
    )
    fm = FastMail(conf)
    await fm.send_message(message)
```

**Graceful degradation:** If `MAIL_USERNAME` is empty, skip sending (log warning). Allows dev usage without SMTP config.

---

## 2. Invite Token & Validation Code Strategy

### Token Generation

```python
import secrets

def generate_invite_token() -> str:
    return secrets.token_urlsafe(32)  # 43-char URL-safe string

def generate_validation_code() -> str:
    return str(secrets.randbelow(900000) + 100000)  # 6-digit numeric
```

- `secrets` module is stdlib — no new dependency
- Token stored in DB (hashed with SHA-256 for security, raw token sent in email)
- Actually: for simplicity matching existing auth pattern (no bcrypt overhead needed for short-lived tokens), store token **plaintext** — acceptable since tokens expire in 72h and are single-use

### TokenStatus enum

```python
class InviteStatus(str, enum.Enum):
    pending = "pending"
    accepted = "accepted"
    expired = "expired"
    cancelled = "cancelled"
```

### Expiry check

```python
from datetime import datetime, timezone, timedelta

INVITE_TTL_HOURS = 72

def is_invite_expired(invite: TeamInvite) -> bool:
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    return now > invite.expires_at
```

---

## 3. Database Model: `TeamInvite`

New table `team_invites`:

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

### Alembic Migration

Since `alembic upgrade head` runs at startup (lifespan in `main.py`), adding `TeamInvite` to `models.py` and generating a new migration is the correct path:

```bash
cd backend
alembic revision --autogenerate -m "add team_invites table"
# Review generated file in alembic/versions/
alembic upgrade head
```

The `env.py` already imports `app.models` ensuring all models are in `Base.metadata`.

---

## 4. Backend API Routes

### Router: `backend/app/routers/invites.py`

Following existing router pattern (prefix + APIRouter):

```
POST /api/teams/invite          — send email invite (supervisor/admin)
POST /api/teams/add             — direct-add existing user to team (supervisor/admin)
GET  /api/invites/validate      — validate token, return metadata (public)
POST /api/invites/accept        — accept invite with token + code (public)
GET  /api/invites/pending       — list pending invites (supervisor/admin)
DELETE /api/invites/{invite_id} — cancel pending invite (supervisor/admin)
```

### Auth guard: `require_supervisor_or_admin`

Add to `backend/app/auth.py`:

```python
async def require_supervisor_or_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role not in (UserRole.admin, UserRole.supervisor):
        raise HTTPException(status_code=403, detail="Supervisor or admin access required")
    return current_user
```

Note: `require_supervisor` already exists and does the same check. Rename/alias it for semantic clarity or reuse existing.

### Accept flow (public endpoint, no auth required)

```
POST /api/invites/accept
Body: { token: str, validation_code: str, username: str, full_name: str, password: str }
Response: UserOut + sets access_token cookie (auto-login after accept)
```

Logic:
1. Look up invite by token
2. Check status == pending, not expired
3. Verify validation_code matches
4. Check no existing user with that email
5. Create User with invite.email, invite.role
6. Mark invite as accepted, set accepted_at
7. Return user + set auth cookie (mirrors `/api/auth/token` cookie pattern)

### Direct-add flow (`POST /api/teams/add`)

```
Body: { user_id: int, role?: UserRole }
```

Simply looks up existing user, optionally updates role. Returns UserOut.

---

## 5. Alembic Migration — `InviteStatus` enum

PostgreSQL requires CREATE TYPE for enums. The `--autogenerate` will produce:

```sql
CREATE TYPE invitestatus AS ENUM ('pending', 'accepted', 'expired', 'cancelled');
CREATE TABLE team_invites (...);
```

This is handled automatically by Alembic when `InviteStatus` is a Python `enum.Enum` used in SQLAlchemy `Enum()`.

---

## 6. Frontend: SvelteKit Routes & Components

### New routes

```
frontend/src/routes/invite/accept/+page.svelte   — public invite acceptance page
```

### Auth guard bypass

`+layout.svelte` currently redirects unauthenticated users to `/login`. The `/invite/accept` route must be **excluded** from that guard:

```typescript
// In +layout.svelte onMount / reactive redirect:
const PUBLIC_PATHS = ['/login', '/register', '/invite/accept'];
if (!$isLoggedIn && !PUBLIC_PATHS.some(p => path.startsWith(p))) {
    goto('/login');
}
```

### Invite acceptance page flow

1. On mount: read `?token=` from URL, call `GET /api/invites/validate?token=…`
2. Display invite metadata (invited by, team, role)
3. Form: validation code (6-digit), username, full name, password
4. Submit: `POST /api/invites/accept` → on success, redirect to `/`
5. Error states: expired token, invalid code, email already registered

### Team page enhancements (`frontend/src/routes/team/+page.svelte`)

Add supervisor/admin conditional UI:
- "Invite Member" button → modal (email input + role selector)
- "Add Member" button → modal (search existing users + role)
- Pending invites table (shows email, role, invited by, expires at, cancel button)

### Auth store

`$isSupervisor` already exists in `frontend/src/lib/stores/auth.ts`. Use for conditional UI rendering.

---

## 7. Rate Limiting

Invite endpoints should be rate-limited to prevent abuse:

```python
@router.post("/api/teams/invite")
@limiter.limit("10/hour")
async def send_invite(request: Request, ...):
```

`limiter` imported from `app.limiter` (existing pattern in `auth.py`).

---

## 8. Email Template (HTML)

Inline HTML string in `email_service.py` (no Jinja2 template files needed for simplicity):

```
Subject: You've been invited to join TeamFlow
Body:
- Team name, sender name
- 6-digit validation code (large, prominent)
- Accept link: https://{FRONTEND_URL}/invite/accept?token={token}
- Expiry note: "This invite expires in 72 hours"
```

Add `FRONTEND_URL` to config (default `http://localhost:5173` for dev).

---

## 9. Validation Architecture

### Unit testable components

- `generate_invite_token()` — pure function, deterministic length
- `generate_validation_code()` — pure function, 6-digit range
- `is_invite_expired()` — pure function, datetime comparison
- Invite accept endpoint — test with mock DB: valid token+code → creates user; expired → 400; wrong code → 400

### Integration points

- `POST /api/teams/invite` → verify email sent (mock FastMail in tests)
- `POST /api/invites/accept` → verify user created + cookie set
- `GET /api/invites/validate` → verify token lookup and metadata return

### Frontend acceptance page

- Snapshot/e2e: page loads with valid token, form renders, submit redirects to `/`

---

## 10. Key Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Email library | `fastapi-mail` | Async, pydantic config, minimal setup |
| Token storage | Plaintext in DB | Short-lived (72h), single-use, simpler than hashing |
| Validation code | 6-digit numeric via `secrets` | UX: easy to type from email |
| Accept endpoint auth | Public (no JWT) | New users don't have accounts yet |
| Auto-login after accept | Yes (set cookie) | Better UX, mirrors login flow |
| "Add member" scope | Update existing user role only | No new user creation — just association |
| Invite status tracking | `InviteStatus` enum in DB | Auditable, prevents replay attacks |
| Rate limiting | 10/hour on invite endpoint | Prevents spam, consistent with existing pattern |
| Frontend public path | `/invite/accept` excluded from auth guard | Invitation recipients aren't logged in |
