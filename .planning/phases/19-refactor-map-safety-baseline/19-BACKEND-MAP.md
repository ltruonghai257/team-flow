# 19-BACKEND-MAP.md
# Phase 19: Backend Target Map

**Created:** 2026-04-27
**Phase:** 19 — Refactor Map & Safety Baseline

> **Inspiration:** Open WebUI (`open-webui/open-webui`) is used as a structural reference only.
> TeamFlow-native names are used throughout. Open WebUI product vocabulary (e.g., `pipeline`, `tool_server`,
> `knowledge`) is not copied. No backend code is moved in Phase 19.

---

## Backend Target Structure

The target keeps `backend/app` as the Python package root. Internal folders are reorganized toward Open WebUI-inspired groupings where they improve maintainability, with TeamFlow-native names.

```
backend/
├── alembic.ini                          # Alembic config (stays, protected)
├── alembic/                             # Migration history (stays, protected)
│   ├── env.py                           # Imports app.config, app.database, app.models — update with any move
│   ├── script.py.mako
│   └── versions/                        # 11 migration files — append-only, never reorder
├── requirements.txt
├── Dockerfile                           # Dev image: uvicorn app.main:app at 0.0.0.0:8000
├── tests/                               # Backend test suite (stays, protected)
│   ├── conftest.py                      # pytest fixtures with async DB session
│   ├── test_tasks.py, test_sprints.py, test_status_sets.py
│   ├── test_sub_teams.py, test_projects.py, test_notifications.py
│   ├── test_dashboard.py, test_performance.py, test_timeline.py
└── app/                                 # Python package root (stays as `app`)
    ├── main.py                          # FastAPI app + lifespan (stays, PROTECTED)
    ├── config.py                        # Settings / env vars (stays)
    ├── database.py                      # AsyncEngine, AsyncSessionLocal, Base, get_db (stays, PROTECTED — Alembic env imports Base)
    ├── limiter.py                       # Slowapi rate limiter singleton (stays)
    ├── auth.py                          # JWT helpers, get_current_user (stays, PROTECTED)
    ├── ai_client.py                     # acompletion() wrapper for external AI (stays)
    ├── email_service.py                 # Email sending (stays OR → services/email.py, Phase 20 discretion)
    ├── scheduler_jobs.py                # APScheduler start/shutdown + job functions (stays, PROTECTED)
    ├── models.py                        # All SQLAlchemy models — STAYS monolithic by default
    │                                    #   OR split to models/ package — Phase 20 discretion after import analysis
    │                                    #   (see Domain Split Candidates section below)
    ├── schemas.py                       # All Pydantic schemas — STAYS monolithic by default
    │                                    #   OR split to schemas/ package — Phase 20 discretion after import analysis
    │                                    #   (see Domain Split Candidates section below)
    ├── routers/                         # One router per domain (stays, all prefixes PROTECTED)
    │   ├── __init__.py
    │   ├── ai.py             (/api/ai)
    │   ├── auth.py           (/api/auth)
    │   ├── chat.py           (/api/chat)
    │   ├── dashboard.py      (/api/dashboard)
    │   ├── invites.py        (/api/teams/invite, /api/invites/*)
    │   ├── milestones.py     (/api/milestones)
    │   ├── notifications.py  (/api/notifications)
    │   ├── performance.py    (/api/performance)
    │   ├── projects.py       (/api/projects)
    │   ├── schedules.py      (/api/schedules)
    │   ├── sprints.py        (/api/sprints)
    │   ├── statuses.py       (/api/status-sets)
    │   ├── sub_teams.py      (/api/sub-teams)
    │   ├── tasks.py          (/api/tasks)
    │   ├── timeline.py       (/api/timeline)
    │   ├── users.py          (/api/users)
    │   └── websocket.py      (/ws/chat — no router prefix, route set on decorator)
    ├── services/                        # Already exists — service layer
    │   ├── __init__.py
    │   └── reminder_notifications.py    # Reminder reconciliation (stays)
    │                                    # Phase 20 can add: services/email.py (extracted from email_service.py)
    ├── websocket/                       # Already exists — keeps `websocket/` name (not renamed to `socket/`)
    │   ├── __init__.py
    │   └── manager.py                   # ConnectionManager singleton (stays, PROTECTED import path)
    └── scripts/                         # Utility scripts (stays)
        ├── __init__.py
        ├── create_admin.py
        └── seed_demo.py
```

