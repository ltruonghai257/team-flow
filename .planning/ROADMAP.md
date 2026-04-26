# Roadmap: TeamFlow

_Updated: 2026-04-26_

---

## Milestone History

### Milestone 1: Production-Ready Team Management Platform

**Status:** Complete (Phases 1-11)
**Completed:** 2026-04-24

| Phase | Name | Requirements | Status |
|-------|------|--------------|--------|
| 1 | Production Hardening | REQ-01 | Done |
| 2 | RBAC & Role Model | REQ-07 | Done |
| 3 | Supervisor Performance Dashboard | REQ-02 | Done |
| 4 | Team Timeline View | REQ-03 | Done |
| 5 | Enhanced AI Features | REQ-04 | Done |
| 6 | Mobile-Responsive UI | REQ-06 | Done |
| 7 | Azure Deployment & CI/CD | REQ-05 | Done |
| 8 | User Invite & Team Management | - | Done |
| 9 | Verification Docs (Phases 1-3) | - | Done |
| 10 | Verification Docs (Phases 4-5) | - | Done |
| 11 | Verification Docs (Phases 6-8) | - | Done |

### Milestone 2.0: Team Hierarchy, Sprints & Advanced Analytics

**Status:** In progress — Phases 17–18 remaining before v2.1 structural refactor begins
**Phases:** 12-18

| Phase | Name | Status |
|-------|------|--------|
| 12 | Task Types | ✅ Done |
| 13 | Multi-team Hierarchy & Timeline Visibility | ✅ Done |
| 14 | Sprint Model | ✅ Done |
| 15 | Custom Kanban Statuses | ✅ Done |
| 16 | Advanced KPI Dashboard | ✅ Done |
| 17 | Sprint & Release Reminders | 🗂 Not started |
| 18 | Status Transition Graph (Workflow Rules) | 🗂 Not started |

**Phase 17: Sprint & Release Reminders**
- **Goal:** Team members and supervisors receive in-app notifications N days before sprint end and milestone due dates; configurable lead time; no duplicate reminders via `EventNotification` rows
- **Depends on:** Phase 13 (team membership for fanout), Phase 14 (sprint model for trigger events)
- **Requirements:** REMIND-01, REMIND-02
- **Plans:**
  - **Wave 1:** `17-01` - Backend reminder settings, proposal approval, migration, and notification event contracts
  - **Wave 2** *(blocked on Wave 1 completion)*: `17-02` - Reminder recipient generation and scheduler reconciliation
  - **Wave 3** *(blocked on Waves 1-2 completion)*: `17-03` - Sprint/milestone date-change rebuild hooks
  - **Wave 4** *(blocked on Wave 1 completion)*: `17-04` - `/team` reminder settings and proposal review UI
  - **Wave 5** *(blocked on Waves 1-4 completion)*: `17-05` - Notification copy, bell routing, target handling, and final verification
- **Cross-cutting constraints:**
  - Reminder settings are scoped by sub-team with a default 2-day shared lead time.
  - Supervisors propose setting changes; admins approve/apply them on `/team`.
  - Generated sprint/milestone reminders use existing `EventNotification` delivery and prevent duplicate generated rows without breaking existing schedule/task reminder offsets.
  - Recipient fanout includes participants plus responsible supervisors, deduped per user per event.
- **Success Criteria:**
  1. All sprint participants receive an in-app notification N days before sprint end date (default 2 days); N is configurable per sub-team by supervisor/admin
  2. Milestone due-date reminders are sent to all project members
  3. Duplicate reminders are prevented via `EventNotification` unique constraint on `(event_type, event_ref_id, user_id)`
  4. Reminders are delivered through the existing 60s notification poll

