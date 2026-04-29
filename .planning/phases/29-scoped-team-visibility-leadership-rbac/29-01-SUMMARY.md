---
phase: 29-scoped-team-visibility-leadership-rbac
plan: 01
subsystem: auth
tags: [rbac, visibility, sqlalchemy, pytest, alembic]

requires: []
provides:
  - Phase 29 active backend roles: manager, supervisor, assistant_manager, member
  - Shared backend visibility helpers for role and sub-team scope decisions
  - Manager and leader auth guard dependencies backed by shared visibility predicates
  - Focused backend tests for member, leader, peer-leader, and manager visibility
affects: [phase-29-plan-02, phase-29-plan-03, backend-auth, backend-routers, frontend-role-visibility]

tech-stack:
  added: [backend/pytest.ini]
  patterns:
    - Centralized visibility predicates in backend/app/services/visibility.py
    - Manager all-team scope uses None; selected sub-team scope uses explicit allowed ID list

key-files:
  created:
    - backend/app/services/visibility.py
    - backend/alembic/versions/29c1d2e3f4a5_update_user_roles_for_phase_29.py
    - backend/tests/test_visibility.py
    - backend/pytest.ini
  modified:
    - backend/app/models/enums.py
    - backend/app/utils/auth.py

key-decisions:
  - "Kept Phase 29 visibility as a shared backend service so later routers can reuse one source of truth."
  - "Mapped old-named guard imports to manager/leader behavior during the staged router rollout, without preserving an active admin role value."
  - "Added backend/pytest.ini so the exact plan verification command imports the backend app package from backend/."

patterns-established:
  - "Use is_manager, is_leader, and is_member from visibility.py instead of direct role tuple checks."
  - "Use visible_sub_team_ids and scoped_sub_team_filter for query-level scope enforcement."

requirements-completed: [VIS-01, VIS-02, VIS-03, VIS-04, VIS-07]

duration: 7 min
completed: 2026-04-29
---

# Phase 29 Plan 01: Role And Visibility Foundation Summary

**Manager-led RBAC foundation with shared backend visibility helpers and role/scope regression tests**

## Performance

- **Duration:** 7 min
- **Started:** 2026-04-29T15:27:39Z
- **Completed:** 2026-04-29T15:34:56Z
- **Tasks:** 4
- **Files modified:** 6

## Accomplishments

- Replaced the active backend role enum with `manager`, `supervisor`, `assistant_manager`, and `member`.
- Added a shared visibility service for manager, leader, member, peer-leader, visible-user, and scoped SQLAlchemy filter decisions.
- Updated auth dependencies to expose manager and leader guard behavior through the new shared predicates.
- Added focused backend tests covering all four active roles, peer leaders, manager all-team visibility, and member sub-team scope.

## Task Commits

1. **Task 1: Replace the active backend role enum and schema types** - `076444a` (feat)
2. **Task 2: Add shared visibility helpers for role and scope decisions** - `fa0f213` (feat)
3. **Task 3: Update auth dependencies to use the shared role model** - `8ad32c1` (feat)
4. **Task 4: Lock the foundation with backend visibility tests** - `5f70733` (test)

**Plan metadata:** final docs commit

## Files Created/Modified

- `backend/app/models/enums.py` - Replaced `admin` with `manager` and added `assistant_manager`.
- `backend/alembic/versions/29c1d2e3f4a5_update_user_roles_for_phase_29.py` - Adds the clean pre-release PostgreSQL enum replacement migration.
- `backend/app/services/visibility.py` - Centralizes Phase 29 role predicates, visible scope resolution, peer-leader lookup, and scoped query filters.
- `backend/app/utils/auth.py` - Adds `require_manager`, `require_leader_or_manager`, and `require_leader`; resolves sub-team context through visibility helpers.
- `backend/tests/test_visibility.py` - Covers role vocabulary, member scope, supervisor/assistant manager peer-leader scope, manager scope, auth guards, and scoped filters.
- `backend/pytest.ini` - Sets `pythonpath = .` so the plan's backend pytest command imports `app`.

## Decisions Made

- Shared backend visibility helpers are the source of truth for Phase 29 scope logic.
- Manager all-team visibility is represented by `None` for allowed sub-team IDs; explicit sub-team selection resolves to a concrete list.
- Old guard names remain as import aliases to new behavior during the staged router rollout, but active privileged checks no longer reference `UserRole.admin`.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Added backend pytest import-root config**
- **Found during:** Task 1 verification
- **Issue:** `cd backend && rtk uv run pytest tests/test_visibility.py -q` could not import `app` because the backend had no pytest config setting the import root.
- **Fix:** Added `backend/pytest.ini` with `pythonpath = .`.
- **Files modified:** `backend/pytest.ini`
- **Verification:** `cd backend && rtk uv run pytest tests/test_visibility.py -q` passes.
- **Committed in:** `076444a`

---

**Total deviations:** 1 auto-fixed (1 blocking)
**Impact on plan:** Required to run the exact plan verification command. No product behavior scope was added.

## Issues Encountered

- The first verification command needed escalated execution because `uv` accesses `/Users/haila/.cache/uv`, which is outside the workspace sandbox.
- The visibility tests initially used `pytest.fixture` for an async fixture; the project uses strict `pytest_asyncio`, so the fixture was switched to `pytest_asyncio.fixture`.

## Authentication Gates

None.

## Known Stubs

None.

## Verification

- `cd backend && rtk uv run pytest tests/test_visibility.py -q` - PASS (`9 passed, 1 warning`)
- `backend/app/models/enums.py` contains `assistant_manager` - PASS
- `backend/app/utils/auth.py` contains manager/leader guard dependencies - PASS
- `backend/app/services/visibility.py` exists and is imported by auth/tests - PASS
- `UserRole.admin` is absent from active role foundation files - PASS

## Threat Flags

| Flag | File | Description |
|------|------|-------------|
| threat_flag: schema-migration | `backend/alembic/versions/29c1d2e3f4a5_update_user_roles_for_phase_29.py` | Updates the role enum at the authenticated-route trust boundary; covered by T-29-03 mitigation and focused tests. |

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

Ready for Phase 29 Plan 02. Later router updates can reuse `backend/app/services/visibility.py` and auth guard dependencies instead of re-implementing role checks.

## Self-Check: PASSED

- Created files exist: `backend/app/services/visibility.py`, `backend/alembic/versions/29c1d2e3f4a5_update_user_roles_for_phase_29.py`, `backend/tests/test_visibility.py`, `backend/pytest.ini`.
- Task commits exist: `076444a`, `fa0f213`, `8ad32c1`, `5f70733`.
- Required verification command passed after final task commit.

---
*Phase: 29-scoped-team-visibility-leadership-rbac*
*Completed: 2026-04-29*
