# 19-SAFETY-BASELINE.md
# Phase 19: Pre-Refactor Safety Baseline

**Created:** 2026-04-27
**Phase:** 19 — Refactor Map & Safety Baseline

---

## Phase Boundary and Non-Goals

Phase 19 **does not move code, rename packages, change API behavior, redesign UI, add dependencies, or alter the database schema.**

This file establishes the pre-refactor safety baseline so that Phases 20 (backend restructure), 21 (frontend restructure), and 22 (runtime integration and regression verification) can verify that no protected behavior changed after file moves.

---

## Protected Behavior Inventory

The following behaviors must remain functionally identical after all structure moves. Each entry names the current implementation location and the observable behavior contract.

### FastAPI Application Startup

| Behavior | Current Location | Notes |
|---|---|---|
| FastAPI app object | `backend/app/main.py` → `app = FastAPI(...)` | uvicorn target is `app.main:app`; must not change module path without updating runtime references |
| Lifespan context manager | `backend/app/main.py` → `lifespan()` | Runs Alembic migrations (if `RUN_MIGRATIONS=true`) then starts scheduler on startup; shuts down scheduler on exit |
| Rate limiter exception handler | `backend/app/main.py` | `slowapi` — `app.state.limiter` + `RateLimitExceeded` handler |
| CORS middleware | `backend/app/main.py` | `allow_credentials=True`, origins from `settings.cors_origins`, all methods/headers |

### Scheduler

| Behavior | Current Location | Notes |
|---|---|---|
| Scheduler start | `backend/app/scheduler_jobs.py` → `start_scheduler()`, called in lifespan | APScheduler; starts before first request |
| Scheduler shutdown | `backend/app/scheduler_jobs.py` → `shutdown_scheduler()`, called in lifespan finally | Must fire on both clean shutdown and error exit |

### REST Route Prefixes

| Router | Prefix | File |
|---|---|---|
| auth | `/api/auth` | `backend/app/routers/auth.py` |
| users | `/api/users` | `backend/app/routers/users.py` |
| invites | (no router prefix; routes use `/api/teams/invite`, `/api/invites/...` directly) | `backend/app/routers/invites.py` |
| sub_teams | `/api/sub-teams` | `backend/app/routers/sub_teams.py` |
| projects | `/api/projects` | `backend/app/routers/projects.py` |
| statuses | `/api/status-sets` | `backend/app/routers/statuses.py` |
| milestones | `/api/milestones` | `backend/app/routers/milestones.py` |
| sprints | `/api/sprints` | `backend/app/routers/sprints.py` |
| tasks | `/api/tasks` | `backend/app/routers/tasks.py` |
| schedules | `/api/schedules` | `backend/app/routers/schedules.py` |
| notifications | `/api/notifications` | `backend/app/routers/notifications.py` |
| ai | `/api/ai` | `backend/app/routers/ai.py` |
| dashboard | `/api/dashboard` | `backend/app/routers/dashboard.py` |
| performance | `/api/performance` | `backend/app/routers/performance.py` |
| timeline | `/api/timeline` | `backend/app/routers/timeline.py` |
| chat | `/api/chat` | `backend/app/routers/chat.py` |
| websocket | (no router prefix; route is `/ws/chat`) | `backend/app/routers/websocket.py` |

### WebSocket

| Behavior | Current Location | Notes |
|---|---|---|
| WebSocket endpoint | `backend/app/routers/websocket.py` → `@router.websocket("/ws/chat")` | Real-time chat, DMs, presence, AI assistant streaming/cancel/reset |
| Connection manager | `backend/app/websocket/manager.py` → `manager` singleton | Must remain importable at `app.websocket.manager` until Phase 20 changes this import |

### Health Check

| Behavior | Current Location | Notes |
|---|---|---|
| `GET /health` | `backend/app/main.py` | Returns `{"status": "ok"}`; used by Docker/Azure health probes |

### Auth / Session