**Phase 18: Status Transition Graph (Workflow Rules)**
- **Goal:** Add directed graph of allowed status transitions per status set (YouTrack-style). Any task move not permitted by the graph is rejected. Empty graph = free movement (fully backward-compatible).
- **Depends on:** Phase 15 (custom status model)
- **Requirements:** TRANS-01, TRANS-02, TRANS-03
- **Success Criteria:**
  1. `StatusTransition` model with `(status_set_id, from_status_id, to_status_id)` unique constraint exists and is migrated
  2. `GET/POST/DELETE /status-sets/{id}/transitions` endpoints work; supervisor/admin only for write
  3. Task update rejects moves not in allowed transition list with HTTP 422 when rules are defined
  4. Kanban drag-drop enforces transitions client-side with a toast on blocked moves
  5. Task edit form status dropdown filters to permitted next statuses only
  6. Transition matrix UI in `StatusSetManager` (supervisor/admin only)
  7. Zero regressions when no transitions are defined (free movement preserved)

**Sequencing:** Complete Phases 16, 17, and 18 first, then begin Milestone v2.1 structural refactor.

---

## Milestone v2.1: Open WebUI-Style Project Structure Refactor

> **Starts after Milestone 2.0 (Phases 16–18) is complete.**

**Goal:** Refactor TeamFlow's FastAPI backend and SvelteKit frontend into a clearer Open WebUI-inspired structure while preserving behavior.

**Reference repo:** `https://github.com/open-webui/open-webui`

**Definition of Done:** Backend and frontend folders follow the agreed Open WebUI-inspired target structure; imports, runtime entrypoints, Docker/Azure paths, Alembic, tests, and SvelteKit build/check all work; critical user flows behave the same as before the refactor.

---

## Phases

- [ ] **Phase 19: Refactor Map & Safety Baseline** — Document target structure, map current files to new locations, identify protected behavior, and establish pre-move verification commands
- [ ] **Phase 20: Backend Package Restructure** — Move FastAPI code toward an Open WebUI-style package layout and update imports, router registration, Alembic config, tests, and runtime targets
- [ ] **Phase 21: Frontend SvelteKit Structure** — Move frontend API clients/types/utilities into Open WebUI-style `src/lib` groups while preserving routes and UI behavior
- [ ] **Phase 22: Runtime Integration & Regression Verification** — Update Docker/dev/Azure entrypoints, run full checks, perform smoke tests, and document old-to-new paths

---

## Phase Details

### Phase 19: Refactor Map & Safety Baseline

**Goal:** Create a concrete migration map before moving code so the refactor stays surgical and verifiable.
**Depends on:** Nothing
**Requirements:** STRUCT-01, STRUCT-02, STRUCT-03

**Success Criteria:**

1. Target backend structure is documented, including package root, routers, models/domain modules, schemas, migrations, utils, socket/websocket, config, and app entrypoint.
2. Target frontend structure is documented, including `src/lib/apis`, `components`, `stores`, `types`, `utils`, and route boundaries.
3. Current file-to-target mapping exists for backend and frontend files that will move.
4. Protected behavior list exists for API routes, auth/session behavior, Svelte routes, WebSocket chat, scheduler jobs, AI task input, Docker runtime, and Alembic migrations.
5. Pre-refactor verification commands are run or explicitly documented if blocked by environment.

**Plans:** TBD
**UI hint:** no

### Phase 20: Backend Package Restructure

**Goal:** Reorganize backend code into a maintainable Open WebUI-inspired FastAPI package layout without changing API behavior.
**Depends on:** Phase 19
**Requirements:** BACK-01, BACK-02, BACK-03, BACK-04, BACK-05

**Success Criteria:**

1. Backend package structure matches the approved target map and has clear module boundaries for routers, schemas, models/domain modules, config, utils, migrations, and socket/websocket code.
2. FastAPI app startup, router registration, CORS, rate limiting, scheduler startup/shutdown, WebSocket routing, and `/health` response remain behaviorally unchanged.
3. Alembic can locate metadata and run migrations against the new package paths without rewriting existing migration history.
4. Backend tests import the new package paths and pass.
5. Temporary compatibility shims, if needed, are documented and limited to migration support.

**Plans:** TBD
**UI hint:** no

### Phase 21: Frontend SvelteKit Structure

**Goal:** Reorganize frontend shared code into Open WebUI-style SvelteKit folders while preserving existing routes and UI behavior.
**Depends on:** Phase 19
**Requirements:** FRONT-01, FRONT-02, FRONT-03, FRONT-04, FRONT-05

