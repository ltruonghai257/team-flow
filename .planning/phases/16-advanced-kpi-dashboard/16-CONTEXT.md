# Phase 16: Advanced KPI Dashboard - Context

**Gathered:** 2026-04-26
**Status:** Ready for planning

<domain>
## Phase Boundary

The supervisor performance dashboard exposes sprint and team KPI metrics computed from real sprint, task type, member, and DB-backed completion data. This phase adds velocity, burndown, cycle time by task type, throughput by member/type, defect metrics, MTTR, KPI scoring, filters, drill-downs, and exports inside the existing supervisor performance surface.

</domain>

<decisions>
## Implementation Decisions

### Dashboard Structure
- **D-01:** Keep `/performance` as the main route for Phase 16.
- **D-02:** Convert the performance dashboard into a tabbed interface rather than creating a separate sprint analytics route.
- **D-03:** Use tabs such as Overview, Sprint, Quality, Members, and Settings to keep the dashboard manageable.
- **D-04:** Existing member workload/performance content should remain available, but Phase 16 should reorganize it around the new KPI views.

### Metric Definitions
- **D-05:** Use mixed metric strictness: time-based metrics are strict, count-based metrics are flexible.
- **D-06:** Cycle time and MTTR require usable `created_at` and `completed_at` values; records missing either timestamp are excluded from those calculations.
- **D-07:** Velocity and throughput should use completed task counts when story points or estimates are missing.
- **D-08:** Burndown is computed on the fly from task completion dates within the sprint window; historical burndown snapshots remain out of scope for v2.0.
- **D-09:** Bug metrics use `Task.type == bug`: bugs reported are created bug tasks, bugs resolved are completed bug tasks, and MTTR is average bug `completed_at - created_at`.
- **D-10:** All completion checks must use Phase 15 DB-backed `custom_status.is_done`, not `TaskStatus.done` or status slug comparisons.

### Filtering Scope
- **D-11:** Use view-specific filters instead of one global mega-filter.
- **D-12:** Sprint views should filter by sprint, project, member, task type, and useful date ranges.
- **D-13:** Team/member views should filter by member, task type, project, and date range where meaningful.
- **D-14:** Quality/defect views should filter by project, member, task type, and date range.
- **D-15:** Requirement default windows still matter: last 6 sprints, active/closed sprint burndown, last 3 months for cycle time, last 8 weeks for throughput, and last 30 days for defect/MTTR. Custom date ranges may override where the chart supports it.

### Chart Interaction and Exports
- **D-16:** KPI charts should provide static readable summaries with labels/tooltips.
- **D-17:** KPI charts should support drill-down where useful: clicking a bar/point opens the underlying tasks, member slice, sprint slice, or project slice.
- **D-18:** KPI chart data should be exportable, with CSV as the baseline export format.
- **D-19:** Existing inline SVG chart approach is acceptable if it keeps the charts maintainable; `layerchart` is installed but must be verified before use.

### Member Performance Management
- **D-20:** The dashboard should be people-first: member scorecards and member KPI health should be prominent when a supervisor opens `/performance`.
- **D-21:** The dashboard should also be exception-aware: surface who needs attention due to overload, low KPI score, slipping trends, high defect load, poor cycle time, or other warning signals.
- **D-22:** The goal is to make member performance and KPI management easy for supervisors, not just to render charts.

### KPI Score and Weighting
- **D-23:** Each member should have a numeric KPI score with a visible metric breakdown.
- **D-24:** Use a transparent default scoring formula based on workload balance, completion/velocity, cycle time, on-time rate, and defect metrics.
- **D-25:** Supervisors should be able to configure KPI metric weights.
- **D-26:** KPI weight controls belong in a Settings tab inside `/performance`, near the KPI dashboard.
- **D-27:** Default weights should be explainable and editable; downstream planning should avoid opaque scoring.

### Agent's Discretion
- Exact tab labels and ordering, provided the people-first and exception-aware goals are preserved.
- Exact score formula and default weight values, provided the formula is transparent and covers the agreed metric categories.
- Exact drill-down presentation, such as modal, side panel, or linked filtered task view.
- Exact CSV export implementation and filename format.
- Whether to use inline SVG or verified chart helpers, provided no unstable dependency blocks the phase.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Roadmap and Requirements
- `.planning/ROADMAP.md` — Phase 16 goal, dependencies, and success criteria.
- `.planning/REQUIREMENTS.md` — KPI-01 through KPI-05 acceptance criteria and metric windows.
- `.planning/STATE.md` — Phase 16 watch-outs, including `is_done` dependency and chart library verification.

### Prior Phase Context
- `.planning/phases/13-multi-team-hierarchy-timeline-visibility/13-CONTEXT.md` — Sub-team scoping, admin global switcher, and server-side visibility decisions.
- `.planning/phases/14-sprint-model/14-CONTEXT.md` — Sprint model, sprint board, and sprint close context.
- `.planning/phases/15-custom-kanban-statuses/15-CONTEXT.md` — DB-backed status and `is_done` completion semantics that Phase 16 metrics must use.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `frontend/src/routes/performance/+page.svelte`: Existing supervisor performance dashboard route with member table and inline SVG workload chart; this should become the tabbed KPI dashboard shell.
- `frontend/src/routes/performance/[id]/+page.svelte`: Existing member detail route and inline SVG trend chart; useful for drill-down/member profile patterns.
- `frontend/src/lib/api.ts`: Existing `performance.teamStats()` and `performance.memberStats(id)` API client pattern; Phase 16 should extend this domain client.
- `backend/app/routers/performance.py`: Existing performance aggregation endpoint; this is the main backend integration point for new KPI endpoints.

### Established Patterns
- Backend aggregation currently uses SQLAlchemy aggregate queries with `func.count`, filtered aggregates, and grouped results.
- Existing performance queries still compare directly against `TaskStatus.done`; Phase 16 must replace KPI completion logic with DB-backed `is_done` joins after Phase 15.
- Frontend charting currently uses inline SVG and comments indicate `layerchart` was removed/bypassed; `frontend/package.json` still lists `layerchart: next` and `d3-shape`.
- API calls use the `X-SubTeam-ID` header from the admin sub-team switcher; KPI endpoints must honor the same scoping model.

### Integration Points
- `backend/app/routers/performance.py`: Add or extend endpoints for velocity, burndown, cycle time by type, throughput, defect metrics, member KPI score, weight settings, drill-down slices, and CSV/export data.
- `backend/app/schemas.py`: Add response schemas for KPI charts, scorecards, weight settings, and drill-down task lists.
- `backend/app/models.py`: Use Task, User, Project, Sprint/milestone fields from Phase 14, task type from Phase 12, and custom status completion semantics from Phase 15.
- `frontend/src/routes/performance/+page.svelte`: Add tabbed UI, member scorecards, chart panels, filters, settings, drill-down affordances, and export controls.
- `frontend/src/lib/api.ts`: Add performance client methods for KPI data and weight settings.

</code_context>

<specifics>
## Specific Ideas

- The first supervisor impression should answer: who is doing well, who needs attention, and why.
- Member scorecards should combine numeric KPI score, trend, workload, velocity/completion, quality/defect signals, and short reason labels.
- Drill-down should connect charts back to real tasks so supervisors can inspect the data behind a KPI.
- CSV export is part of the expected chart behavior, not a later nice-to-have.
- Weight configuration should live close to the KPI dashboard, not buried in unrelated team administration.

</specifics>

<deferred>
## Deferred Ideas

None - discussion stayed within phase scope.

</deferred>

---

*Phase: 16-Advanced KPI Dashboard*
*Context gathered: 2026-04-26*
