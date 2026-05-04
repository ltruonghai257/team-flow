# 19-REFACTOR-PLAYBOOK.md
# Phase 19: Refactor Playbook

**Created:** 2026-04-27
**Phase:** 19 — Refactor Map & Safety Baseline
**Milestone:** v2.1 — Open WebUI-Style Project Structure Refactor

---

## Phase Boundary and Non-Goals

**Phase 19 is a documentation and mapping phase only.**

It does not move code, rename packages, change API behavior, redesign the UI, add dependencies, alter the database schema, or introduce any compatibility shims.

**What Phase 19 produces:**
- `19-SAFETY-BASELINE.md` — pre-refactor protected behavior inventory and baseline command status
- `19-BACKEND-MAP.md` — backend target structure, current-to-target file map, and Phase 20 migration slices
- `19-FRONTEND-MAP.md` — frontend target structure, API/type split map, and Phase 21 migration slices
- This playbook — synthesis and downstream phase contracts

---

## Approved Backend Target Structure

> Full details: [`19-BACKEND-MAP.md`](.planning/phases/19-refactor-map-safety-baseline/19-BACKEND-MAP.md)

**Package root:** `backend/app` (stays — not renamed)

Key groupings:
- **App core:** `main.py`, `config.py`, `database.py`, `limiter.py`, `auth.py`, `ai_client.py`, `scheduler_jobs.py`
- **Routers:** `backend/app/routers/` — one per domain, all route prefixes PROTECTED
- **Models:** `backend/app/models.py` stays monolithic by default; domain split to `backend/app/models/` is Phase 20 discretion after import analysis
- **Schemas:** `backend/app/schemas.py` stays monolithic by default; domain split to `backend/app/schemas/` is Phase 20 discretion
- **Services:** `backend/app/services/` (already exists; `reminder_notifications.py` stays)
- **WebSocket:** `backend/app/websocket/manager.py` (stays, import path PROTECTED)
- **Scripts:** `backend/app/scripts/` (stays)
- **Alembic:** `backend/alembic/` (append-only, PROTECTED)
- **Tests:** `backend/tests/` (PROTECTED)

Open WebUI groups **not copied:** `pipelines`, `tools`, `internal`, `audits`, `constants`, `socket/` (TeamFlow uses native FastAPI WebSocket).

---

## Approved Frontend Target Structure

> Full details: [`19-FRONTEND-MAP.md`](.planning/phases/19-refactor-map-safety-baseline/19-FRONTEND-MAP.md)

**SvelteKit root:** `frontend/src` (stays — not moved to repo root `src/`)

Key groupings:
- **`lib/apis/`** — NEW: feature API modules split from `api.ts`; shared `request.ts` wrapper stays centralized
- **`lib/types/`** — NEW: shared TypeScript types by domain (split from inline definitions in `api.ts`)
- **`lib/components/`** — STAYS (already organized by feature group)
- **`lib/stores/`** — STAYS
- **`lib/websocket.ts`** — STAYS (connects to `/ws/chat`, PROTECTED)
- **`lib/utils.ts`** — STAYS
- **`routes/`** — STAYS, all route URLs PROTECTED

---

## Protected Behavior List

> Full details: [`19-SAFETY-BASELINE.md`](.planning/phases/19-refactor-map-safety-baseline/19-SAFETY-BASELINE.md)

The following behaviors must remain functionally identical after all Phase 20/21/22 file moves:

| Category | What Is Protected |
|---|---|
| **Uvicorn target** | `app.main:app` — cwd `/app/backend` in supervisord |
| **FastAPI startup** | Lifespan: Alembic migration + scheduler start on startup; scheduler shutdown on exit |
| **All REST route prefixes** | `/api/auth`, `/api/tasks`, `/api/projects`, `/api/status-sets`, `/api/sub-teams`, etc. |
| **WebSocket** | `GET /ws/chat` upgrade — chat, DMs, presence, AI assistant streaming/cancel/reset |
| **Health endpoint** | `GET /health` → `{"status": "ok"}` |
| **Auth/session** | Cookie (`access_token`, httponly, samesite=lax) + bearer; tokenUrl = `/api/auth/token` |
| **Invite acceptance** | `POST /api/invites/accept` and frontend route `/invite/accept` |
| **AI task input** | `/api/ai/*` endpoints; `acompletion()` wrapper in `ai_client.py` |
| **Scheduler jobs** | `process_due_notifications` (60s) + `reconcile_generated_reminders` (5min) |
| **Notification delivery** | `/api/notifications/pending` polling |
| **Alembic history** | 11 migration files, append-only; `env.py` imports `app.models` (noqa) |
| **Svelte route URLs** | `/`, `/login`, `/register`, `/invite/accept`, `/tasks`, `/projects`, `/milestones`, `/schedule`, `/timeline`, `/team`, `/performance`, `/performance/[id]`, `/ai` |
| **Frontend request behavior** | `credentials: 'include'`, `X-SubTeam-ID` header, base URL `/api`, error handling |
| **WebSocket client** | `frontend/src/lib/websocket.ts` connects to `/ws/chat` |
| **nginx routing** | `/api/` → uvicorn, `/ws/` → uvicorn (upgrade), `/` → SPA fallback (`200.html`) |
| **Docker build pipeline** | bun frontend build → Python deps → final with nginx+supervisord; `COPY backend/ /app/backend/` |

