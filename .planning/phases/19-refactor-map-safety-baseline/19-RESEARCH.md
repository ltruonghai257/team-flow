# Phase 19: Refactor Map & Safety Baseline - Research

## RESEARCH COMPLETE

## Planning Question

What must be known before planning a structure-only refactor of TeamFlow toward an Open WebUI-inspired layout?

## Inputs Reviewed

- `.planning/phases/19-refactor-map-safety-baseline/19-CONTEXT.md`
- `.planning/ROADMAP.md`
- `.planning/REQUIREMENTS.md`
- `.planning/STATE.md`
- `.planning/codebase/STRUCTURE.md`
- `.planning/codebase/ARCHITECTURE.md`
- `.planning/codebase/CONVENTIONS.md`
- Current file inventory under `backend/app`, `backend/tests`, `backend/alembic`, `frontend/src`, `frontend/tests`, Docker/runtime files
- Open WebUI GitHub tree for current reference structure:
  - `backend/open_webui/`: `models`, `routers`, `socket`, `utils`, `config.py`, `env.py`, `main.py`, migrations and storage/data groups
  - `src/lib/`: `apis`, `components`, `stores`, `types`, `utils`, constants, workers

## Key Findings

### Phase Boundary

Phase 19 should produce documentation artifacts only. It should not move Python modules, split TypeScript files, change package roots, add dependencies, alter database schema, or edit runtime commands beyond documenting what later phases must update.

### Current TeamFlow Backend Shape

TeamFlow already has a conservative FastAPI root at `backend/app`, with these major groups:

- Entry/config/runtime: `main.py`, `config.py`, `database.py`, `limiter.py`
- Auth and cross-cutting services: `auth.py`, `ai_client.py`, `email_service.py`, `scheduler_jobs.py`
- API layer: `routers/*.py`, including REST routers plus `routers/websocket.py`
- Domain persistence and DTOs: large shared `models.py` and `schemas.py`
- Services: `services/reminder_notifications.py`
- WebSocket manager: `websocket/manager.py`
- Alembic: `backend/alembic`, `backend/alembic.ini`
- Tests: `backend/tests/*.py`

The riskiest backend coupling is not the router layout; it is the shared `models.py` and `schemas.py` modules plus import paths used by Alembic, tests, scheduler jobs, scripts, and runtime targets.

### Current TeamFlow Frontend Shape

TeamFlow uses SvelteKit under `frontend/src`, which should remain the root for this milestone. Existing shared code is concentrated in:

- `frontend/src/lib/api.ts`: request wrapper, domain API objects, shared exported types
- `frontend/src/lib/stores/*.ts`: auth, chat, notifications, sub-team scope
- `frontend/src/lib/websocket.ts`: chat WebSocket singleton
- `frontend/src/lib/utils.ts`
- `frontend/src/lib/components/*`: shared components grouped by feature
- `frontend/src/routes/*`: user-facing routes that must keep current URLs

The riskiest frontend coupling is the single API/type module and many `$lib/api` imports across routes/components. Route URLs and visual behavior must not change.

### Open WebUI-Inspired Adaptation

Open WebUI currently separates backend concerns under `backend/open_webui` with groups like `routers`, `models`, `socket`, `utils`, config/env files, and migrations. Its frontend `src/lib` contains `apis`, `components`, `stores`, `types`, and `utils`. For TeamFlow, this should be adapted as:

- Keep `backend/app` instead of renaming to `backend/open_webui`.
- Keep `frontend/src` instead of moving SvelteKit to root `src`.
- Use TeamFlow-native domain names: tasks, projects, milestones, sprints, statuses, notifications, chat, ai, performance, team/invites.
- Split only where the map shows real benefit and Phase 20/21 can verify incrementally.

### Protected Behavior Inventory

Phase 19 must protect these surfaces before Phase 20/21:

