# Plan 31-01 Summary: Schema and Service Foundation

## Objective
Create the schema and service foundation for the role-aware dashboard endpoint.

## Tasks Completed

### Task 1: Create backend/app/schemas/dashboard.py with five new Pydantic schemas
- Created `DashboardTaskItem` - slim task card for my_tasks
- Created `DashboardTeamHealthMember` - per-member team health entry
- Created `DashboardKpiSummary` - KPI strip with avg_score, completion_rate, needs_attention_count
- Created `DashboardActivityItem` - recent standup post entry
- Created `DashboardPayload` - top-level response schema with `exclude_none=True` for role-conditional fields
- All schemas importable and correctly typed

### Task 2: Create backend/app/services/kpi.py by extracting KPI computation from performance.py
- Extracted helper functions: `score_workload`, `score_velocity`, `score_cycle_time`, `score_on_time`, `score_defects`
- Extracted filter functions: `completed_task_filter`, `active_task_filter`
- Extracted `get_or_create_kpi_weights` function
- Created `KpiComputeResult` and `KpiPerMemberData` dataclasses
- Created `compute_kpi_overview` async function with:
  - Added `overdue_tasks` aggregate to per-member query
  - Built `per_member` list with overdue_tasks included
  - Computed `completion_rate` as total_completed / (total_active + total_completed)
- Updated `performance.py` to import and delegate to the new KPI service
- Removed old helper functions from `performance.py`
- Performance router behavior unchanged - response is identical to before

### Task 3: Update backend/app/schemas/__init__.py to export new dashboard schemas
- Added imports for all 5 dashboard schemas
- `DashboardStats` still exported (will be removed in Plan 31-02)
- All new schemas importable from `app.schemas`

## Deviations
None - all tasks completed as specified.

## Key Files Created/Modified
- **Created:** `backend/app/schemas/dashboard.py` (55 lines)
- **Created:** `backend/app/services/kpi.py` (177 lines)
- **Modified:** `backend/app/routers/performance.py` (removed 233 lines, added 432 lines - net refactor to use service)
- **Modified:** `backend/app/schemas/__init__.py` (added 13 lines)

## Self-Check: PASSED
- `from app.schemas.dashboard import DashboardPayload` exits 0
- `from app.services.kpi import compute_kpi_overview, KpiComputeResult` exits 0
- `from app.schemas import DashboardPayload, DashboardStats` exits 0
- `from app.routers.performance import router` exits 0
- `backend/app/routers/performance.py` contains `from app.services.kpi import`
- `backend/app/routers/performance.py` does NOT contain `def _score_workload` (moved to service)
- `DashboardPayload` has `exclude_none=True` in model_config
