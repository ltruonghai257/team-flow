# Phase 16: Advanced KPI Dashboard - Pattern Map

**Date:** 2026-04-26
**Status:** Complete

## Closest Existing Analogs

| Target | Closest Analog | Pattern to Reuse |
|--------|----------------|------------------|
| KPI backend endpoints | `backend/app/routers/performance.py` | Router-scoped aggregate queries using SQLAlchemy `select`, `func.count`, filtered aggregates, and `require_supervisor` |
| KPI response contracts | `backend/app/schemas.py` | Pydantic `BaseModel` response classes near existing `PerformanceDashboard` models |
| Admin/supervisor scoping | `backend/app/auth.py` and `frontend/src/lib/api.ts` | `get_sub_team` dependency and `X-SubTeam-ID` header |
| Team dashboard route | `frontend/src/routes/performance/+page.svelte` | `onMount`, `$state`, inline SVG charting, dark dashboard cards, member table |
| Member detail drill-down | `frontend/src/routes/performance/[id]/+page.svelte` | Member profile header, trend chart, recent completed task list |
| API client extension | `frontend/src/lib/api.ts` | Domain object with typed helper methods under `performance` export |

## File Mapping

### `backend/app/models.py`

Role: persistence for configurable KPI weights.

Analog: `SubTeam`, `TeamInvite`, and enum/table declarations in the same file.

Expected additions:

- `KPIWeightSettings` model scoped by `sub_team_id`.
- Integer columns: `workload_weight`, `velocity_weight`, `cycle_time_weight`, `on_time_weight`, `defect_weight`.
- Timestamp column: `updated_at`.

### `backend/alembic/versions/*.py`

Role: schema migration for KPI weight settings.

Analog: existing Alembic migration files under `backend/alembic/versions/`.

Expected additions:

- Create `kpi_weight_settings` table.
- Add foreign key to `sub_teams.id`.
- Add uniqueness/index for `sub_team_id`.

### `backend/app/schemas.py`

Role: typed response/request contracts.

Analog: existing `PerformanceDashboard`, `TeamMemberPerformance`, and `UserPerformanceDetail` schemas.

Expected additions:

- KPI filter, point, series, scorecard, drill-down, and weight schemas.
- Weight update validation ensuring total = 100.

### `backend/app/routers/performance.py`

Role: KPI API implementation.

Analog: existing `get_team_performance` and `get_user_performance_detail`.

Expected additions:

- Shared date range parsing.
- Shared sub-team scoped task query.
- Shared completion predicate using Phase 15 `CustomStatus.is_done`.
- KPI endpoints under `/api/performance/kpi/...`.
- Existing endpoints updated away from `TaskStatus.done` once Phase 15 is complete.

### `frontend/src/lib/api.ts`

Role: frontend API client methods.

Analog: existing `performance.teamStats()` and `performance.memberStats(id)`.

Expected additions:

- `performance.kpiOverview(params)`
- `performance.kpiSprint(params)`
- `performance.kpiQuality(params)`
- `performance.kpiMembers(params)`
- `performance.kpiDrilldown(params)`
- `performance.kpiWeights()`
- `performance.updateKpiWeights(data)`

### `frontend/src/lib/components/performance/*.svelte`

Role: reusable dashboard UI components.

Analog: inline performance page structures and existing component style under `frontend/src/lib/components/tasks/`.

Expected additions:

- `KpiTabs.svelte`
- `KpiScoreCard.svelte`
- `KpiChartPanel.svelte`
- `KpiFilters.svelte`
- `KpiDrilldown.svelte`
- `KpiWeightSettings.svelte`

### `frontend/src/routes/performance/+page.svelte`

Role: tabbed supervisor KPI workspace.

Analog: existing route page.

Expected changes:

- Replace single workload chart/table layout with tabbed structure.
- Load KPI endpoint data per selected tab.
- Preserve existing dark surface styling and member table access.
- Add CSV export and drill-down interactions.

## Constraints for Executor

- Read `16-UI-SPEC.md` before editing frontend files.
- Do not add new chart packages.
- Use existing `lucide-svelte` icons.
- Do not hardcode completion as `TaskStatus.done`.
- Do not bypass `get_sub_team` or `X-SubTeam-ID`.