- FastAPI startup and lifespan, including optional Alembic upgrade and scheduler start/shutdown
- Router registration and current prefixes: `/api/auth`, `/api/users`, `/api/projects`, `/api/status-sets`, `/api/tasks`, `/api/notifications`, `/api/ai`, `/api/chat`, `/api/performance`, `/api/timeline`, `/ws/chat`, `/health`
- Auth/session behavior: cookie and bearer token auth, `/api/auth/token`, `/api/auth/me`, logout, invite acceptance
- Svelte routes: `/`, `/tasks`, `/projects`, `/milestones`, `/team`, `/timeline`, `/performance`, `/performance/[id]`, `/schedule`, `/ai`, `/login`, `/register`, `/invite/accept`
- WebSocket behavior: `/ws/chat`, chat channels, DMs, presence, assistant streaming/cancel/reset
- Scheduler/notifications: due notification processing and generated sprint/milestone reminder reconciliation
- AI task input and AI breakdown/parse endpoints
- Docker/runtime: `Dockerfile`, `backend/Dockerfile`, `frontend/Dockerfile`, `docker-compose.yml`, `supervisord.conf`, `nginx.conf`, uvicorn target `app.main:app`
- Alembic env imports and migration history
- Backend and frontend test entrypoints

## Recommended Planning Shape

Use four documentation plans:

1. Safety baseline and protected behavior inventory.
2. Backend target structure and old-to-new map.
3. Frontend target structure and old-to-new map.
4. Final refactor playbook synthesizing sequencing, shim policy, and Phase 20/21/22 handoff.

This keeps backend and frontend map work parallel after the shared safety baseline, then creates one final contract for the downstream restructure phases.

## Validation Architecture

Phase 19 is a documentation phase, so validation should verify artifact completeness, traceability, and command capture rather than running application behavior checks as the primary signal.

Required automated checks:

- `rtk proxy node .codex/get-shit-done/bin/gsd-tools.cjs verify references .planning/phases/19-refactor-map-safety-baseline/19-REFACTOR-PLAYBOOK.md`
- `rtk proxy rg "STRUCT-01|STRUCT-02|STRUCT-03|D-01|D-16" .planning/phases/19-refactor-map-safety-baseline`
- `rtk proxy rg "backend/app/main.py|frontend/src/lib/api.ts|/ws/chat|app.main:app|alembic" .planning/phases/19-refactor-map-safety-baseline`
- `rtk proxy rg "blocked|fallback|failure reason|next-best fallback" .planning/phases/19-refactor-map-safety-baseline/19-SAFETY-BASELINE.md`

Baseline commands the Phase 19 executor should run or explicitly document as blocked:

- Backend tests: `rtk pytest backend/tests -q`
- Backend import/compile check: `rtk proxy python -m compileall backend/app`
- Alembic check: `rtk proxy alembic -c backend/alembic.ini heads` from the correct working directory, or document why local env blocks it
- Frontend check: from `frontend`, `rtk npm run check` or Bun equivalent if local scripts support Bun
- Frontend production build: from `frontend`, `rtk npm run build` or Bun equivalent if local scripts support Bun
- Frontend smoke/e2e availability: `rtk playwright test` scoped to existing frontend tests when dependencies and browsers are available

Manual review checks:

- Confirm route URL list in the playbook matches ROADMAP Phase 19 success criteria.
- Confirm backend and frontend maps name current source files and target locations.
- Confirm temporary shims include owners and removal notes.

## Planning Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Map omits runtime import targets | Phase 20 breaks Docker/Azure or uvicorn startup | Require runtime file inventory in Plan 01 and synthesis in Plan 04 |
| API/type split loses request behavior | Phase 21 regresses auth cookies or sub-team scoping | Keep shared request/auth behavior centralized and map feature APIs around it |
| Alembic imports are overlooked | Migration commands fail after backend restructure | Include Alembic env and migration history in backend protected behavior |
| Documentation is too generic | Downstream executor makes broad refactor choices | Require old-to-new tables with concrete current files and target paths |
| Baseline checks are skipped silently | Refactor starts without a known safety line | Require blocked-command reason plus fallback for every unavailable command |

