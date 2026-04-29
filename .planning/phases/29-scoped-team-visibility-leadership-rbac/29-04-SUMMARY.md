---
phase: 29-scoped-team-visibility-leadership-rbac
plan: 04
subsystem: ui
tags: [rbac, sveltekit, playwright, seed-data, alembic]

requires:
  - phase: 29-scoped-team-visibility-leadership-rbac
    provides: Backend Phase 29 role model, scoped visibility helpers, and endpoint enforcement
provides:
  - Frontend manager/supervisor/assistant_manager/member role helpers and navigation filtering
  - Team page controls that hide leadership assignment from scoped leaders and members
  - Demo seed reset data with manager, supervisors, assistant manager, and members across two sub-teams
  - Browser coverage for navigation and team role visibility
affects: [frontend-navigation, team-management, demo-seed, phase-29-rbac]

tech-stack:
  added: []
  patterns:
    - Role-aware frontend affordances derive from auth store helpers
    - Browser role coverage uses mocked API responses for deterministic visibility assertions

key-files:
  created:
    - frontend/tests/team-visibility.spec.ts
  modified:
    - frontend/src/lib/stores/auth.ts
    - frontend/src/lib/navigation/sidebar.ts
    - frontend/src/routes/+layout.svelte
    - frontend/src/routes/team/+page.svelte
    - frontend/tests/navigation-groups.spec.ts
    - backend/app/scripts/seed_demo.py
    - backend/alembic/versions/29c1d2e3f4a5_update_user_roles_for_phase_29.py

key-decisions:
  - "Manager replaces obsolete admin meaning in frontend role helpers, navigation, team UI, and demo seed data."
  - "Supervisors and assistant managers keep member-management affordances but only managers see leadership role assignment options."
  - "Demo reset seeds two sub-teams so scoped role visibility can be exercised locally."

patterns-established:
  - "Frontend role helpers expose manager/leader/member concepts instead of checking raw legacy role strings."
  - "Visibility tests mock /api/auth/me and page data endpoints to assert UI affordances by role without backend fixture coupling."

requirements-completed: [VIS-01, VIS-02, VIS-03, VIS-04, VIS-05, VIS-06, VIS-07]

duration: 17 min
completed: 2026-04-29
---

# Phase 29 Plan 04: Frontend RBAC Visibility and Demo Seed Summary

**Manager/leader/member frontend visibility with deterministic Playwright coverage and a clean demo reset for the four-role model**

## Performance

- **Duration:** 17 min
- **Started:** 2026-04-29T16:31:17Z
- **Completed:** 2026-04-29T16:48:55Z
- **Tasks:** 4 completed
- **Files modified:** 15

## Accomplishments

- Replaced frontend role assumptions with `manager`, `supervisor`, `assistant_manager`, and `member` helpers.
- Updated grouped navigation and `/team` UI so inaccessible privileged actions are removed instead of disabled.
- Added mocked Playwright coverage for manager, scoped leader, and member UI states.
- Refreshed `seed_demo.py` to reseed manager/supervisor/assistant-manager/member accounts across Engineering and Product sub-teams.
- Fixed the existing PostgreSQL enum migration so the documented seed reset path works locally.

## Task Commits

1. **Task 1: Update frontend role typing, navigation, and layout guards** - `f57bb1c` (feat)
2. **Task 2: Update the Team page management affordances** - `5d05ab1` (feat)
3. **Task 3: Refresh demo seed data for the new leadership model** - `0de3555` (feat)
4. **Task 4: Run final RBAC regression verification** - `d45a6bf` (test)

## Files Created/Modified

- `frontend/tests/team-visibility.spec.ts` - Browser role-affordance coverage for manager, supervisor, assistant manager, and member.
- `frontend/tests/navigation-groups.spec.ts` - Navigation coverage for all four active roles and removed Performance access for members.
- `frontend/src/lib/stores/auth.ts` - Active role union and derived manager/leader helpers.
- `frontend/src/lib/navigation/sidebar.ts` - Role-aware grouped navigation filtering for manager and scoped leaders.
- `frontend/src/routes/+layout.svelte` - Layout guard and manager-only sub-team selector wiring.
- `frontend/src/routes/team/+page.svelte` - Team, invite, direct-add, reminder, and sub-team controls aligned to the new role model.
- `backend/app/scripts/seed_demo.py` - Demo reset data for manager/supervisor/assistant-manager/member roles across two sub-teams.
- `backend/alembic/versions/29c1d2e3f4a5_update_user_roles_for_phase_29.py` - PostgreSQL enum migration fix for clean role reset.

