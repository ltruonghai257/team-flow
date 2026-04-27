---
phase: 18-status-transition-graph
plan: 02
subsystem: api
tags: [fastapi, workflow, task-updates, project-overrides, testing]
requires:
  - phase: 18-01
    provides: status transition persistence and status-set transition endpoints
provides:
  - backend status transition enforcement for task updates
  - structured 422 blocked-transition responses
  - project override transition snapshot copying
  - transition cleanup across status delete and archive flows
affects: [tasks, statuses, kanban, project-overrides]
tech-stack:
  added: []
  patterns: [transition rules act as strict allowlist once any edge exists, project overrides snapshot both statuses and transitions]
key-files:
  created:
    - .planning/phases/18-status-transition-graph/18-02-SUMMARY.md
  modified:
    - backend/app/routers/tasks.py
    - backend/app/routers/statuses.py
    - backend/tests/test_tasks.py
    - backend/tests/test_status_sets.py
key-decisions:
  - "Transition enforcement only runs for status changes or project changes that alter status context."
  - "Legacy task statuses are mapped into the effective custom status set before workflow enforcement runs."
  - "Project overrides copy transition edges by status slug and then diverge independently from later default changes."
patterns-established:
  - "Blocked workflow moves return HTTP 422 with code status_transition_blocked and allowed_status_ids."
  - "Status deletion explicitly removes attached transition rows while archiving leaves dormant rows intact."
requirements-completed: [TRANS-02, TRANS-03]
duration: 6 min
completed: 2026-04-27
---

# Phase 18 Plan 02: Status Transition Graph Summary

**Task status updates now enforce explicit workflow edges, and project override status sets carry their own transition snapshots**

## Performance

- **Duration:** 6 min
- **Started:** 2026-04-27T02:08:05Z
- **Completed:** 2026-04-27T02:13:58Z
- **Tasks:** 5
- **Files modified:** 4

## Accomplishments

- Added backend transition enforcement for task updates, including legacy-status fallback and no-op handling.
- Returned structured `status_transition_blocked` HTTP 422 payloads with current, target, and allowed status context.
- Copied transition rules into project overrides and cleaned up transition rows during status deletion without deleting archived edges.
- Added focused API coverage for strict allowlists, ordinary task edits, legacy mapping, and override snapshots.

## Task Commits

1. **Tasks 1-4: Enforcement and status lifecycle changes** - `a3bdeb1` (`feat`)
2. **Task 5: Backend enforcement and lifecycle tests** - `40a0bad` (`test`)

**Plan metadata:** pending docs commit

## Files Created/Modified

- `backend/app/routers/tasks.py` - resolves effective status context and blocks disallowed workflow moves
- `backend/app/routers/statuses.py` - copies transitions into project overrides and removes transitions on hard delete
- `backend/tests/test_tasks.py` - covers empty graph behavior, strict allowlist blocking, legacy mapping, and ordinary edits
- `backend/tests/test_status_sets.py` - covers project override transition snapshots alongside the transition API suite

## Decisions Made

- Once any transition row exists for a status set, task movement becomes an exact-edge allowlist.
- Status and project changes share one enforcement path so project moves re-evaluate the task inside the target status context.
- Override transition copying uses slugs rather than source IDs so project snapshots point only at project-local statuses.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

- `backend/tests/test_tasks.py` had pre-existing SQLite-incompatible datetime literals in its older sprint tests. Those were normalized so the focused Wave 2 verification command could run cleanly.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Backend workflow enforcement is in place and tested.
- Phase 18-03 can wire transition-rule editing into the existing status-set manager UI.

---
*Phase: 18-status-transition-graph*
*Completed: 2026-04-27*
