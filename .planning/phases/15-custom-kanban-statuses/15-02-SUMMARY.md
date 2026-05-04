---
phase: 15-custom-kanban-statuses
plan: 15-02
subsystem: backend-api
tags: [fastapi, sqlalchemy, status-sets, dual-write, completion-semantics]

requires:
  - DB-backed status set schema with sub-team defaults and project override scope (15-01)
provides:
  - Status-set management API at /api/status-sets (default, effective, reorder, delete, override)
  - Task dual-write: custom_status_id resolved from explicit ID or legacy enum slug mapping
  - is_done-based completed_at transitions replacing hardcoded TaskStatus.done checks
affects: [phase-15-custom-kanban-statuses, phase-16-kpi-dashboard]

tech-stack:
  added: []
  patterns:
    - Status scope resolution: project override → sub-team default → unscoped fallback
    - Dual-write with legacy enum mapping at create/update time

key-files:
  created:
    - backend/app/routers/statuses.py
  modified:
    - backend/app/schemas.py
    - backend/app/routers/tasks.py
    - backend/app/main.py

key-decisions:
  - "Slug is computed once at status creation; name updates do not regenerate slug (stable canonical key per D-05)."
  - "Task update: custom_status_id takes priority over legacy status for is_done resolution."
  - "create_task and update_task both call _resolve_custom_status so AI/legacy inputs map to DB statuses."

requirements-completed: [STATUS-01, STATUS-02, STATUS-04]

duration: 12 min
completed: 2026-04-26
---

# Phase 15 Plan 15-02: Backend Status APIs and Task Dual-Write Summary

**Status-set management API and task dual-write: custom_status_id resolved at create/update, is_done drives completed_at transitions**

## Performance

- **Duration:** 12 min
- **Tasks:** 5
- **Files modified:** 4

## Accomplishments

- Added `CustomStatusOut`, `StatusSetOut`, `CustomStatusCreate/Update`, `StatusReorderPayload`, `StatusDeletePayload`, `ProjectStatusRevertPayload` schemas; extended `TaskCreate/Update/Out` with `custom_status_id` and `custom_status`.
- Created `backend/app/routers/statuses.py` with 8 endpoints: `GET /default`, `GET /effective`, `POST /default/statuses`, `PATCH /statuses/{id}`, `POST /{set_id}/reorder`, `POST /statuses/{id}/delete`, `POST /projects/{id}/override`, `DELETE /projects/{id}/override`.
- Implemented safe delete (archive / move_delete / hard delete with task-count guard), project override creation via copy, and revert with slug-matching plus `fallback_mappings` gate.
- Updated `tasks.py`: all list/get/create/update queries include `selectinload(Task.custom_status)`; `_resolve_custom_status` helper maps explicit ID or legacy enum to DB status; `is_done` drives `completed_at` instead of `TaskStatus.done` comparison.
- Registered `statuses.router` in `main.py`.
- `python -m compileall backend/app` exits 0.

## Task Commits

1. **Task 15-02-01: Add status schemas** — `51acb74`
2. **Task 15-02-02/03: Create status-set router with safe delete, archive, reorder, override** — `a1a826c`
3. **Task 15-02-04: Update task create/list/update for custom status dual-write** — `cbe66e1`
4. **Task 15-02-05: Register router and verify compile** — `5b39b06`

## Deviations from Plan

**None** — plan executed exactly as written. Tasks 15-02-02 and 15-02-03 were implemented together in a single file creation since they both wrote to `statuses.py`.

## Verification

- PASS: `backend/app/schemas.py` contains `class CustomStatusOut`, `class StatusSetOut`, `class StatusReorderPayload`, `class StatusDeletePayload`, `custom_status_id`, `custom_status`.
- PASS: `backend/app/routers/statuses.py` exists with `APIRouter(prefix="/api/status-sets"`, `_status_slug`, `Select a sub-team before editing default statuses`, `@router.get("/default"`, `@router.get("/effective"`, `@router.post("/{status_set_id}/reorder"`, `@router.post("/statuses/{status_id}/delete"`.
- PASS: `statuses.py` contains `mode == "archive"`, `mode == "move_delete"`, `replacement_status_id`, `Statuses with tasks must be moved or archived before they can be deleted.`, `fallback_mappings`, `slug`.
- PASS: `backend/app/routers/tasks.py` contains `selectinload(Task.custom_status)`, `custom_status_id`, `is_done`.
- PASS: Old `new_status == TaskStatus.done and task.status != TaskStatus.done` branch removed.
- PASS: `backend/app/main.py` contains `statuses` and `app.include_router(statuses.router)`.
- PASS: `python -m compileall backend/app` exits 0.

## Self-Check: PASSED

- All key files present on disk.
- All 4 task commits visible in git history.

---
*Phase: 15-custom-kanban-statuses*
*Completed: 2026-04-26*
