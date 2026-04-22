# Research: Supervisor Performance Dashboard (Phase 3)

## Technical Deep Dive: High-Performance Aggregations

### 1. Multi-Metric SQL Pattern (SQLAlchemy)
To avoid N+1 queries or multiple database round-trips when fetching the team overview, use the **Aggregate Filter** pattern (native to PostgreSQL, supported in SQLAlchemy 1.4+). This allows calculating all columns for all users in a single pass.

**Prescriptive Pattern:**
```python
from sqlalchemy import func, select, extract, case
from app.models import User, Task, TaskStatus

# Define metrics in a single query
stmt = (
    select(
        User.id,
        User.full_name,
        User.role,
        # Active Tasks: todo, in_progress, review, blocked
        func.count(Task.id).filter(Task.status != TaskStatus.done).label("active_tasks"),
        # Completed (30d)
        func.count(Task.id).filter(
            Task.status == TaskStatus.done,
            Task.completed_at >= now - timedelta(days=30)
        ).label("completed_30d"),
        # Cycle Time (Hours)
        func.avg(
            extract("epoch", Task.completed_at - Task.created_at) / 3600
        ).filter(Task.status == TaskStatus.done).label("avg_cycle_time"),
        # On-Time Rate (Ratio)
        func.count(Task.id).filter(
            Task.status == TaskStatus.done,
            Task.completed_at <= Task.due_date
        ).label("on_time_count"),
        func.count(Task.id).filter(
            Task.status == TaskStatus.done,
            Task.due_date.is_not(None)
        ).label("total_with_due_date")
    )
    .join(Task, User.id == Task.assignee_id, isouter=True)
    .group_by(User.id)
)
```

### 2. Collaboration Activity (Messages Proxy)
Calculating "Collaboration Activity" via chat message counts is most efficient when using the existing index on `sender_id`.

- **SQL Pattern**: `func.count(ChatMessage.id).filter(ChatMessage.created_at >= now - timedelta(days=30))`
- **Performance**: PostgreSQL performs a **Bitmap Index Scan** on `sender_id` and `created_at`. At the scale of 5-15 users, this is sub-millisecond.
- **Implementation**: Join `User` with `ChatMessage` in the same massive aggregation query or run as a second targeted query joined by user ID.

### 3. Traffic-Light Status Logic (Backend vs. Frontend)
To ensure consistency across the API and UI, the "Status" should be a **derived property** computed in the Backend (and returned in the JSON) but the logic can be mirrored in the Frontend for real-time responsiveness if needed.

**Thresholds:**
- `RED`: `overdue_count > 0` OR `active_tasks > 10`
- `YELLOW`: `tasks_due_within_48h > 0` OR `active_tasks > 7`
- `GREEN`: Default

## Frontend: LayerChart v2 + Svelte 5 (Runes)

### 1. Best Practices
- **Version**: Must use `layerchart@next` (v2.x) for native Svelte 5 support.
- **Data Binding**: Use `$state.raw()` for chart data to bypass deep reactivity proxies (significant performance gain for larger datasets).
- **Events**: Use lowercase event names (e.g., `ontooltipclick`) to align with Svelte 5 native event handling.
- **Snippets**: Replace Svelte 4 `<slot>` patterns with `{#snippet}` for tooltips and custom axis labels.

**LayerChart Rune Pattern:**
```svelte
<script lang="ts">
  import { BarChart, Tooltip, TooltipItem } from 'layerchart';
  
  let { workloadData } = $props<{ workloadData: any[] }>();
  // Use $state.raw for the actual data passed to LayerChart
  let chartData = $state.raw(workloadData);
</script>

<div class="h-[300px]">
  <BarChart data={chartData} x="username" y="active_tasks">
    {#snippet tooltip()}
      <Tooltip>
        {#snippet children({ data })}
          <TooltipItem label="Active Tasks" value={data.active_tasks} />
        {/snippet}
      </Tooltip>
    {/snippet}
  </BarChart>
</div>
```

## Common Pitfalls & Edge Cases

### 1. Handling Nulls in Ratios
- **On-Time Rate**: If `total_with_due_date` is 0, the ratio is undefined. Return `null` or `100` (opt-out) based on preference.
- **Empty Users**: New users with 0 tasks must be handled. Ensure `LEFT JOIN` is used so they appear in the dashboard with zeroed metrics.

### 2. Cycle Time Skew
- **In-Progress Tasks**: Exclude tasks without a `completed_at` timestamp from the average.
- **Re-opened Tasks**: If a task is moved from `done` to `todo`, `completed_at` currently persists (potential bug discovered in `tasks.py`). 
    - *Action*: `03-PLAN.md` should include a fix to clear `completed_at` when moving out of `done`.

### 3. Timezone Consistency
- All calculations should use the database's naive UTC timestamps to match the existing `created_at` pattern.
- Avoid `utcnow()` (deprecated in Python 3.12+); use `datetime.now(timezone.utc).replace(tzinfo=None)`.

## Metric Breakdown Table

| Metric | SQL Logic | Notes |
| :--- | :--- | :--- |
| **Active Tasks** | `status != 'done'` | Includes 'blocked' and 'review' |
| **On-Time Rate** | `completed_at <= due_date` | Only counts tasks with `due_date` |
| **Cycle Time** | `AVG(completed_at - created_at)` | Converted to hours via `epoch` |
| **Collab. Activity** | `count(chat_messages)` | Last 30 days rolling |
| **At-Risk** | `due_date < now + 2d` | For status `todo` or `in_progress` |