### Open WebUI Groups NOT Copied

The following Open WebUI package groups do not fit TeamFlow and are intentionally excluded:

| Open WebUI Group | Reason Not Copied |
|---|---|
| `routers/pipelines.py`, `routers/tools.py` | TeamFlow has no pipeline or tool server concept |
| `internal/` | Open WebUI-specific internal routing; TeamFlow uses `routers/` directly |
| `models/audits.py`, `models/feedback.py` | No audit trail or feedback loop features in TeamFlow |
| `env.py` (root env parser) | TeamFlow uses Pydantic `BaseSettings` in `config.py` — cleaner for this project size |
| `constants.py` (large constants module) | TeamFlow constants live in `config.py` and enum values in `models.py` |
| `socket/` (Socket.IO) | TeamFlow uses native FastAPI WebSocket, not Socket.IO |

---

## Current-to-Target File Map

### Core App Files

| Current Path | Target Path | Reason | Risk | Import Update Scope | Shim Candidate |
|---|---|---|---|---|---|
| `backend/app/main.py` | **stays** | PROTECTED; uvicorn target `app.main:app` | Any move requires supervisord, Dockerfile, and compose updates | N/A | No |
| `backend/app/config.py` | **stays** | Small, no coupling issues | Low | N/A | No |
| `backend/app/database.py` | **stays** | PROTECTED — `Base` imported by Alembic env | Medium (Alembic env.py must track any move) | alembic/env.py | No |
| `backend/app/limiter.py` | **stays** | Singleton used across all routers | Low | N/A | No |
| `backend/app/auth.py` | **stays** | PROTECTED — cookie/bearer auth | Low | N/A | No |
| `backend/app/ai_client.py` | **stays** | Single-function wrapper, low coupling | Low | N/A | No |
| `backend/app/email_service.py` | **stays** OR `backend/app/services/email.py` | Move only if Phase 20 needs cleaner services/ grouping | Low | routers/invites.py (and any other importer) | Yes if moved |
| `backend/app/scheduler_jobs.py` | **stays** | PROTECTED — called in lifespan | Low | N/A | No |

### Models

| Current Path | Target Path Options | Reason | Risk | Import Update Scope | Notes |
|---|---|---|---|---|---|
| `backend/app/models.py` | **Option A (default):** stays as monolith | Safest; zero import churn | Very low | None | Recommended starting point for Phase 20 |
| `backend/app/models.py` | **Option B (domain split):** `backend/app/models/` package | Improves long-term maintainability | High | All routers, schemas.py, auth.py, services/, scheduler_jobs.py, websocket/manager.py, alembic/env.py | Requires `models/__init__.py` to re-export everything during transition |

**Domain Split Candidates (if Option B chosen by Phase 20):**

| Domain Module | Models It Would Contain |
|---|---|
| `models/enums.py` | UserRole, TaskStatus, StatusSetScope, TaskPriority, TaskType, MilestoneStatus, SprintStatus, NotificationStatus, NotificationEventType, ReminderProposalStatus, InviteStatus |
| `models/user.py` | User, SubTeam, TeamInvite, KPIWeightSettings |
| `models/project.py` | Project, Milestone, Sprint, Task, Schedule |
| `models/status.py` | StatusSet, CustomStatus, StatusTransition |
| `models/notification.py` | EventNotification, SubTeamReminderSettings, ReminderSettingsProposal |
| `models/chat.py` | ChatChannel, ChatChannelMember, ChatConversation, ChatMessage, UserPresence |
| `models/ai.py` | AIConversation, AIMessage |

**Critical coupling note:** All relationship FKs between domains (e.g., Task → Project, ChatMessage → User) create cross-model imports. Phase 20 must run import dependency analysis before committing to a split depth. A monolith `models.py` has zero cross-import risk.

### Schemas

