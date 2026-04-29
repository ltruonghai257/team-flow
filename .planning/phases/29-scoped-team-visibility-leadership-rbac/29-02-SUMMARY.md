---
phase: 29-scoped-team-visibility-leadership-rbac
plan: 02
subsystem: auth
tags: [rbac, visibility, fastapi, pytest, invites, teams]

requires:
  - phase: 29-01
    provides: Phase 29 role enum, auth guards, and shared visibility helpers
provides:
  - Scoped user list, detail, update, role, and deactivation behavior
  - Manager-only leadership role assignment for users, invites, and direct-add
  - Scoped sub-team listing with manager-only team mutation
  - Scoped pending invite listing and cancellation
affects: [phase-29-plan-03, phase-29-plan-04, backend-routers, team-management, invite-management]

tech-stack:
  added: []
  patterns:
    - Use backend/app/services/visibility.py for role assignment and sub-team scoping
    - Use manager authority for leadership assignment and reminder proposal review

key-files:
  created:
    - .planning/phases/29-scoped-team-visibility-leadership-rbac/29-02-SUMMARY.md
  modified:
    - backend/app/routers/users.py
    - backend/app/routers/sub_teams.py
    - backend/app/routers/invites.py
    - backend/app/schemas/users.py
    - backend/app/services/visibility.py
    - backend/tests/test_visibility.py
    - backend/tests/test_sub_teams.py

key-decisions:
  - "Kept managers as the only role allowed to assign manager, supervisor, and assistant_manager privileges."
  - "Allowed supervisors and assistant managers to manage only member users and pending member invites inside visible sub-team scope."
  - "Kept sub-team creation, update, delete, and reminder proposal review under manager authority while allowing leaders to list only their allowed teams."

patterns-established:
  - "Use can_assign_role before mutating invite or user role state."
  - "Use visible_sub_team_ids with scoped_sub_team_filter for scoped invite and sub-team lists."

requirements-completed: [VIS-02, VIS-03, VIS-04, VIS-06, VIS-07]

duration: 15 min
completed: 2026-04-29
---

# Phase 29 Plan 02: Scoped Management RBAC Summary

**Manager-only leadership assignment with scoped user, team, invite, and direct-add management**

## Performance

- **Duration:** 15 min
- **Started:** 2026-04-29T15:39:34Z
- **Completed:** 2026-04-29T15:54:10Z
- **Tasks:** 4
- **Files modified:** 7

## Accomplishments

- User list/detail/update endpoints now use Phase 29 visibility helpers and block out-of-scope mutations.
- Sub-team listing is scoped for supervisors and assistant managers, while create/update/delete and reminder proposal review are manager-only.
- Invite and direct-add flows enforce manager-only leadership assignment and scoped member-only leader management.
- Regression tests cover manager, supervisor, assistant manager, member, scoped pending invites, direct-add, and out-of-scope mutation paths.

## Task Commits

1. **Task 1: Scope user list, detail, and role update endpoints** - `cef1f31` (feat)
2. **Task 2: Scope sub-team listing and management** - `4372ef7` (feat)
3. **Task 3: Enforce invite and direct-add role/scope rules** - `a9c3c21` (feat)
4. **Task 4: Expand management regression tests** - `c475a8b` (test)

**Plan metadata:** final docs commit

## Files Created/Modified

- `backend/app/routers/users.py` - Applies scoped user list/detail/update behavior and manager-only role/deactivation controls.
- `backend/app/schemas/users.py` - Validates user update role payloads with the Phase 29 `UserRole` enum.
- `backend/app/routers/sub_teams.py` - Uses manager authority for team mutation and reminder review, with scoped leader listing.
- `backend/app/routers/invites.py` - Enforces manager-only leadership invites/direct-add and scoped pending invite list/cancel behavior.
- `backend/app/services/visibility.py` - Adds `can_assign_role` for shared role-assignment checks.
- `backend/tests/test_visibility.py` - Covers user management, invite, direct-add, pending invite, and acceptance scope regressions.
- `backend/tests/test_sub_teams.py` - Covers manager-only sub-team mutation, scoped team listing, and manager reminder review behavior.

## Decisions Made

- Managers remain the only role that can assign leadership roles or mutate sub-team structures.
- Supervisors and assistant managers can invite/direct-add only `member` users inside their allowed scope.
- Pending invites are filtered with the same sub-team visibility helper used by other scoped lists.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Fixed test auth cookie precedence**
- **Found during:** Task 3
- **Issue:** API tests logged in multiple roles, but auth prefers cookies over bearer headers, so a later login could override the intended Authorization header.
- **Fix:** Cleared test-client cookies before and after visibility-test login helper calls.
- **Files modified:** `backend/tests/test_visibility.py`
- **Verification:** `cd backend && rtk uv run pytest tests/test_visibility.py -q` passed.
- **Committed in:** `a9c3c21`

**2. [Rule 3 - Blocking] Removed auth rate-limit coupling from sub-team tests**
- **Found during:** Task 4
- **Issue:** The combined regression command exceeded the `/api/auth/token` test rate limit after adding more API coverage.
- **Fix:** Sub-team tests now mint test JWTs directly from fixture users instead of hitting the login endpoint.
- **Files modified:** `backend/tests/test_sub_teams.py`
- **Verification:** `cd backend && rtk uv run pytest tests/test_visibility.py tests/test_sub_teams.py -q` passed.
- **Committed in:** `c475a8b`

---

**Total deviations:** 2 auto-fixed (2 blocking)
**Impact on plan:** Both fixes were limited to test reliability and were required to run the exact plan verification command.

## Issues Encountered

- The focused pytest command reports one existing Pydantic deprecation warning from `app/core/config.py`.
- The worktree had unrelated uncommitted milestone and frontend test changes before this plan started; they were left untouched.

## Authentication Gates

None.

## Known Stubs

None.

## Verification

- `cd backend && rtk uv run pytest tests/test_visibility.py -q` - PASS (`18 passed, 1 warning`)
- `cd backend && rtk uv run pytest tests/test_visibility.py tests/test_sub_teams.py -q` - PASS (`23 passed, 1 warning`)
- Managers can assign leadership roles in tests - PASS
- Supervisors and assistant managers cannot assign leadership roles in tests - PASS
- Pending invites and sub-team lists are scoped in tests - PASS

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

Ready for Phase 29 Plan 03. The remaining people-aware surfaces can reuse the same `visible_sub_team_ids`, `scoped_sub_team_filter`, and role-assignment patterns.

## Self-Check: PASSED

- Summary file exists at `.planning/phases/29-scoped-team-visibility-leadership-rbac/29-02-SUMMARY.md`.
- Task commits exist: `cef1f31`, `4372ef7`, `a9c3c21`, `c475a8b`.
- Required plan verification command passed after the final task commit.

---
*Phase: 29-scoped-team-visibility-leadership-rbac*
*Completed: 2026-04-29*