## Verification

- `cd frontend && bun run check` - PASS, 0 errors; existing warning baseline remains.
- `cd frontend && bun x playwright test tests/navigation-groups.spec.ts --workers=1` - PASS, 11 passed.
- `cd frontend && bun x playwright test tests/team-visibility.spec.ts --workers=1` - PASS, 4 passed.
- `cd backend && python -m app.scripts.seed_demo` - PASS after applying existing Phase 29 migration.
- `cd backend && rtk uv run pytest tests/test_visibility.py tests/test_sub_teams.py tests/test_projects.py tests/test_tasks.py tests/test_timeline.py tests/test_milestones.py tests/test_board.py tests/test_knowledge_sessions.py -q` - PASS, 52 passed, 2 xfailed, 1 warning.
- `cd frontend && bun x playwright test tests/navigation-groups.spec.ts tests/team-visibility.spec.ts --workers=1` - PASS, 15 passed.

## Decisions Made

- Manager is the only frontend role that can assign leadership roles.
- Supervisors and assistant managers retain member-management affordances, with backend scope enforcement remaining authoritative.
- Demo seed data adds a Product Team to exercise multi-team visibility while preserving the existing KPI-heavy demo task set.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Removed stale frontend role references outside the initial navigation files**
- **Found during:** Task 1
- **Issue:** `bun run check` failed because active frontend routes still imported `isSupervisor` or checked obsolete `admin` role strings after the auth store role union changed.
- **Fix:** Updated related active frontend role checks in Projects, Tasks, Updates, Knowledge Sessions, Register, timeline API typing, and request comments to the manager/leader role model.
- **Files modified:** `frontend/src/routes/projects/+page.svelte`, `frontend/src/routes/tasks/+page.svelte`, `frontend/src/routes/updates/+page.svelte`, `frontend/src/routes/schedule/knowledge-sessions/+page.svelte`, `frontend/src/routes/register/+page.svelte`, `frontend/src/lib/apis/timeline.ts`, `frontend/src/lib/apis/request.ts`
- **Verification:** `cd frontend && bun run check`; `rg -n "admin|isSupervisor|isAdmin" frontend/src`
- **Committed in:** `f57bb1c`

**2. [Rule 3 - Blocking] Fixed PostgreSQL enum migration for the seed reset path**
- **Found during:** Task 3
- **Issue:** `python -m app.scripts.seed_demo` could not insert `manager` because the local PostgreSQL enum was not migrated, and the existing migration failed while dropping a renamed enum type with dependent defaults.
- **Fix:** Dropped role defaults before changing enum types and dropped the correctly renamed `userrole_old` type.
- **Files modified:** `backend/alembic/versions/29c1d2e3f4a5_update_user_roles_for_phase_29.py`
- **Verification:** `cd backend && alembic upgrade heads`; `cd backend && python -m app.scripts.seed_demo`
- **Committed in:** `0de3555`

---

**Total deviations:** 2 auto-fixed (2 blocking)
**Impact on plan:** Both fixes were required to complete the specified verification and kept scope within Phase 29 role visibility and clean reset behavior.

## Issues Encountered

- Playwright needs local dev-server socket access outside the filesystem sandbox; reran browser specs with approved escalation.
- `uv` needed access to the user-level cache for backend tests; reran backend regression with approved escalation.
- Existing `svelte-check` warnings remain in pre-existing files; no new errors were introduced.

## Known Stubs

None.

## Threat Flags

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

Phase 29 Plan 04 completes the frontend, demo data, and final regression pass for scoped leadership RBAC. Phase 29 is ready for verification or milestone closeout.

## Self-Check: PASSED

- Found summary file at `.planning/phases/29-scoped-team-visibility-leadership-rbac/29-04-SUMMARY.md`.
- Found task commits `f57bb1c`, `5d05ab1`, `0de3555`, and `d45a6bf` in git history.
- No tracked file deletions were introduced by task commits.

---
*Phase: 29-scoped-team-visibility-leadership-rbac*
*Completed: 2026-04-29*