---

## Baseline Command Results Summary

> Full details: [`19-SAFETY-BASELINE.md` — Pre-Refactor Command Baseline](.planning/phases/19-refactor-map-safety-baseline/19-SAFETY-BASELINE.md)

All baseline commands were blocked by local environment constraints (no running DB, no installed Python/bun packages). Each is documented with failure reason and fallback.

| Command | Status | Fallback Applied |
|---|---|---|
| `pytest backend/tests -q` | BLOCKED (no DB) | Import pattern grep; all 9 test files confirmed present |
| `python -m compileall backend/app` | BLOCKED (no Python env) | Structural inspection; no syntax errors detected |
| `alembic -c backend/alembic.ini heads` | BLOCKED (no alembic) | Manual migration chain inspection; 11 files, head: `d3e4f5a6b7c8` |
| `cd frontend && bun run check` | BLOCKED (no node_modules) | Package.json `check` script confirmed present; svelte-check configured |
| `cd frontend && bun run build` | BLOCKED (no node_modules) | svelte.config.js structure verified; adapter-static with 200.html fallback |
| Playwright tests | BLOCKED (no stack/browsers) | Test files confirmed: sprint_board.spec.ts, status_transition.spec.ts, mobile/ |

**Phase 20 and Phase 21 must re-run all blocked commands in an environment where the full stack is available before moving code.**

---

## Sequencing Notes

Phase 19 produces the map. Phases 20/21 execute independently. Phase 22 owns integrated verification.

```
Phase 19 (done) ──┬── Phase 20 (backend) ──┐
                  │                        ├── Phase 22 (runtime + regression)
                  └── Phase 21 (frontend) ──┘
```

- **Phase 20** owns backend package restructure. It can begin immediately after Phase 19 without waiting for Phase 21.
- **Phase 21** owns frontend SvelteKit structure. It can begin immediately after Phase 19 without waiting for Phase 20.
- **Phase 22** owns Docker/dev/Azure runtime entrypoint updates and integrated regression verification. It runs after both Phase 20 and Phase 21 are complete.
- Phases 20 and 21 must not modify `supervisord.conf`, `nginx.conf`, or the root `Dockerfile` — those belong to Phase 22.

---

## Temporary Shim Policy

A compatibility shim is a one-line re-export that keeps an old import path working during a migration slice. Shims must be:

1. One line only (e.g., `from app.services.email import send_email`)
2. Documented in the table below with owner, removal condition, and target removal phase
3. Never used to duplicate logic

**No shims exist yet.** Phase 20 and Phase 21 must register any shim they create here:

| Shim File | Re-exports From | Owner | Removal Condition | Target Removal Phase |
|---|---|---|---|---|
| (none) | — | — | — | — |

Phase 22 is the final deadline for verifying all shims have been removed.

---

## Phase 20 Handoff

**Owner:** Phase 20 — Backend Package Restructure

**Input artifacts from Phase 19:**
- `19-BACKEND-MAP.md` — target structure, current-to-target map, migration slices B0–B7
- `19-SAFETY-BASELINE.md` — protected behavior inventory and baseline commands

**Phase 20 responsibilities:**

1. Run slice B0: produce a full `from app.*` import map to confirm no imports are missed
2. Decide whether to keep `models.py` and `schemas.py` monolithic (default, recommended) or split to domain packages
3. Execute backend migration slices in order: B1 (optional email extraction) → B2 (schemas) → B3 (models) → B4 (router imports) → B5 (alembic/tests/runtime imports) → B6 (shim removal) → B7 (regression)
4. Re-run all BLOCKED baseline commands (`pytest`, `compileall`, `alembic heads`) in a working environment before declaring Phase 20 complete
5. Must NOT modify `supervisord.conf`, `nginx.conf`, or the root `Dockerfile` — these belong to Phase 22
6. Must NOT change any API route prefixes, WebSocket endpoint, health endpoint, auth behavior, or Alembic migration history

