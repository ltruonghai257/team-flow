# Phase 16: Advanced KPI Dashboard - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md - this log preserves the alternatives considered.

**Date:** 2026-04-26
**Phase:** 16-Advanced KPI Dashboard
**Areas discussed:** Dashboard Structure, Metric Definitions, Filtering Scope, Chart Interaction, Member Performance Management, KPI Health Signals, KPI Score Calculation, Configurable KPI Weights

---

## Dashboard Structure

| Option | Description | Selected |
|--------|-------------|----------|
| Single expanded `/performance` dashboard | All KPI charts appear on the existing performance page. Fastest path, but may become dense. | |
| Tabbed `/performance` dashboard | Existing member table stays, with tabs like Overview, Sprint, Quality, Members. Balanced and keeps one route. | Yes |
| Separate sprint analytics page | `/performance` remains team/member focused; sprint metrics move to a dedicated route. Cleaner long term, more navigation work. | |

**User's choice:** Tabbed `/performance` dashboard.
**Notes:** Keep one performance route while separating KPI areas into tabs.

---

## Metric Definitions

| Option | Description | Selected |
|--------|-------------|----------|
| Strict data quality | Exclude incomplete records from each metric and show excluded count notes. Most accurate, but may expose sparse charts. | |
| Best-effort with fallbacks | Include what can be counted, use task count when story points are missing, and quietly skip fields that cannot be computed. | |
| Mixed: strict for time metrics, flexible for counts | Cycle time/MTTR require both created/completed dates; velocity/throughput use task counts when points are missing. Matches requirements closely. | Yes |

**User's choice:** Mixed: strict for time metrics, flexible for counts.
**Notes:** Time-based metrics require complete timestamps; count-based metrics should still work without story points.

---

## Filtering Scope

| Option | Description | Selected |
|--------|-------------|----------|
| Core filters only | Sprint, project, member, task type. Date ranges stay fixed by requirement windows. | |
| Core filters + date range | Add custom date ranges across charts where possible. More flexible, more edge cases. | Yes |
| View-specific filters | Sprint charts filter by sprint/project; team charts filter by member/type; quality charts filter by project/member/type. No global mega-filter. | Yes |

**User's choice:** Core filters plus date range, applied as view-specific filters.
**Notes:** Avoid one global filter bar controlling every chart.

---

## Chart Interaction

| Option | Description | Selected |
|--------|-------------|----------|
| Static summaries | Charts show the required metrics with tooltips/labels only. Fastest and easiest to verify. | Yes |
| Clickable drill-down | Clicking a bar/point opens the underlying tasks or member slice. More useful for supervisors, more implementation work. | Yes |
| Export-oriented | Prioritize CSV/export buttons for chart data over drill-down interactions. | Yes |

**User's choice:** All chart interaction modes.
**Notes:** Charts should summarize, support drill-down, and export KPI data.

---

## Member Performance Management

| Option | Description | Selected |
|--------|-------------|----------|
| People first | Member scorecards lead the page, with each person's KPI health, workload, velocity, quality, and trend. | Yes |
| Sprint health first | Sprint burndown/velocity leads, with member breakdowns inside the sprint view. | |
| Exception first | Show who needs attention: overloaded, underperforming, blocked, high defect load, or slipping trend. | Yes |

**User's choice:** People first and exception-aware.
**Notes:** The supervisor should easily manage member performance and KPIs.

---

## KPI Health Signals

| Option | Description | Selected |
|--------|-------------|----------|
| Simple health states | Green/yellow/red with short reasons like "high overdue load" or "cycle time rising." | |
| Numeric KPI score | One composite score per member, with metric breakdown underneath. | Yes |
| No score, just metrics | Avoid judgment labels; show raw metrics and trends only. | |

**User's choice:** Numeric KPI score.
**Notes:** Each member should have a visible KPI score and breakdown.

---

## KPI Score Calculation

| Option | Description | Selected |
|--------|-------------|----------|
| Transparent fixed formula | Fixed weighted score from workload balance, completion/velocity, cycle time, on-time rate, and defect metrics. Easiest to explain. | Yes |
| Supervisor-configurable weights | Supervisor can adjust which metrics matter more. More flexible, larger scope. | Yes |
| Score now, weights later | Implement fixed formula in Phase 16, but structure it so configurable weights can be added later. | |

**User's choice:** Transparent default formula plus supervisor-configurable weights.
**Notes:** Default weights must be explainable and editable.

---

## Configurable KPI Weights

| Option | Description | Selected |
|--------|-------------|----------|
| Performance settings tab | Keep weight controls inside `/performance`, near the KPI dashboard. | Yes |
| Team settings | Manage weights on `/team` because they apply to team evaluation policy. | |
| Inline edit on score card | Quick edit from the score section, with a modal for weights. | |

**User's choice:** Performance settings tab.
**Notes:** KPI weight controls belong near the dashboard they affect.

## Agent's Discretion

- Exact tab labels and ordering.
- Exact score formula and default weight values, provided the formula is transparent and covers the agreed metric categories.
- Exact drill-down presentation.
- Exact CSV export implementation and filename format.
- Whether to use inline SVG or verified chart helpers.

## Deferred Ideas

None.