| Current Path | Target Path Options | Reason | Risk | Import Update Scope | Notes |
|---|---|---|---|---|---|
| `backend/app/schemas.py` | **Option A (default):** stays as monolith | Safest; schemas are stateless Pydantic models | Very low | None | Recommended starting point for Phase 20 |
| `backend/app/schemas.py` | **Option B (domain split):** `backend/app/schemas/` package | Improves discoverability | Medium | All routers that import from schemas, auth.py | Requires `schemas/__init__.py` re-export during transition |

**Schema Domain Groupings (if split chosen):**

| Schema Module | Classes It Would Contain |
|---|---|
| `schemas/auth.py` | Token, TokenData, UserCreate, UserUpdate, UserRoleUpdate, UserOut |
| `schemas/project.py` | ProjectCreate, ProjectUpdate, ProjectOut |
| `schemas/milestone.py` | MilestoneCreate, MilestoneUpdate, MilestoneOut |
| `schemas/sprint.py` | SprintBase, SprintCreate, SprintUpdate, SprintOut, SprintClosePayload |
| `schemas/status.py` | CustomStatusOut, StatusSetOut, StatusTransitionOut, StatusTransitionPair, StatusTransitionsReplace, BlockedStatusTransitionDetail, CustomStatusCreate, CustomStatusUpdate, StatusReorderPayload, StatusDeletePayload, ProjectStatusRevertPayload |
| `schemas/task.py` | TaskCreate, TaskUpdate, TaskOut, AiParseRequest, AiParseResponse |
| `schemas/schedule.py` | ScheduleCreate, ScheduleUpdate, ScheduleOut |
| `schemas/notification.py` | NotificationCreate, NotificationBulkCreate, NotificationOut, ReminderSettingsOut, ReminderSettingsUpdate, ReminderSettingsProposalCreate, ReminderSettingsProposalReview, ReminderSettingsProposalOut |
| `schemas/chat.py` | ChatChannelOut, ChatMessageOut, ChatConversationOut, AIMessageCreate, AIMessageOut, AIConversationOut |
| `schemas/dashboard.py` | DashboardStats, TrendDataPoint |
| `schemas/performance.py` | TeamMemberPerformance, PerformanceDashboard, UserPerformanceDetail, AiBreakdownRequest, AiBreakdownSubtask, AiBreakdownResponse, ProjectSummaryRequest, ProjectSummarySections, ProjectSummaryResponse, KPIWeightSettingsOut, KPIWeightSettingsUpdate, KPIWarningEmailRequest, KPIWarningEmailResponse, KPIFilterOptions, KPIReason, KPIScoreBreakdown, KPIMemberScorecard, KPIChartPoint, KPIChartSeries, KPIOverviewSummary, KPIOverviewResponse, KPISprintResponse, KPIQualityResponse, KPIMembersResponse, KPIDrilldownTask, KPIDrilldownResponse |
| `schemas/timeline.py` | TimelineTaskOut, TimelineMilestoneOut, TimelineProjectOut |
| `schemas/sub_team.py` | SubTeamBase, SubTeamCreate, SubTeamUpdate, SubTeamOut |
| `schemas/invite.py` | InviteCreate, InviteOut, InviteValidateOut, InviteAcceptRequest, DirectAddRequest |

### Routers

All routers **stay in place** (`backend/app/routers/*.py`). Route prefixes are PROTECTED.

| Current Path | Target Path | Reason |
|---|---|---|
| `backend/app/routers/websocket.py` | **stays** | `/ws/chat` route must not change |
| all other `backend/app/routers/*.py` | **stays** | Route prefixes are protected |

### Services

| Current Path | Target Path | Reason | Risk | Import Update Scope | Shim Candidate |
|---|---|---|---|---|---|
| `backend/app/services/reminder_notifications.py` | **stays** | Already well-located | None | N/A | No |
| `backend/app/email_service.py` | `backend/app/services/email.py` (Phase 20 discretion) | Better services grouping | Low | `backend/app/routers/invites.py` | Yes — `backend/app/email_service.py` → re-exports from `services/email.py` |

### WebSocket

| Current Path | Target Path | Reason |
|---|---|---|
| `backend/app/websocket/manager.py` | **stays** | PROTECTED — imported as `app.websocket.manager` |
| `backend/app/routers/websocket.py` | **stays** | See Routers above |

