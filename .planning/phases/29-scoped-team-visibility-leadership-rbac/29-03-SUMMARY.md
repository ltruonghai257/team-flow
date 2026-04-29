---
phase: 29-scoped-team-visibility-leadership-rbac
plan: 03
subsystem: api
tags: [fastapi, sqlalchemy, rbac, visibility, pytest]
requires:
  - phase: 29-01
    provides: shared manager/leader/member visibility helpers
  - phase: 29-02
    provides: scoped user, team, and invite management
provides:
  - backend project and task list/detail/write endpoints scoped by Phase 29 visibility
  - timeline and milestone planning payloads scoped by visible project/team data
  - collaboration, knowledge, notification, and performance surfaces updated to manager/leader scope
  - cross-surface leak-prevention regression tests
affects: [projects, tasks, timeline, milestones, updates, board, knowledge, notifications, performance]
tech-stack:
  added: []
  patterns:
    - shared visibility helpers applied at backend query boundaries
    - direct-ID endpoints return 404/403 for out-of-scope records
key-files:
  created:
    - backend/alembic/versions/19bc99b2b9ee_add_milestone_decisions.py
  modified:
    - backend/app/routers/projects.py
    - backend/app/routers/tasks.py
    - backend/app/routers/timeline.py
    - backend/app/routers/milestones.py
    - backend/app/routers/updates.py
    - backend/app/routers/knowledge_sessions.py
    - backend/app/routers/notifications.py
    - backend/app/routers/performance.py
    - backend/app/services/visibility.py
    - backend/app/services/knowledge_sessions.py
    - backend/tests/test_visibility.py
    - backend/tests/test_board.py
    - backend/tests/test_knowledge_sessions.py
    - backend/tests/test_performance.py
key-decisions:
  - "Backend query filters remain the source of truth for VIS-05; frontend filtering is not relied on for authorization."
  - "Schedule endpoints stayed personally owned as planned; no team-visible schedule surface was added."
patterns-established:
  - "Use visible_sub_team_ids plus scoped_sub_team_filter for project-owned data."
  - "Use require_visible_user before performance/user-targeted actions."
requirements-completed: [VIS-01, VIS-02, VIS-03, VIS-04, VIS-05]
duration: 31 min
completed: 2026-04-29
---

# Phase 29 Plan 03: Cross-Surface Visibility Enforcement Summary

**Phase 29 visibility filters now protect work, planning, collaboration, notification, and reporting backend surfaces.**

## Performance

- **Duration:** 31 min
- **Started:** 2026-04-29T15:56:35Z
- **Completed:** 2026-04-29T16:28:27Z
- **Tasks:** 4
- **Files modified:** 20

## Accomplishments

- Scoped project and task list/detail/write paths through shared visibility helpers.
- Changed timeline member behavior from assigned-task-only to full own-sub-team planning data.
- Scoped milestone CRUD, command view, and milestone decision endpoints by visible project scope.
- Replaced stale admin knowledge-session assumptions with manager/leader semantics.
- Scoped notification task event resolution and performance user access.
- Added regression coverage for direct-ID leaks across users, projects, tasks, milestones, board, knowledge sessions, and performance.

## Task Commits

1. **Task 1: Scope project and task list/detail/write access** - `9395a3d`
2. **Task 2: Scope timeline and milestone planning surfaces** - `9360b07`
3. **Task 3: Scope update, board, schedule, knowledge, notification, and performance surfaces** - `413bfec`
4. **Task 4: Add cross-surface leak-prevention regression tests** - `ada01c5`

## Verification

- `cd backend && rtk uv run pytest tests/test_visibility.py tests/test_projects.py tests/test_tasks.py tests/test_timeline.py tests/test_milestones.py tests/test_board.py tests/test_knowledge_sessions.py -q`  
  Result: `47 passed, 2 xfailed, 1 warning`
- `cd backend && rtk uv run pytest tests/test_visibility.py tests/test_projects.py tests/test_tasks.py -q`  
  Result: `30 passed, 2 xfailed, 1 warning`
- `cd backend && rtk uv run pytest tests/test_visibility.py tests/test_timeline.py tests/test_milestones.py -q`  
  Result: `27 passed, 1 warning`
- `cd backend && rtk uv run pytest tests/test_visibility.py tests/test_board.py tests/test_knowledge_sessions.py tests/test_performance.py -q`  
  Result: `31 passed, 1 warning`
