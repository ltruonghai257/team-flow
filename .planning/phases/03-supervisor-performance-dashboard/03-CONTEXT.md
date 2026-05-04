# Context: Supervisor Performance Dashboard (Phase 3)

## Goal
Implement a supervisor-only dashboard that provides per-member performance metrics, workload visualization, and at-risk task tracking.

## Decisions

### 1. Performance Metrics & Formulas
- **Active Tasks**: `count(tasks WHERE status != 'done' AND assignee_id = user_id)`
- **Completed (30d)**: `count(tasks WHERE status = 'done' AND completed_at > now - 30 days AND assignee_id = user_id)`
- **On-time Rate**: `(count(tasks WHERE status = 'done' AND completed_at <= due_date) / count(tasks WHERE status = 'done' AND due_date IS NOT NULL)) * 100`
- **Avg Cycle Time**: `avg(completed_at - created_at)` for completed tasks.
- **Collaboration Activity**: Proxy metric — `count(chat_messages WHERE sender_id = user_id)` (filtered by channel type if possible).
- **Total Completed**: `count(tasks WHERE status = 'done' AND assignee_id = user_id)`

### 2. Status Indicators (Traffic-Light)
- **Red (Overloaded/At-Risk)**: 
    - `overdue_count > 0` OR `active_task_count > 10`
- **Yellow (Watch)**: 
    - `tasks_due_within_48h > 0` OR `active_task_count > 7`
- **Green (On Track)**:
    - All other cases.

### 3. Frontend Implementation
- **Visualization Library**: `LayerChart` (or `Pancake` if LayerChart is too heavy).
- **Routing**: 
    - `/performance`: Main supervisor dashboard (Table + Team Charts).
    - `/performance/:user_id`: Individual member detail view (Trend Charts + Task List).
- **Access Control**: Both routes must be protected by a `supervisor` or `admin` role check (frontend and backend).

### 4. Technical Approach
- **Backend**: New router `backend/app/routers/dashboard_performance.py` or extend `dashboard.py`. Use SQLAlchemy aggregations for efficiency.
- **Frontend**: Create new components in `frontend/src/lib/components/performance/` for charts and tables.
- **Calculation**: On-the-fly SQL queries (no caching required for now).

## Gray Areas Resolved
- **Calculation Frequency**: On-the-fly.
- **Thresholds**: Defined as 10 (Red) and 7 (Yellow) active tasks.
- **Route vs Modal**: Dedicated routes for profile views.

## Next Steps
1. **Research**: Determine best SQL queries for the new collaboration metric and complex trends.
2. **Planning**: Create `03-PLAN.md` with implementation steps.