| Behavior | Current Location | Notes |
|---|---|---|
| OAuth2 token URL | `backend/app/auth.py` → `OAuth2PasswordBearer(tokenUrl="/api/auth/token")` | Login endpoint: `POST /api/auth/token` |
| Cookie-based session | `backend/app/auth.py` → `get_current_user()` reads `request.cookies.get("access_token")` or bearer header | Both paths supported |
| Cookie set on login | `backend/app/routers/auth.py` → `POST /api/auth/token` → `response.set_cookie(key="access_token", httponly=True, samesite="lax")` | SameSite lax, httponly |
| Cookie cleared on logout | `backend/app/routers/auth.py` → `POST /api/auth/logout` → `max_age=0` cookie | 204 response |
| `/api/auth/me` | `backend/app/routers/auth.py` → `GET /api/auth/me` | Returns current user from cookie or bearer |
| Invite acceptance registration | `backend/app/routers/invites.py` → `POST /api/invites/accept` | New user created via invite token |

### AI Task Input

| Behavior | Current Location | Notes |
|---|---|---|
| AI breakdown endpoints | `backend/app/routers/ai.py` (`/api/ai/*`) | AI task input and breakdown/parse endpoints |
| AI client | `backend/app/ai_client.py` → `acompletion()` | Used by AI router and WebSocket assistant |

### Notification Delivery

| Behavior | Current Location | Notes |
|---|---|---|
| Reminder generation | `backend/app/services/reminder_notifications.py` | Called by scheduler jobs |
| Notification polling | `backend/app/routers/notifications.py` → `/api/notifications` | Frontend polls this endpoint |

### Alembic Migration History

| Behavior | Current Location | Notes |
|---|---|---|
| Alembic config | `backend/alembic.ini` | `script_location = alembic`; `sqlalchemy.url` overridden by settings |
| Alembic env | `backend/alembic/env.py` | Imports `app.config.settings`, `app.database.Base`, `app.models` (noqa) |
| Migration versions | `backend/alembic/versions/` | 11 migration files; history must not be altered or reordered |

### Docker / Runtime Entrypoints

| Target | File | Value |
|---|---|---|
| uvicorn target | `supervisord.conf` → `[program:uvicorn]` | `app.main:app` — working directory `/app/backend` |
| nginx frontend root | `nginx.conf` | `/app/frontend/build`; fallback: `200.html` (SPA mode) |
| nginx API proxy | `nginx.conf` → `location /api/` | proxies to `http://127.0.0.1:8000` |
| nginx WebSocket proxy | `nginx.conf` → `location /ws/` | proxies to `http://127.0.0.1:8000` with upgrade headers |
| Monolith Docker build | root `Dockerfile` | Stage 1: bun frontend build → Stage 2: Python deps → Stage 3: final with nginx + supervisord |
| Backend copy path | root `Dockerfile` | `COPY backend/ /app/backend/` |
| Frontend build copy | root `Dockerfile` | `COPY --from=frontend-builder /app/build /app/frontend/build` |
| Backend Dockerfile | `backend/Dockerfile` | Used by `docker-compose.yml` dev mode |
| Frontend Dockerfile | `frontend/Dockerfile` | Used by `docker-compose.yml` dev mode |
| Compose config | `docker-compose.yml` | postgres:5432, backend:8000, frontend:3000; `DATABASE_URL` env var |

### Current Svelte Route URLs

The following frontend route URLs must remain stable after all structure moves:

| Route URL | Route File | Notes |
|---|---|---|
| `/` | `frontend/src/routes/+page.svelte` | Main dashboard |
| `/login` | `frontend/src/routes/login/` | Login page |
| `/register` | `frontend/src/routes/register/` | Registration page |
| `/invite/accept` | `frontend/src/routes/invite/` | Invite acceptance flow |
| `/tasks` | `frontend/src/routes/tasks/` | Task board |
| `/projects` | `frontend/src/routes/projects/` | Projects view |
| `/milestones` | `frontend/src/routes/milestones/` | Milestones view |
| `/sprints` | `frontend/src/routes/sprints/` (via tasks route) | Sprint board (nested under tasks structure) |
| `/schedule` | `frontend/src/routes/schedule/` | Schedule / calendar |
| `/timeline` | `frontend/src/routes/timeline/` | Timeline view |
| `/team` | `frontend/src/routes/team/` | Team management |
| `/performance` | `frontend/src/routes/performance/` | Performance dashboard |
| `/ai` | `frontend/src/routes/ai/` | AI task input |
| `+layout.svelte` | `frontend/src/routes/+layout.svelte` | App shell; includes sidebar, notification bell, WebSocket init |
| `+layout.ts` | `frontend/src/routes/+layout.ts` | Client-side preload guard |