**Success Criteria:**

1. Frontend shared code uses `src/lib/apis`, `src/lib/components`, `src/lib/stores`, `src/lib/types`, and `src/lib/utils` consistently.
2. API client behavior remains stable after splitting feature-focused API modules.
3. Shared types are centralized where useful and imported by routes/components without introducing circular dependencies.
4. Current route URLs keep working: `/`, `/tasks`, `/projects`, `/milestones`, `/team`, `/timeline`, `/performance`, `/schedule`, `/ai`, `/login`, `/register`, and invite acceptance.
5. No visual redesign is introduced as part of this phase.

**Plans:** TBD
**UI hint:** no

### Phase 22: Runtime Integration & Regression Verification

**Goal:** Make the refactored structure production-safe by updating runtime entrypoints and verifying critical flows.
**Depends on:** Phase 20, Phase 21
**Requirements:** RUN-01, RUN-02, RUN-03, VERIFY-01, VERIFY-02, VERIFY-03, VERIFY-04

**Success Criteria:**

1. Dockerfile, compose/dev scripts, Azure startup commands, and uvicorn target reference the refactored backend app.
2. Frontend check and production build pass.
3. Backend tests pass.
4. Smoke checks pass for login/session, task board load, AI task input, WebSocket chat connection, scheduler/notifications, and `/health`.
5. Developer notes document old-to-new import paths, moved directories, and any temporary compatibility shims.

**Plans:** TBD
**UI hint:** no

---

## Progress Table

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 16. Advanced KPI Dashboard | 0/5 | Planned | - |
| 17. Sprint & Release Reminders | 0/5 | Planned | - |
| 18. Status Transition Graph | 0/? | Not started | - |
| 19. Refactor Map & Safety Baseline | 0/? | Not started | - |
| 20. Backend Package Restructure | 0/? | Not started | - |
| 21. Frontend SvelteKit Structure | 0/? | Not started | - |
| 22. Runtime Integration & Regression Verification | 0/? | Not started | - |

---

## Phase Sequencing

```text
Milestone 2.0 (remaining):
Phase 16 - Advanced KPI Dashboard
Phase 17 - Sprint & Release Reminders
Phase 18 - Status Transition Graph

Milestone v2.1 (starts after Phase 18):
Phase 19 - Refactor Map & Safety Baseline
  ├─ Phase 20 - Backend Package Restructure
  └─ Phase 21 - Frontend SvelteKit Structure
       └─ Phase 22 - Runtime Integration & Regression Verification
```

Phase 20 and Phase 21 can be planned independently after Phase 19, but Phase 22 must wait for both because it verifies integrated runtime behavior.

---

## Coverage

| Requirement | Phase | Status |
|-------------|-------|--------|
| REMIND-01 | Phase 17 | Pending |
| REMIND-02 | Phase 17 | Pending |
| TRANS-01 | Phase 18 | Pending |
| TRANS-02 | Phase 18 | Pending |
| TRANS-03 | Phase 18 | Pending |
| STRUCT-01 | Phase 19 | Pending |
| STRUCT-02 | Phase 19 | Pending |
| STRUCT-03 | Phase 19 | Pending |
| BACK-01 | Phase 20 | Pending |
| BACK-02 | Phase 20 | Pending |
| BACK-03 | Phase 20 | Pending |
| BACK-04 | Phase 20 | Pending |
| BACK-05 | Phase 20 | Pending |
| FRONT-01 | Phase 21 | Pending |
| FRONT-02 | Phase 21 | Pending |
| FRONT-03 | Phase 21 | Pending |
| FRONT-04 | Phase 21 | Pending |
| FRONT-05 | Phase 21 | Pending |
| RUN-01 | Phase 22 | Pending |
| RUN-02 | Phase 22 | Pending |
| RUN-03 | Phase 22 | Pending |
| VERIFY-01 | Phase 22 | Pending |
| VERIFY-02 | Phase 22 | Pending |
| VERIFY-03 | Phase 22 | Pending |
| VERIFY-04 | Phase 22 | Pending |

**Coverage: 25/25 requirements mapped**
