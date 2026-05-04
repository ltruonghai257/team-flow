# Phase 16: Advanced KPI Dashboard - Research

**Date:** 2026-04-26
**Status:** Complete

## Research Goal

Plan Phase 16 so the supervisor performance dashboard exposes real sprint and member KPI analytics without regressing TeamFlow's current FastAPI/SvelteKit patterns.

## Inputs Read

- `.planning/ROADMAP.md` Phase 16 section
- `.planning/REQUIREMENTS.md` KPI-01 through KPI-05
- `.planning/STATE.md`
- `.planning/phases/16-advanced-kpi-dashboard/16-CONTEXT.md`
- `.planning/phases/16-advanced-kpi-dashboard/16-UI-SPEC.md`
- `backend/app/routers/performance.py`
- `backend/app/schemas.py`
- `backend/app/models.py`
- `frontend/src/routes/performance/+page.svelte`
- `frontend/src/routes/performance/[id]/+page.svelte`
- `frontend/src/lib/api.ts`

## Key Findings

### Existing Performance Surface

The current backend exposes:

- `GET /api/performance/team`
- `GET /api/performance/user/{user_id}`

Both endpoints compute aggregates directly in `backend/app/routers/performance.py` and currently use `TaskStatus.done` as the completion source.

The current frontend exposes:

- `/performance` team dashboard with a workload SVG chart and member table.
- `/performance/[id]` member detail page with an inline SVG completion trend.

This is a good base, but Phase 16 requires broader API shape and a more structured UI.

### Phase 15 Dependency

Phase 16 must not implement completion queries against `TaskStatus.done`. It must use DB-backed custom status semantics from Phase 15:

- `Task.custom_status_id`
- `CustomStatus.is_done == true`
- Multiple `is_done` statuses are valid.

Execution should wait until Phase 15 has landed, or the executor must adapt to the final Phase 15 model names if they differ.

### Sprint Dependency

Phase 14 sprint model is present in the working tree:

- `SprintStatus`
- `Sprint`
- `Task.sprint_id`
- `Milestone.sprints`

Phase 16 can plan against `Sprint`, `Task.sprint_id`, and `Sprint.status`, but execution should verify Phase 14 migration is applied before building sprint analytics.

### Charting Strategy

`layerchart` is installed as `next`, but current performance pages explicitly say layerchart was removed and inline SVG is used. UI-SPEC permits inline SVG if maintainable and requires a compile/render proof before using layerchart.

Recommendation: keep inline SVG for Phase 16 to avoid dependency churn and unblock planning. Use small reusable Svelte components to reduce page complexity.

### KPI Weight Persistence

The user requested supervisor-configurable KPI weights, with controls in `/performance` Settings. Persisting weights requires a backend store. Best fit for this project:

- Add a `KPIWeightSettings` table scoped by `sub_team_id`.
- Store explicit integer percentages for `workload_weight`, `velocity_weight`, `cycle_time_weight`, `on_time_weight`, and `defect_weight`.
- Enforce total = 100 in backend validation.
- Default weights should be deterministic and explainable.

This introduces a schema change and therefore requires an Alembic migration and blocking migration task.

## Metric Definitions

### Completion Predicate

Use a shared backend query helper for done tasks:

```python
Task.custom_status_id == CustomStatus.id
CustomStatus.is_done.is_(True)
Task.completed_at.is_not(None)
```

For active tasks, use either no custom status or `CustomStatus.is_done.is_(False)`.

### Velocity

- Window: last 6 sprints.
- Grouping: sprint, member.
- Value: completed task count.
- Optional points: use `Task.estimated_hours` as the existing estimation field if present; label it as estimate total, not story points, unless a true story point field exists later.

### Burndown

- Window: selected active or closed sprint.
- Compute on the fly from sprint start/end and task completion dates.
- Remaining tasks for a date = tasks assigned to sprint whose completed_at is null or after that date.
- No snapshot table in v2.0.

### Cycle Time

- Window: default last 3 months, custom date range allowed.
- Formula: `completed_at - created_at`.
- Only include completed tasks with both timestamps.
- Group by task type.

### Throughput

- Window: default last 8 weeks, custom date range allowed.
- Formula: completed task count per week.
- Group by member and task type.

### Defect and MTTR

- Window: default last 30 days, custom date range allowed.
- Bugs reported: `Task.type == TaskType.bug` and `Task.created_at` in period.
- Bugs resolved: bug tasks completed in period.
- MTTR: average `completed_at - created_at` for completed bug tasks.
- Group MTTR by member.

### KPI Score

Default score categories:

- Workload balance
- Completion/velocity
- Cycle time
- On-time rate
- Defect/quality

Weights are editable and must total 100. Score output must include raw category scores and reason labels. Avoid opaque scoring.

## API Shape Recommendation

Add focused KPI endpoints under the existing performance router:

- `GET /api/performance/kpi/overview`
- `GET /api/performance/kpi/sprint`
- `GET /api/performance/kpi/quality`
- `GET /api/performance/kpi/members`
- `GET /api/performance/kpi/drilldown`
- `GET /api/performance/kpi/weights`
- `PATCH /api/performance/kpi/weights`

Each endpoint should honor `X-SubTeam-ID` through existing `get_sub_team`.

## UI Strategy

Convert `/performance` into a tabbed dashboard with:

- Overview: member KPI cards first, then exception list and summary tiles.
- Sprint: velocity and burndown.
- Quality: bugs reported/resolved and MTTR.
- Members: throughput, cycle time, member table.
- Settings: KPI weights.

Use shared local components under `frontend/src/lib/components/performance/`:

- `KpiTabs.svelte`
- `KpiScoreCard.svelte`
- `KpiChartPanel.svelte`
- `KpiFilters.svelte`
- `KpiDrilldown.svelte`
- `KpiWeightSettings.svelte`

## Validation Architecture

Plan validation should verify:

1. Every KPI requirement ID appears in at least one PLAN.md frontmatter `requirements` list.
2. Plans include a blocking prerequisite that Phase 15 completion semantics are available before execution.
3. Backend plans include a shared completion predicate based on custom status `is_done`.
4. Frontend plans use the approved `16-UI-SPEC.md` tab, color, filter, export, and drill-down contracts.
5. Plans include verification commands for backend import/compile and frontend Svelte checks.

## Risks

- Phase 16 execution before Phase 15 will produce wrong metrics if it falls back to `TaskStatus.done`.
- Inline SVG charts can become page-local complexity if not componentized.
- KPI scoring can become subjective if formula and weights are not exposed.
- Drill-down can accidentally bypass sub-team scoping if implemented as a raw task query.

## Research Complete

Phase 16 should be planned as a five-plan sequence: backend persistence/contracts, backend KPI endpoints, frontend API/components, dashboard assembly, and verification hardening.

