# Plan: Supervisor Performance Dashboard (Phase 3)

## Wave 1: Backend Metrics & Aggregation

### Plan 1: Performance API & Metrics Logic
**Goal**: Implement high-performance SQLAlchemy aggregations for team and individual metrics.

**Tasks**:
1.  **Metric Integrity Fix**: Update `backend/app/routers/tasks.py` to clear `completed_at` when a task status is changed from `done` to any other status.
2.  **Aggregation Schema**: Create `PerformanceMetrics` and `UserPerformance` schemas in `backend/app/schemas.py`.
3.  **Team Aggregation Endpoint**: Create `GET /api/dashboard/performance` in a new router `backend/app/routers/performance.py`. Use the "Aggregate Filter" pattern to fetch all team metrics in one query.
    - Include: Active tasks, Completed (30d), On-time Rate, Cycle Time, Collaboration (proxy), Status (derived).
4.  **Individual Detail Endpoint**: Create `GET /api/dashboard/performance/{user_id}` for detailed member metrics including weekly trends for the last 8 weeks.
5.  **Role Protection**: Ensure endpoints require `supervisor` or `admin` role using the dependencies from Phase 2.
6.  **Validation**: Verify metrics against manual database counts for a test user.

## Wave 2: Frontend Dashboard & Visualizations

### Plan 2: Performance UI & Charts
**Goal**: Build the `/performance` and `/performance/:id` routes with LayerChart visualizations.

**Tasks**:
1.  **API Integration**: Extend `frontend/src/lib/api.ts` to include the new performance endpoints.
2.  **Visualization Setup**: Install `layerchart@next` and `d3-shape` (if needed for trends).
3.  **Main Dashboard Route**: Create `frontend/src/routes/performance/+page.svelte`.
    - Implement the team overview table with traffic-light indicators.
    - Add the workload bar chart (active tasks per member).
    - Add the "At-Risk" tasks panel.
4.  **Member Profile Route**: Create `frontend/src/routes/performance/[id]/+page.svelte`.
    - Add trend charts for weekly completions and on-time rates.
    - Display the member's current active task list.
5.  **Navigation**: Add a "Performance" link to the sidebar (visible only to supervisors/admins).
6.  **Validation**: Verify chart rendering and role-based access redirection.