### Scripts

| Current Path | Target Path | Reason |
|---|---|---|
| `backend/app/scripts/create_admin.py` | **stays** | Utility script, no refactor needed |
| `backend/app/scripts/seed_demo.py` | **stays** | Utility script, no refactor needed |

### Alembic and Tests

| Current Path | Target Path | Protection Notes |
|---|---|---|
| `backend/alembic/` | **stays** | PROTECTED — migration history is append-only |
| `backend/alembic/env.py` | **stays** | Must update together with any move of `app.config`, `app.database`, or `app.models` |
| `backend/alembic.ini` | **stays** | `script_location = alembic` relative to backend/ |
| `backend/tests/` | **stays** | Test imports use `from app.*`; must update if models/schemas split |
| `backend/tests/conftest.py` | **stays** | Async test session setup |

### Runtime References to `app.main:app`

| File | Reference | Phase 20 must update if? |
|---|---|---|
| `supervisord.conf` | `command=... uvicorn app.main:app ... directory=/app/backend` | If `main.py` moves or `app` package renamed |
| `backend/Dockerfile` | `CMD ["uvicorn", "app.main:app", ...]` | Same |
| `docker-compose.yml` | `DATABASE_URL` env; builds from `./backend` | If `backend/` directory structure changes |
| root `Dockerfile` | `COPY backend/ /app/backend/` | If backend root path changes |

---

## Migration Slices

Phase 20 executes the backend restructure in small, verifiable slices. Each slice names the files it touches and the protected behavior it verifies after completion.

### Slice Order

| # | Slice Name | Files | Verification After Slice |
|---|---|---|---|
| B0 | **Non-moving prep: import inventory** | No file moves | Run `python -m compileall backend/app` to confirm baseline. Grep all `from app.*` imports to produce a full current import map. |
| B1 | **Services extraction: email_service → services/email.py** *(optional)* | `backend/app/email_service.py` → `backend/app/services/email.py`; add shim at old path | `python -m compileall backend/app`; verify invite routes still work |
| B2 | **Schemas monolith stays OR domain split** | If splitting: create `backend/app/schemas/` with `__init__.py` re-export first | `python -m compileall backend/app`; run backend tests |
| B3 | **Models monolith stays OR domain split** | If splitting: create `backend/app/models/` with `__init__.py` re-export first; update `alembic/env.py` import in same commit | `python -m compileall backend/app`; run `alembic heads` or equivalent; run backend tests |
| B4 | **Router import updates** | Update all routers to use new schema/model paths after B2/B3 | `python -m compileall backend/app`; run backend tests |
| B5 | **Alembic/test/runtime import update pass** | Update `alembic/env.py`, `backend/tests/conftest.py`, any test that imports models or schemas directly | Run `alembic heads`; run backend tests; `python -m compileall backend/app` |
| B6 | **Shim removal** | Remove any compatibility re-exports added in B1-B4 | Run backend tests; verify no stale imports |
| B7 | **Final backend regression baseline** | No file changes | Run full backend test suite; verify `/health`; smoke check login + task creation |

### Slice Dependencies

```
B0 → B1 (optional) → B2 → B3 → B4 → B5 → B6 → B7
                     ↑
            (B2 and B3 can be deferred if monolith stays)
```

If Phase 20 chooses to keep `models.py` and `schemas.py` monolithic, **slices B2, B3, B4, and B6 are skipped**. B0, B1 (optional), B5 (for any env.py updates), and B7 (regression) still apply.

### Protected Behavior Each Slice Must Not Break

| Slice | Protected Behavior |
|---|---|
| All | `app.main:app` uvicorn target unchanged |
| All | `/health`, all `/api/*` route prefixes, `/ws/chat` unchanged |
| B1 | Email sending for invites (`POST /api/teams/invite`) |
| B2, B3 | Alembic `env.py` imports and migration head intact |
| B3 | `alembic/env.py` → `import app.models` (noqa) must remain valid |
| B5 | `alembic heads` returns current head; backend tests pass |
| B7 | Full backend test suite passes; manual smoke checklist from 19-SAFETY-BASELINE.md passes |