- Admin dependency scan across plan surfaces: no active `UserRole.admin`, `require_admin`, or `admin` matches.
- Status-transition scan found only existing `StatusTransition` enforcement in `backend/app/routers/tasks.py`; no status-transition graph or YouTrack workflow-rule work was added.

## Files Created/Modified

- `backend/app/services/visibility.py` - added a reusable visible sub-team validator.
- `backend/app/routers/projects.py` - scoped project list, create, detail, update, and delete.
- `backend/app/routers/tasks.py` - scoped task list, create, detail, update, delete, project, and assignee access.
- `backend/app/routers/timeline.py` - scoped timeline projects by visible sub-team data.
- `backend/app/routers/milestones.py` - scoped milestone CRUD, command view, and decision endpoints.
- `backend/app/routers/updates.py` - updated template write guard naming to leader/manager semantics.
- `backend/app/routers/knowledge_sessions.py` - replaced admin/supervisor checks with manager/leader scope.
- `backend/app/services/knowledge_sessions.py` - updated visible session and presenter scope rules.
- `backend/app/routers/notifications.py` - scoped task event reminder resolution.
- `backend/app/routers/performance.py` - scoped performance target-user access.
- `backend/tests/test_visibility.py` - added cross-surface project/task/milestone leak tests.
- `backend/tests/test_board.py` - added board week payload scope coverage.
- `backend/tests/test_knowledge_sessions.py` - updated role fixtures to manager semantics.
- `backend/tests/test_performance.py` - replaced missing fixture with focused scoped-performance coverage.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Stale role fixtures referenced removed admin/supervisor fixtures**
- **Found during:** Tasks 1, 2, and 3 verification
- **Issue:** Existing tests referenced missing `admin_user` / `supervisor_user` fixtures or `UserRole.admin`, blocking required verification after Phase 29 role changes.
- **Fix:** Replaced those fixtures with local manager/supervisor/member setup and token generation.
- **Files modified:** `backend/tests/test_projects.py`, `backend/tests/test_timeline.py`, `backend/tests/test_knowledge_sessions.py`, `backend/tests/test_performance.py`, `backend/tests/test_tasks.py`
- **Verification:** All task and plan pytest commands passed.
- **Committed in:** `9395a3d`, `9360b07`, `413bfec`

**2. [Rule 3 - Blocking] Milestone decision backend dependency was uncommitted but required**
- **Found during:** Task 2
- **Issue:** `backend/app/routers/milestones.py` depended on milestone decision models/schemas/migration that were already present but uncommitted in the worktree.
- **Fix:** Included the backend milestone-decision model/schema/migration/test files in the Task 2 commit so the scoped milestone router is self-contained.
- **Files modified:** `backend/app/models/work.py`, `backend/app/models/__init__.py`, `backend/app/schemas/work.py`, `backend/app/schemas/__init__.py`, `backend/alembic/versions/19bc99b2b9ee_add_milestone_decisions.py`, `backend/tests/test_milestones.py`
- **Verification:** `tests/test_visibility.py tests/test_timeline.py tests/test_milestones.py` passed.
- **Committed in:** `9360b07`

**Total deviations:** 2 auto-fixed blocking issues.

## Issues Encountered

- Initial sandboxed `uv` verification could not access the existing user-level uv cache. Verification was rerun with approved escalation.
- Existing warning remains from Pydantic class-based config deprecation in `app/core/config.py`; it is pre-existing and outside this plan.

## Known Stubs

None found by stub-pattern scan.

## Threat Flags

| Flag | File | Description |
|------|------|-------------|
| threat_flag: schema | `backend/alembic/versions/19bc99b2b9ee_add_milestone_decisions.py` | Milestone decision persistence was included as a blocking dependency for scoped milestone decision endpoints. |
| threat_flag: endpoint-scope | `backend/app/routers/notifications.py` | Task notification event resolution now checks visible task scope before creating/listing event reminders. |

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

VIS-05 backend enforcement is covered for the required surfaces. Ready for Phase 29 Plan 04 frontend/seed alignment.

## Self-Check: PASSED

- Found summary file on disk.
- Found task commits: `9395a3d`, `9360b07`, `413bfec`, `ada01c5`.

---
*Phase: 29-scoped-team-visibility-leadership-rbac*
*Completed: 2026-04-29*
