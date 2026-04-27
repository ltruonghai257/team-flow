# Backend Package Restructure — Phase 20 Migration Guide

**Phase:** 20-backend-package-restructure  
**Date:** 2026-04-27  
**Status:** Complete (Phase 22 runtime/Docker/Azure verification pending)

---

## Overview

Phase 20 reorganised `backend/app` into an Open WebUI-inspired group layout.
All old import paths remain working through compatibility delegates until Phase 22
runtime/Docker/Azure verification confirms they are safe to remove.

---

## Old-to-New Path Map

### Runtime-adjacent modules

| Old path | New canonical path | Risk | Remove in |
|---|---|---|---|
| `app.config` | `app.core.config` | HIGH | Phase 22 |
| `app.limiter` | `app.core.limiter` | LOW | Phase 22 |
| `app.database` | `app.db.database` | HIGH | Phase 22 |
| `app.scheduler_jobs` | `app.internal.scheduler_jobs` | MEDIUM | Phase 22 |
| `app.auth` | `app.utils.auth` | HIGH | Phase 22 |
| `app.ai_client` | `app.utils.ai_client` | LOW | Phase 22 |
| `app.email_service` | `app.utils.email_service` | LOW | Phase 22 |
| `app.websocket.manager` | `app.socket.manager` | HIGH | Phase 22 |

### App factory

| Old path | New canonical path | Risk | Notes |
|---|---|---|---|
| `app.main:app` | `app.api.main:app` | HIGH | uvicorn/Docker/supervisord keep `app.main:app` |
| — | `app.api.main:create_app` | — | New factory for testability |

### Model package

| Old path | New canonical path | Notes |
|---|---|---|
| `app.models.User` | `app.models.users.User` | `app.models` re-exports all |
| `app.models.SubTeam` | `app.models.users.SubTeam` | |
| `app.models.TeamInvite` | `app.models.users.TeamInvite` | |
| `app.models.KPIWeightSettings` | `app.models.users.KPIWeightSettings` | |
| `app.models.Project` | `app.models.work.Project` | |
| `app.models.Milestone` | `app.models.work.Milestone` | |
| `app.models.Sprint` | `app.models.work.Sprint` | |
| `app.models.StatusSet` | `app.models.work.StatusSet` | |
| `app.models.CustomStatus` | `app.models.work.CustomStatus` | |
| `app.models.StatusTransition` | `app.models.work.StatusTransition` | |
| `app.models.Task` | `app.models.work.Task` | |
| `app.models.Schedule` | `app.models.work.Schedule` | |
| `app.models.EventNotification` | `app.models.notifications.EventNotification` | |
| `app.models.SubTeamReminderSettings` | `app.models.notifications.SubTeamReminderSettings` | |
| `app.models.ReminderSettingsProposal` | `app.models.notifications.ReminderSettingsProposal` | |
| `app.models.ChatChannel` | `app.models.communication.ChatChannel` | |
| `app.models.ChatChannelMember` | `app.models.communication.ChatChannelMember` | |
| `app.models.ChatConversation` | `app.models.communication.ChatConversation` | |
| `app.models.ChatMessage` | `app.models.communication.ChatMessage` | |
| `app.models.UserPresence` | `app.models.communication.UserPresence` | |
| `app.models.AIConversation` | `app.models.ai.AIConversation` | |
| `app.models.AIMessage` | `app.models.ai.AIMessage` | |
| All enums | `app.models.enums.*` | `app.models` re-exports all enums |

### Schema package

| Old path | New canonical path | Notes |
|---|---|---|
| `app.schemas.Token` / `TokenData` | `app.schemas.auth.*` | |
| `app.schemas.UserOut` etc. | `app.schemas.users.*` | |
| `app.schemas.TaskOut` etc. | `app.schemas.work.*` | _to_naive_utc helper lives here |
| `app.schemas.NotificationOut` etc. | `app.schemas.notifications.*` | |
| `app.schemas.ChatMessageOut` etc. | `app.schemas.communication.*` | |
| `app.schemas.AIConversationOut` etc. | `app.schemas.ai.*` | |
| `app.schemas.TeamMemberPerformance` etc. | `app.schemas.performance.*` | |
| `app.schemas.SubTeamOut` etc. | `app.schemas.teams.*` | |
| `app.schemas.KPIOverviewResponse` etc. | `app.schemas.kpi.*` | |

---

## Compatibility Shims

All old-path modules are now single-import delegates. They re-export from the
canonical module and contain a comment identifying them as Phase 20 shims.

**HIGH-RISK shims (keep through Phase 22):**
- `app.main` — uvicorn/Docker/supervisord target: `uvicorn app.main:app`
- `app.models` — Alembic, all tests, all routers use `from app.models import ...`
- `app.schemas` — all routers use `from app.schemas import ...`
- `app.config` — Alembic env.py now uses canonical, but other external tooling may not
- `app.database` — external tooling may use Base/engine from this path
- `app.auth` / `app.websocket.manager` — used by tests and websocket router

**LOW-RISK shims (can remove after Phase 22 smoke):**
- `app.limiter`, `app.ai_client`, `app.email_service`, `app.scheduler_jobs`

---

## Verification Commands

```bash
# Compile check
cd backend && uv run python -m compileall app -q

# Package structure + import identity tests
cd backend && uv run python -m pytest tests/test_package_structure.py -v

# Full backend unit test suite
cd backend && uv run python -m pytest tests/ -v

# App factory smoke (requires env/DB)
cd backend && uv run python -c "
from app.api.main import app, create_app
from app.main import app as compat_app
assert app is compat_app
assert callable(create_app)
routes = {getattr(r, 'path', '') for r in app.routes}
assert '/health' in routes
assert '/ws/chat' in routes
print('app factory OK')
"

# Identity assertions for runtime-adjacent modules
cd backend && uv run python -c "
from app.core.config import settings; from app.config import settings as old
from app.socket.manager import manager; from app.websocket.manager import manager as old_mgr
assert settings is old; assert manager is old_mgr
print('identity OK')
"
```

---

## Alembic

`backend/alembic/env.py` now imports from canonical paths:
- `from app.core.config import settings`
- `from app.db.database import Base`
- `import app.models` (triggers all domain model registration)

No migration history was changed.

---

## Phase 22 Handoff

Phase 22 (Runtime Integration & Regression Verification) should:
1. Run the full backend test suite and E2E smoke against the restructured package.
2. Verify `uvicorn app.main:app` starts and `/health` responds.
3. Verify Docker image builds and container starts cleanly.
4. Remove LOW-RISK shims if verification passes.
5. Decide on HIGH-RISK shim removal timeline based on runtime confidence.

Relevant shim comments in source files: `# Phase 20 compatibility delegate — canonical path: ...`