**Phase 20 MUST NOT do:**
- Change `app.main:app` uvicorn target without a Phase 22 coordination note
- Alter Alembic migration history
- Add new Python dependencies
- Change any REST route prefix or WebSocket endpoint

---

## Phase 21 Handoff

**Owner:** Phase 21 — Frontend SvelteKit Structure

**Input artifacts from Phase 19:**
- `19-FRONTEND-MAP.md` — target structure, API/type split map, migration slices F0–F7
- `19-SAFETY-BASELINE.md` — frontend protected behaviors (route URLs, request behavior, WebSocket)

**Phase 21 responsibilities:**

1. Run slice F0: grep all `import ... from '$lib/api'` callsites to build a complete importer map
2. Execute frontend migration slices in order: F1 (types) → F2 (request wrapper) → F3 (feature API modules) → F4 (barrel export) → F5 (import updates) → F6 (optional route-local components) → F7 (final check/build/smoke)
3. Keep `request()` centralized in `lib/apis/request.ts` — credentials, sub-team header, base URL, error handling must not be duplicated in feature modules
4. Re-run BLOCKED frontend commands (`bun run check`, `bun run build`, Playwright) in a working environment before declaring Phase 21 complete
5. Must NOT change any Svelte route URLs or alter visual behavior

**Phase 21 MUST NOT do:**
- Rename or move any `routes/` file in a way that changes a route URL
- Redesign any UI component or page
- Add new npm/bun dependencies
- Modify backend code

---

## Phase 22 Handoff

**Owner:** Phase 22 — Runtime Integration and Regression Verification

**Input artifacts from Phase 19:**
- `19-SAFETY-BASELINE.md` — full manual smoke checklist and Docker entrypoint review
- `19-BACKEND-MAP.md` and `19-FRONTEND-MAP.md` — shim policy and removal notes

**Phase 22 responsibilities:**

1. Update `supervisord.conf`, root `Dockerfile`, `backend/Dockerfile`, `docker-compose.yml`, and `nginx.conf` if any Phase 20/21 move changed a runtime import path, build output path, or package root name
2. Verify the Docker monolith build succeeds (`docker build .`)
3. Verify the full manual smoke checklist from `19-SAFETY-BASELINE.md` passes: login/session, task board, AI task input, WebSocket chat, scheduler/notifications, `/health`, invite acceptance, SPA fallback
4. Remove all temporary compatibility shims registered in the shim table above
5. Run the full backend test suite and confirm all tests pass against the refactored paths
6. Run frontend `check` and `build` and confirm no errors
7. Run Playwright E2E tests

**Phase 22 MUST NOT do:**
- Move source code — Phase 22 is verification and runtime-config updates only
- Add new dependencies
- Change API behavior or route URLs

---

## Traceability

### STRUCT Requirements

| Requirement | Description | Satisfied By |
|---|---|---|
| **STRUCT-01** | Developer can understand the repo layout from a documented target structure that maps current TeamFlow folders to Open WebUI-inspired folders | `19-BACKEND-MAP.md` § Backend Target Structure, Current-to-Target File Map; `19-FRONTEND-MAP.md` § Frontend Target Structure, Current-to-Target File Map; this playbook §§ Approved Backend / Frontend Target Structure |
| **STRUCT-02** | Existing behavior boundaries are explicitly protected before code moves begin | `19-SAFETY-BASELINE.md` §§ Protected Behavior Inventory, Pre-Refactor Command Baseline, Manual Smoke Checklist, Docker/Runtime Entrypoint Review; this playbook § Protected Behavior List |
| **STRUCT-03** | Refactor work is split into small migration slices so imports can be updated and verified incrementally | `19-BACKEND-MAP.md` § Migration Slices (B0–B7); `19-FRONTEND-MAP.md` § Migration Slices (F0–F7); this playbook § Phase 20/21 Handoff |

### Decision Traceability (D-01 through D-16)

