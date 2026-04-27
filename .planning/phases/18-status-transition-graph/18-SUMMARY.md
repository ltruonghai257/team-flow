# Phase 18 Summary: Status Transition Graph (Workflow Rules)

**Status:** COMPLETE  
**Completed:** 2026-04-27  
**Plans executed:** 4/4 (18-01 → 18-04)

---

## What Was Done

### Wave 1 — Plan 18-01: Status Transition Graph Persistence and API
- Added `StatusTransition` model with unique constraint on `(status_set_id, from_status_id, to_status_id)` and no-self-transition protection
- Created Alembic migration `d3e4f5a6b7c8_add_status_transitions.py`
- Added transition list, replace, and delete schemas with `BlockedTransitionDetail` for structured error responses
- Implemented `/api/status-sets/{id}/transitions` endpoints (GET, POST replace, DELETE)
- Added archived-status filtering (`include_archived=true` parameter)
- Created backend test harness with per-test SQLite databases and dependency overrides
- Added focused backend API tests for transition auth, duplicate rejection, empty-list compatibility, and archived filtering

### Wave 2 — Plan 18-02: Backend Task Update Enforcement
- Resolved effective status context (default status set or project override) in task updates
- Implemented strict allowlist enforcement: once any transition edge exists, task movement requires exact edge match
- Returned HTTP 422 with `status_transition_blocked` error code, including current/target status IDs and allowed target IDs
- Added legacy status fallback: maps legacy task statuses into effective custom status set before enforcement
- Implemented project override transition snapshot copying (by slug, then independent)
- Added transition cleanup on status hard delete (archived transitions remain dormant)
- Added backend tests for strict allowlists, ordinary edits, legacy mapping, and override snapshots

### Wave 3 — Plan 18-03: Transition Management UI
- Added transition API client types and methods (`getTransitions`, `replaceTransitions`) to `frontend/src/lib/api.ts`
- Created `StatusTransitionEditor.svelte` with matrix-first editing using active statuses only, disabled self-transitions, explicit "Generate linear flow" button, and explicit "Save transitions" button
- Created `StatusTransitionPreview.svelte` with read-only graph preview, status color dots, compact edges, truncation for long names, and non-blocking workflow warnings
- Integrated transition editor into `StatusSetManager.svelte` behind compact "Statuses" / "Transition rules" tabs
- Transition matrix state is local draft UI until user explicitly saves

### Wave 4 — Plan 18-04: Task Workflow Enforcement UI
- Added transition-aware helpers to `/tasks` page to load effective status set transitions and compute allowed targets
- Updated edit-task status select to show allowed targets plus current status in DB-backed mode
- Preserved legacy edit fallback when no DB-backed statuses loaded (binds to legacy `status` field)
- Added Kanban restriction hints and client-side invalid-drop blocking with optimistic-state rollback on blocked moves
- Preserved structured blocked-transition detail in shared API helper for UI inspection
- Fixed unrelated `unknown` catch annotations in `login` and `register` routes for frontend check compliance

---

## Artifacts

- `backend/alembic/versions/d3e4f5a6b7c8_add_status_transitions.py` — migration
- `backend/app/models.py` — `StatusTransition` model
- `backend/app/schemas.py` — transition schemas and `BlockedTransitionDetail`
- `backend/app/routers/statuses.py` — transition CRUD endpoints
- `backend/app/routers/tasks.py` — transition enforcement in task updates
- `backend/tests/conftest.py` — async FastAPI database test harness
- `backend/tests/test_status_sets.py` — transition API and enforcement tests
- `backend/tests/test_tasks.py` — task update enforcement tests
- `frontend/src/lib/api.ts` — transition API client methods
- `frontend/src/lib/components/statuses/StatusTransitionEditor.svelte` — matrix editor
- `frontend/src/lib/components/statuses/StatusTransitionPreview.svelte` — read-only preview
- `frontend/src/lib/components/statuses/StatusSetManager.svelte` — integrated tabs
- `frontend/src/routes/tasks/+page.svelte` — transition-aware task board
- `frontend/src/lib/components/tasks/KanbanBoard.svelte` — drag-drop enforcement

---

## Must-Haves Verification

| Must-Have | Status |
|---|---|
| `StatusTransition` model with unique constraint exists | ✅ |
| `GET/POST/DELETE /status-sets/{id}/transitions` endpoints work | ✅ |
| Task update rejects moves not in allowed transition list with HTTP 422 when rules defined | ✅ |
| Kanban drag-drop enforces transitions client-side with toast on blocked moves | ✅ |
| Task edit form status dropdown filters to permitted next statuses only | ✅ |
| Transition matrix UI in `StatusSetManager` (supervisor/admin only) | ✅ |
| Zero regressions when no transitions defined (free movement preserved) | ✅ |

---

## Decisions Made

- Empty transition lists are a saved state, not an error condition — enforcement remains backward-compatible until rules are configured
- Archived statuses excluded from normal transition reads and cannot be written as endpoints
- Once any transition row exists for a status set, task movement becomes an exact-edge allowlist
- Status and project changes share one enforcement path so project moves re-evaluate task inside target status context
- Override transition copying uses slugs rather than source IDs so project snapshots point only at project-local statuses
- Transition editing uses two-tab layout in `StatusSetManager` to avoid crowding existing management surface
- Generated linear flow is draft-only until `Save transitions` (explicit-save requirement)
- Workflow warnings are informational and derived from current selected matrix state
- Pre-existing backend test failures waived as outside Phase 18 scope (Phase 18-specific tests pass)

---

## Requirements Completed

- TRANS-01: Status transition persistence and API
- TRANS-02: Backend enforcement and project override lifecycle
- TRANS-03: Task workflow enforcement UI

---

*Phase: 18-status-transition-graph*
*Completed: 2026-04-27*
