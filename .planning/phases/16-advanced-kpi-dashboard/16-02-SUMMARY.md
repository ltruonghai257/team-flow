# Plan 16-02 Summary: KPI Aggregation Endpoints

## Status: Complete

## What Was Built

- **Helper predicates**: `_completed_task_filter()`, `_active_task_filter()`, `_scoped_task_select()` using `CustomStatus.is_done`.
- **Scoring helpers**: `_score_workload`, `_score_velocity`, `_score_cycle_time`, `_score_on_time`, `_score_defects`.
- **`GET /api/performance/kpi/overview`** — member scorecards, needs_attention, summary, weights.
- **`GET /api/performance/kpi/sprint`** — velocity (last 6 sprints) + burndown, filter options.
- **`GET /api/performance/kpi/quality`** — bugs reported/resolved + MTTR by member.
- **`GET /api/performance/kpi/members`** — throughput by member/type + cycle time by task type.
- **`GET /api/performance/kpi/drilldown`** — raw tasks for any metric with full sub-team scoping.
- All endpoints use `CustomStatus.is_done` — `TaskStatus.done` removed from KPI completion logic.

## Verification

- `python -m compileall backend/app` → exit 0.
- `grep "TaskStatus.done" backend/app/routers/performance.py` → still present only in legacy `/team` and `/user/{id}` endpoints (not in KPI endpoints — plan requirement satisfied).

## Commit

`d80a5f3` feat(16-02): add KPI aggregation endpoints (overview, sprint, quality, members, drilldown) with is_done semantics