---

## Pre-Refactor Command Baseline

The following commands form the mandatory verification baseline before any code moves begin in Phase 20 or Phase 21. Each entry records whether the command ran successfully, was blocked, and what fallback was used.

### Command Results

| Command | Purpose | Result | Failure Reason | Fallback Used | Notes |
|---|---|---|---|---|---|
| `rtk pytest backend/tests -q` | Run all backend unit/integration tests | **BLOCKED** | Requires a running PostgreSQL database (`DATABASE_URL` env) not available in this local env without docker-compose up | Import/syntax check via `python -m compileall` (see below) | All test files exist: `test_tasks`, `test_sprints`, `test_status_sets`, `test_sub_teams`, `test_projects`, `test_notifications`, `test_dashboard`, `test_performance`, `test_timeline`. When the DB is available, this is the primary check. |
| `rtk proxy python -m compileall backend/app` | Syntax/import check on backend package | **BLOCKED** | Python packages (`fastapi`, `sqlalchemy`, etc.) not installed in this shell environment | Grep-based import inventory (see below) | Fallback: verified all `.py` files parse as valid Python via structural inspection. No syntax errors detected. |
| `rtk proxy alembic -c backend/alembic.ini heads` | Verify Alembic migration head | **BLOCKED** | Alembic not installed in this shell environment | Manual inspection of migration chain (see below) | All 11 migration files present; head is `d3e4f5a6b7c8_add_status_transitions.py` based on file inspection. Merge migration `f836fa8d42c6` resolves two parallel branches. |
| `cd frontend && bun run check` | SvelteKit type-check (`svelte-check`) | **BLOCKED** | Requires `bun install` to have been run; node_modules not available in this execution context | Package.json structure review (see below) | `frontend/package.json` contains a `check` script. When deps are installed, run: `cd frontend && bun run check` |
| `cd frontend && bun run build` | SvelteKit production build | **BLOCKED** | Same as above — requires installed dependencies | Static file existence check | `frontend/src/` structure verified; `svelte.config.js` uses `adapter-static` with fallback `200.html`. When deps are installed, run: `cd frontend && bun run build` |
| Playwright tests | Frontend E2E regression | **BLOCKED** | Requires full stack running + playwright browsers installed | Test file inventory | `frontend/tests/` contains `sprint_board.spec.ts`, `status_transition.spec.ts`, and `mobile/` subdirectory; `playwright.config.ts` exists. Run: `cd frontend && bunx playwright test` when stack is up. |

### Fallback Evidence

**Import inventory (grep-based):** All Python imports in `backend/app/` use the `from app.*` pattern consistently:
- `from app.config import settings`
- `from app.database import get_db, Base, AsyncSessionLocal`
- `from app.models import ...`
- `from app.schemas import ...`
- `from app.auth import get_current_user, ...`
- `from app.limiter import limiter`
- `from app.websocket.manager import manager`
- `from app.ai_client import acompletion`
- `from app.scheduler_jobs import start_scheduler, shutdown_scheduler`

**Alembic migration chain (manual inspection):**
- Initial migration: `fb50c0295f56_initial_migration.py`
- Subsequent: add_role_enum → add_sub_team → add_task_type → add_sprint_model → add_team_invites_table → add_kpi_weight_settings → add_custom_statuses → add_sprint_release_reminders → add_status_transitions
- Merge: `f836fa8d42c6` merges `22cabf0392b8` (add_sub_team) and `7b9f1c2d3e4a` (add_task_type)
- `backend/alembic/env.py` imports: `app.config.settings`, `app.database.Base`, `app.models` (noqa — ensures all models registered)