| Decision | Statement | Where Honored |
|---|---|---|
| **D-01** | Keep `backend/app` as backend package root while reorganizing internal folders | `19-BACKEND-MAP.md` § Backend Target Structure — `backend/app/` is the package root throughout |
| **D-02** | Treat Open WebUI as structural inspiration, not an exact clone; use TeamFlow-native names | Both MAPs use TeamFlow-native folder names (e.g., `websocket/` not `socket/`); Open WebUI groups not fitted to TeamFlow are listed as explicitly excluded |
| **D-03** | Do not move SvelteKit app to repo-root `src/` during this milestone | `19-FRONTEND-MAP.md` § Frontend Target Structure — `frontend/src` remains the SvelteKit root; note in Phase 22 Handoff |
| **D-04** | Leave backend split depth to Phase 20 discretion after dependency mapping | `19-BACKEND-MAP.md` § Models and § Schemas — both offer monolith (default) and domain-split options with explicit coupling warnings |
| **D-05** | Temporary shims allowed only when small, documented, and paired with removal notes | This playbook § Temporary Shim Policy; `19-SAFETY-BASELINE.md` § Temporary Shim Policy |
| **D-06** | Backend restructuring must preserve FastAPI startup, router registration, auth/session, rate limiting, CORS, scheduler, WebSocket, health, Alembic history, and test imports | `19-SAFETY-BASELINE.md` § Protected Behavior Inventory (complete list); `19-BACKEND-MAP.md` § Core App Files with PROTECTED annotations |
| **D-07** | Prioritize scalable frontend structure, not the smallest possible move | `19-FRONTEND-MAP.md` § Frontend Target Structure — full `lib/apis/`, `lib/types/` grouping documented; optional route-local component extraction in F6 |
| **D-08** | The Phase 19 map may include a full frontend structure pass | `19-FRONTEND-MAP.md` covers full `lib/apis` split (17 modules), `lib/types` split, components, stores, WebSocket, routes, and config — a complete pass |
| **D-09** | Current route URLs and visual behavior must remain stable | `19-FRONTEND-MAP.md` § Route Files — all stay; §§ Migration Slices explicitly guard route URLs; this playbook § Protected Behavior List |
| **D-10** | Split API clients and shared types by feature domain while keeping request/auth behavior centralized | `19-FRONTEND-MAP.md` § Centralized Request/Auth Behavior — `request.ts` keeps BASE URL, credentials, X-SubTeam-ID, error handling; feature modules call it |
| **D-11** | Define the full available baseline as mandatory before code moves | `19-SAFETY-BASELINE.md` § Pre-Refactor Command Baseline — all 6 required command categories documented with results |
| **D-12** | Blocked checks must not be skipped silently — document failure reason and fallback | `19-SAFETY-BASELINE.md` § Pre-Refactor Command Baseline — every command has Result, Failure Reason, and Fallback columns; all 6 BLOCKED commands have explicit fallbacks |
| **D-13** | Manual smoke coverage must include login/session, task board, AI task input, WebSocket chat, scheduler/notifications, `/health`, and current Svelte routes | `19-SAFETY-BASELINE.md` § Manual Smoke Checklist — 13-item checklist covers all required categories |
| **D-14** | Phase 19 output should be a refactor playbook, not only old-to-new tables | This file (19-REFACTOR-PLAYBOOK.md) synthesizes all three artifacts, adds sequencing, shim policy, and handoff contracts |
| **D-15** | Playbook should include target structure, backend/frontend old-to-new maps, protected behavior list, verification commands, sequencing notes, and temporary shim notes | This playbook §§ Approved Backend/Frontend Target Structure, Protected Behavior List, Baseline Command Results, Sequencing Notes, Temporary Shim Policy, Phase 20/21/22 Handoff |
| **D-16** | Use separate backend and frontend tracks; Phase 20 and 21 independently plannable; Phase 22 owns integrated verification | This playbook § Sequencing Notes (diagram); §§ Phase 20 Handoff, Phase 21 Handoff, Phase 22 Handoff with clear ownership boundaries |

### Validation Command Results

Commands from `19-VALIDATION.md` run during playbook creation:

| Validation Command | Result |
|---|---|
| `rg "/api/auth\|/ws/chat\|/health\|app.main:app\|alembic" 19-SAFETY-BASELINE.md` | ✅ All patterns found |
| `rg "failure reason\|fallback\|blocked" 19-SAFETY-BASELINE.md` | ✅ All patterns found |
| `rg "backend/app/main.py\|backend/alembic/env.py\|backend/tests\|app.main:app" 19-BACKEND-MAP.md` | ✅ All patterns found |
| `rg "frontend/src/lib/api.ts\|lib/apis\|/tasks\|/invite/accept\|credentials" 19-FRONTEND-MAP.md` | ✅ All patterns found |
| `rg "## Phase 20 Handoff\|## Phase 21 Handoff\|## Phase 22 Handoff\|## Temporary Shim Policy" 19-REFACTOR-PLAYBOOK.md` | ✅ All sections present |
| `rg "STRUCT-01\|STRUCT-02\|STRUCT-03\|D-01\|D-16" 19-REFACTOR-PLAYBOOK.md` | ✅ All IDs present |
