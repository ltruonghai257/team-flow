---
phase: 15-custom-kanban-statuses
plan: 15-01
subsystem: database
tags: [fastapi, sqlalchemy, alembic, kanban-statuses, pytest]

requires: []
provides:
  - DB-backed status set schema with sub-team defaults and project override scope
  - Custom status records with stable slugs and is_done completion semantics
  - Task custom_status_id dual-write foundation while retaining legacy Task.status
affects: [phase-15-custom-kanban-statuses, phase-16-kpi-dashboard]

tech-stack:
  added: []
  patterns:
    - SQLAlchemy models with Alembic-managed schema migration
    - Dual-write transition pattern retaining legacy enum status during custom status rollout

key-files:
  created:
    - backend/alembic/versions/8a1b2c3d4e5f_add_custom_statuses.py
    - backend/tests/test_status_sets.py
  modified:
    - backend/app/models.py
    - backend/tests/test_tasks.py

key-decisions:
  - "Retained Task.status while adding Task.custom_status_id for the dual-write transition."
  - "Seeded sub-team default status sets plus a fallback unscoped default set for tasks without project sub-team context."
  - "Kept completion transition tests as xfail placeholders because endpoint is_done transition implementation is planned for 15-02."

patterns-established:
  - "Default statuses keep legacy slugs: todo, in_progress, review, done, blocked."
  - "Completion-ready status semantics live on CustomStatus.is_done instead of hardcoded TaskStatus.done."

requirements-completed: [STATUS-03, STATUS-04]

duration: 2 min
completed: 2026-04-26
---

# Phase 15 Plan 15-01: Backend Status Schema, Migration, and Seed Backfill Summary

**DB-backed Kanban status schema with seeded legacy status records, task custom_status_id backfill, and retained Task.status dual-write compatibility**

## Performance

- **Duration:** 2 min
- **Started:** 2026-04-26T07:27:47Z
- **Completed:** 2026-04-26T07:29:51Z
- **Tasks:** 4
- **Files modified:** 4

## Accomplishments

- Added `StatusSetScope`, `StatusSet`, `CustomStatus`, and `Task.custom_status_id` while preserving `Task.status`.
- Added an explicit Alembic migration that creates status tables, seeds five legacy-compatible statuses per default set, creates a fallback default set, and backfills `tasks.custom_status_id`.
- Added model-level status tests and completion transition placeholders for the 15-02 task endpoint work.
- Verified backend app compilation with `python -m compileall backend/app`.

## Task Commits

Each task was committed atomically:

1. **Task 15-01-01: Add status set models and task FK** - `a2662ba` (feat)
2. **Task 15-01-02: Create explicit Alembic migration with seed and backfill** - `556a5e9` (feat)
3. **Task 15-01-03: Add backend test stubs for status migration and completion dependencies** - `24b0c96` (test)
4. **Task 15-01-04: Run schema verification** - `0e8541a` (test)

## Files Created/Modified

- `backend/app/models.py` - Adds status set and custom status models plus `Task.custom_status_id`.
- `backend/alembic/versions/8a1b2c3d4e5f_add_custom_statuses.py` - Creates status schema, seeds defaults, and backfills tasks.
- `backend/tests/test_status_sets.py` - Covers default legacy status records and `done.is_done`.
- `backend/tests/test_tasks.py` - Covers legacy status retention, `custom_status_id`, and xfail completion transition placeholders.

## Decisions Made

- Retained `Task.status` during the custom status transition to preserve AI parsing and existing task workflows.
- Used sub-team default status sets plus an unscoped fallback status set for tasks/projects without sub-team context.
- Left endpoint-level `is_done` completion transition behavior as xfail coverage because the plan explicitly defers task update behavior to 15-02.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

- `pytest tests/test_status_sets.py tests/test_tasks.py` could not run because `pytest` is not installed on PATH: `zsh:1: command not found: pytest`.
- `python -m pytest tests/test_status_sets.py tests/test_tasks.py` also could not run because the active Python environment does not have pytest installed: `/Applications/ServBay/package/python/3.13/3.13.3/bin/python: No module named pytest`.

## Known Stubs

- `backend/tests/test_tasks.py` - `test_moving_to_is_done_status_sets_completed_at` is marked `xfail` because task endpoint transition logic is planned for 15-02.
- `backend/tests/test_tasks.py` - `test_moving_from_is_done_to_non_done_status_clears_completed_at` is marked `xfail` because task endpoint transition logic is planned for 15-02.

## Threat Flags

None - new schema surfaces are covered by the plan threat model.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

Ready for 15-02. The database foundation is present for API work to resolve effective statuses, enforce sub-team/project scoping, and implement `is_done` completion transitions.

## Verification

- PASS: `backend/app/models.py` contains `StatusSetScope`, `StatusSet`, `CustomStatus`, `Task.custom_status_id`, retained `Task.status`, and `CustomStatus.is_done`.
- PASS: migration contains `status_sets`, `custom_statuses`, `tasks.custom_status_id`, all five legacy status slugs, and no `drop_column("tasks", "status")`.
- PASS: `backend/tests/test_status_sets.py` exists and contains `is_done`.
- PASS: `backend/tests/test_tasks.py` exists and contains `completed_at` and `custom_status_id`.
- PASS: `python -m compileall backend/app`.
- BLOCKED: focused pytest command could not run due to missing local pytest dependency.

## Self-Check: PASSED

- Verified key files exist: `backend/app/models.py`, `backend/alembic/versions/8a1b2c3d4e5f_add_custom_statuses.py`, `backend/tests/test_status_sets.py`, `backend/tests/test_tasks.py`, and this summary.
- Verified task commits exist in git history: `a2662ba`, `556a5e9`, `24b0c96`, and `0e8541a`.

---
*Phase: 15-custom-kanban-statuses*
*Completed: 2026-04-26*