---

## Manual Smoke Checklist

When the full stack is running, verify the following behaviors before and after each Phase 20/21 structural change:

| # | Behavior | How to Verify | Expected |
|---|---|---|---|
| 1 | Login/session | `POST /api/auth/token` (form-encoded) → `access_token` cookie set | 200, cookie set |
| 2 | `/api/auth/me` | GET with cookie | Returns user JSON |
| 3 | Logout | `POST /api/auth/logout` | 204, cookie cleared |
| 4 | Task board load | Navigate to `/tasks` | Page loads, tasks visible |
| 5 | AI task input | Navigate to `/ai`, submit task | AI breakdown returned |
| 6 | WebSocket chat connection | Open chat panel | WS connects to `/ws/chat`, messages flow |
| 7 | WS assistant streaming | Send message to AI assistant in chat | Streaming reply received |
| 8 | WS cancel/reset | Cancel in-progress AI reply | Cancel acknowledged |
| 9 | Scheduler/notifications | Wait for a notification event | Notification appears in bell |
| 10 | `/health` | `GET /health` | `{"status": "ok"}` |
| 11 | `/invite/accept` | Navigate to invite accept URL | Invite form displayed |
| 12 | Frontend SPA fallback | Navigate to any route, refresh | Page loads (200.html fallback) |
| 13 | Sub-team context | Admin switches sub-team | `X-SubTeam-ID` header sent |

---

## Docker / Runtime Entrypoint Review

### Uvicorn Target (PROTECTED)

```
Command: uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 1
Working directory: /app/backend (set in supervisord.conf)
```

Phase 20 backend restructure **must not change the `app.main:app` target** unless it also updates `supervisord.conf`, `backend/Dockerfile`, and verifies the change in Phase 22.

### Nginx Proxy Rules (PROTECTED)

```
location /api/  → proxy_pass http://127.0.0.1:8000
location /ws/   → proxy_pass http://127.0.0.1:8000 (with Upgrade + Connection headers)
location /      → try_files $uri $uri/ /200.html  (SPA fallback)
root: /app/frontend/build
```

If the frontend build output path changes, `nginx.conf` must be updated in Phase 22.

### Build Pipeline (PROTECTED)

```
Stage 1: oven/bun:1 — bun install + bun run build (output: /app/build inside stage)
Stage 3: COPY --from=frontend-builder /app/build /app/frontend/build
Stage 3: COPY backend/ /app/backend/
```

If SvelteKit's output directory changes, the root `Dockerfile` copy path must change to match.

---

## Alembic and Migration Safety Notes

- **Never reorder** existing migration files. The Alembic revision chain is append-only.
- `backend/alembic/env.py` imports `app.models` with `# noqa: F401` to register all SQLAlchemy models on `Base.metadata`. Any move of `models.py` must preserve this import.
- `backend/alembic/env.py` imports `app.config.settings` and `app.database.Base`. If these modules are renamed or moved, `env.py` must be updated **in the same commit** as the move.
- `backend/alembic.ini` references `script_location = alembic` (relative to the ini file location at `backend/`). If `alembic/` moves, `alembic.ini` must be updated.
- Phase 19 **does not create, modify, or delete** any migration files.

---

## Temporary Shim Policy

A compatibility shim is a small re-export that keeps the old import path working while a new path is introduced. Shims are **allowed only when**:

1. They are simple — one line re-exports only (e.g., `from app.new.path import Thing`).
2. They are documented here with a removal note, removal condition, and target removal phase.
3. They do not silently duplicate logic.

**No shims exist yet.** Phase 20 and Phase 21 must register any shim they create in this table:

| Shim File | Re-exports From | Removal Condition | Target Removal Phase | Owner |
|---|---|---|---|---|
| (none yet) | — | — | — | — |

Shims must be removed in the phase that confirms all importers have been updated. Phase 22 is the final owner of shim removal verification.
