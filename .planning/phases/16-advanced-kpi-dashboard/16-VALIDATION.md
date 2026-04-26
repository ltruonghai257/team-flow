---
phase: 16
slug: advanced-kpi-dashboard
status: draft
created: 2026-04-26
---

# Phase 16 Validation Strategy

## Validation Architecture

Phase 16 validation must prove that the dashboard is both numerically correct and usable as a supervisor KPI management surface.

## Required Checks

1. **Requirement coverage:** PLAN.md frontmatter covers KPI-01 through KPI-05.
2. **Completion predicate:** backend code uses DB-backed custom status `is_done`, not `TaskStatus.done`, for KPI completion.
3. **Sub-team scoping:** KPI endpoints include `get_sub_team` and apply project/sub-team filters.
4. **Metric windows:** default windows match requirements: 6 sprints, active/closed sprint, 3 months, 8 weeks, 30 days.
5. **KPI score explainability:** API returns score category breakdown and reason labels.
6. **Weight validation:** backend rejects saved weights unless total equals 100.
7. **UI contract:** `/performance` includes tabs, people-first scorecards, exception list, filters, drill-down, export, and settings.
8. **Build checks:** backend import/compile and frontend `bun run check` pass.

## Manual UAT

- Supervisor opens `/performance` and sees member KPI scorecards first.
- Supervisor switches between Overview, Sprint, Quality, Members, and Settings tabs.
- Supervisor filters a sprint chart by sprint/project/member/type/date range.
- Supervisor clicks a chart point/bar and sees the underlying task list.
- Supervisor exports CSV from a chart panel and from a drill-down.
- Supervisor changes KPI weights and sees validation if the total is not 100.

