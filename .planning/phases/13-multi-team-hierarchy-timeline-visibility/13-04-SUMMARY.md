---
phase: 13-multi-team-hierarchy-timeline-visibility
plan: 04
subsystem: backend
tags: [fastapi, routers, sub-team-scoping, role-based-access]

# Dependency graph
requires:
  - phase: 13-02
    provides: [SubTeam CRUD API endpoints, get_sub_team dependency]
provides:
  - Role-aware timeline filtering (member/supervisor/admin)
  - Sub-team scoped invite creation and acceptance
  - Sub-team scoped project creation with supervisor enforcement
  - Sub-team filtering across all data endpoints
affects: [13-05]

# Tech tracking
tech-stack:
  added: []
  patterns: [role-based query filtering, admin header-based context switching, supervisor cross-team restriction]

key-files:
  created: []
  modified: [backend/app/routers/timeline.py, backend/app/routers/invites.py, backend/app/routers/projects.py, backend/app/routers/tasks.py, backend/app/routers/dashboard.py, backend/app/routers/performance.py, backend/app/routers/users.py]

key-decisions:
  - "Members see only projects with assigned tasks (join with Task.assignee_id)"
  - "Supervisors see all projects in their sub-team (sub_team_id filter)"
  - "Admins see all projects, X-SubTeam-ID header provides optional filter"
  - "Invites scoped to inviter's sub-team context (not request body)"
  - "Users auto-assigned to invite's sub_team_id on acceptance"
  - "Supervisors restricted from creating projects outside their sub-team (403)"
  - "All data endpoints filter by sub_team from get_sub_team dependency"

patterns-established:
  - "Pattern: get_sub_team dependency for server-side sub-team context"
  - "Pattern: Admin bypasses filtering, respects X-SubTeam-ID header"
  - "Pattern: Supervisor cross-team enforcement with 403"

requirements-completed: [TEAM-03, TEAM-04, TEAM-05, VIS-01, VIS-02, VIS-03]

# Metrics
duration: 25min
completed: 2026-04-24
---

# Phase 13: Sub-team Scoping for Backend Routers Summary

**Role-aware timeline filtering, sub-team scoped invites/projects, and sub-team filtering across all data endpoints with admin header support**

## Performance

- **Duration:** 25 min
- **Started:** 2026-04-24T00:45:00Z
- **Completed:** 2026-04-24T01:10:00Z
- **Tasks:** 4
- **Files modified:** 7

## Accomplishments
- Timeline router updated with role-aware visibility (members see only their assigned tasks, supervisors see sub-team projects, admins see all with optional X-SubTeam-ID filter)
- Invites router updated to scope new invites to inviter's sub-team context (derived from user's sub_team_id or admin's X-SubTeam-ID header)
- Invite accept endpoint auto-assigns users to invite's sub_team_id
- Projects router updated with sub-team scoping and supervisor enforcement (403 on cross-team creation attempt)
- Tasks router updated with sub-team filtering via Project join
- Dashboard router updated with sub-team filtering for task and user queries
- Performance router updated with sub-team filtering for team metrics
- Users router updated with sub-team filtering for user listing (non-admins see only their sub-team's members)

## Task Commits

Each task was committed atomically:

1. **Task 1: Update timeline router with role-aware visibility** - `987006a` (feat)
2. **Task 2: Update invites router with sub-team scoping** - `c37fe10` (feat)
3. **Task 3: Update projects router with sub-team scoping and enforcement** - `62d74c2` (feat)
4. **Task 4: Add get_sub_team to remaining routers** - `094fb89` (feat)

## Files Created/Modified
- `backend/app/routers/timeline.py` - Added get_sub_team dependency, role-specific WHERE clauses (member join with Task.assignee_id, supervisor/admin sub_team_id filter)
- `backend/app/routers/invites.py` - Added get_sub_team dependency, sub_team_id derived from inviter's context, user assignment on accept
- `backend/app/routers/projects.py` - Added get_sub_team dependency, sub_team_id from context, supervisor enforcement with 403
- `backend/app/routers/tasks.py` - Added get_sub_team dependency, filter by Project.sub_team_id via join
- `backend/app/routers/dashboard.py` - Added get_sub_team dependency, filter task and user queries by sub_team_id
- `backend/app/routers/performance.py` - Added get_sub_team dependency, filter metrics query by Project.sub_team_id via join
- `backend/app/routers/users.py` - Added get_sub_team dependency, filter user listing by sub_team_id

## Decisions Made
- Members see only projects where they have assigned tasks (join with Task.assignee_id)
- Supervisors see all projects in their sub-team (sub_team_id filter)
- Admins see all projects, X-SubTeam-ID header provides optional filter
- Invites scoped to inviter's sub-team context (not from request body per D-16/D-17)
- Users auto-assigned to invite's sub_team_id on acceptance (per D-18)
- Supervisors restricted from creating projects outside their sub-team with 403 (per D-15)
- All data endpoints filter by sub_team from get_sub_team dependency (per D-19)
- Admin endpoints bypass filtering, respect X-SubTeam-ID header (per D-20)

## Deviations from Plan

None - plan executed exactly as written

## Issues Encountered

None

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- Backend router scoping complete with role-based filtering
- Ready for test stub creation and database schema push (Wave 4)

---
*Phase: 13-multi-team-hierarchy-timeline-visibility*
*Completed: 2026-04-24*
