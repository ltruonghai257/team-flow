# Plan 31-02 Summary: Role-Aware Dashboard Endpoint

## Objective
Replace the existing generic dashboard endpoint with a role-aware handler returning DashboardPayload, and remove the now-obsolete DashboardStats schema.

## Tasks Completed

### Task 1: Rewrite backend/app/routers/dashboard.py with role-aware DashboardPayload handler
- Fully replaced dashboard router with new implementation
- Changed response model from `DashboardStats` to `DashboardPayload`
- Implemented Section 1 (my_tasks): queries non-done tasks for current user, sorts overdue-first then by due_date, limits to 20
- Implemented Section 2 (team_health and kpi_summary): guarded by `is_leader(current_user) or is_manager(current_user)` check
  - Calls `compute_kpi_overview(db, sub_team)` from the new KPI service
  - Builds `DashboardTeamHealthMember` list from `kpi_result.per_member` with status based on active_tasks
  - Builds `DashboardKpiSummary` from service result (avg_score, completion_rate, needs_attention_count)
  - Member role: both fields remain None (excluded from JSON by `exclude_none=True`)
- Implemented Section 3 (recent_activity): queries 5 most recent StandupPost, scoped by sub_team_id if sub_team is not None
  - Loads author relationship for each post via `db.refresh`
  - Builds `DashboardActivityItem` list with post_id, author_id, author_name, created_at, field_values
- Router imports: `DashboardPayload`, `DashboardTaskItem`, `DashboardTeamHealthMember`, `DashboardKpiSummary`, `DashboardActivityItem` from schemas.dashboard
- Router imports: `compute_kpi_overview` from services.kpi
- Router imports: `is_leader`, `is_manager` from services.visibility
- No `DashboardStats` import in new router

### Task 2: Remove DashboardStats from schemas/work.py and schemas/__init__.py
- Removed `DashboardStats` class definition from `backend/app/schemas/work.py` (lines 436-448 removed)
- Removed `DashboardStats` from import block in `backend/app/schemas/__init__.py`
- Verified no other files in codebase import `DashboardStats` (only found in schemas/work.py and schemas/__init__.py)
- `DashboardPayload` already exported from schemas/__init__.py (added in Plan 31-01)
- Full app import chain works: `from app.api.main import app` exits 0

## Deviations
None - all tasks completed as specified.

## Key Files Created/Modified
- **Modified:** `backend/app/routers/dashboard.py` (removed 82 lines, added 111 lines - complete rewrite)
- **Modified:** `backend/app/schemas/work.py` (removed 13 lines - DashboardStats class)
- **Modified:** `backend/app/schemas/__init__.py` (removed 1 line - DashboardStats import)

## Self-Check: PASSED
- `from app.routers.dashboard import router` exits 0
- `from app.api.main import app` exits 0
- `backend/app/routers/dashboard.py` contains `response_model=DashboardPayload`
- `backend/app/routers/dashboard.py` contains `from app.services.kpi import compute_kpi_overview`
- `backend/app/routers/dashboard.py` contains `from app.services.visibility import is_leader, is_manager`
- `backend/app/routers/dashboard.py` contains `is_leader(current_user) or is_manager(current_user)` guard
- `backend/app/routers/dashboard.py` does NOT import `DashboardStats`
- `backend/app/routers/dashboard.py` contains `StandupPost.sub_team_id == sub_team.id` (activity scoping)
- `my_tasks` limit of 20 is present in code
- `grep -r "DashboardStats" backend/ --include="*.py"` returns no matches
- `from app.schemas import DashboardPayload` exits 0
