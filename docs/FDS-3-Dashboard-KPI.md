# Functional Design Specification: Dashboard & KPI System

**Version:** 1.0
**Date:** 2026-05-07
**Status:** Draft

## 1. Overview

This specification details the Dashboard and KPI (Key Performance Indicator) system in TeamFlow, which provides role-aware overviews and performance metrics for team management.

### 1.1 Purpose

Implement a professional dashboard that:
- Shows each role exactly what they need at a glance
- Provides real-time team health indicators
- Delivers actionable KPI metrics for supervisors
- Enables quick identification of at-risk team members
- Supports data-driven decision making

### 1.2 Scope

- Dashboard API endpoint with role-conditional payloads
- Dashboard UI with role-specific sections
- KPI calculation methodology
- Team health workload assessment
- Activity feed with visibility scoping

### 1.3 Target Users

- **All Roles:** See personalized task queue and activity feed
- **Supervisor/Assistant Manager/Manager:** See team health and KPI metrics
- **Member:** See only tasks and activity (no team health/KPI)

## 2. Dashboard Architecture

### 2.1 Dashboard API Endpoint

**Endpoint:** `GET /api/dashboard/`

**Authentication:** Required (JWT cookie)

**Response Shape (Role-Conditional):**

```python
# Member Response
{
  "my_tasks": [...],
  "recent_activity": [...]
}

# Supervisor/Assistant Manager/Manager Response
{
  "my_tasks": [...],
  "team_health": [...],
  "kpi_summary": {
    "avg_score": float,
    "completion_rate": float,
    "needs_attention_count": int
  },
  "recent_activity": [...]
}
```

### 2.2 Data Sources

**my_tasks:**
- Source: Task table
- Filter: `assignee_id == current_user.id`
- Filter: `status != 'done'`
- Sort: Overdue first, then by due_date ascending
- Fields: id, title, project_name, priority, status, is_overdue, is_due_soon

**team_health:**
- Source: User table + Task table
- Filter: Users in visible sub-teams
- Calculation: Active task count per user
- Fields: user_id, full_name, avatar_url, active_tasks, overdue_tasks, status (red/yellow/green)

**kpi_summary:**
- Source: Aggregated from KPI calculations
- Filter: Users in visible sub-teams
- Calculation: Average of all KPI scores
- Fields: avg_score, completion_rate, needs_attention_count

**recent_activity:**
- Source: StandupPost table
- Filter: Posts from visible sub-teams
- Limit: 5 most recent
- Fields: post_id, author_id, author_name, created_at, field_values

## 3. Dashboard Sections

### 3.1 My Tasks Section

**Visibility:** All roles

**Purpose:** Show user's assigned tasks sorted by urgency

**Data Structure:**
```typescript
interface TaskCard {
  id: number;
  title: string;
  project_name: string | null;
  priority: TaskPriority;
  status: TaskStatus;
  is_overdue: boolean;
  is_due_soon: boolean;
}
```

**Visual Indicators:**
- **Overdue:** Red background (`bg-red-950/40`)
- **Due Soon (within 48h):** Yellow background (`bg-yellow-950/40`)
- **Normal:** Default styling

**Sorting Logic:**
1. Overdue tasks first
2. Tasks due within 48 hours
3. Other tasks by due_date ascending

**Navigation:**
- Click task card → Navigate to `/tasks` with task selected

### 3.2 Team Health Section

**Visibility:** Supervisor, Assistant Manager, Manager only

**Purpose:** Show workload distribution across team members

**Data Structure:**
```typescript
interface TeamHealthMember {
  user_id: number;
  full_name: string;
  avatar_url: string | null;
  active_tasks: number;
  overdue_tasks: number;
  status: 'red' | 'yellow' | 'green';
}
```

**Status Calculation:**
```python
def calculate_health_status(active_tasks, overdue_tasks):
    if overdue_tasks > 0:
        return 'red'
    if active_tasks > 7:
        return 'yellow'  # Overloaded
    if active_tasks == 0:
        return 'yellow'  # Underloaded
    return 'green'  # Healthy
```

**Visual Indicators:**
- **Red (At-Risk):** Red border (`border-red-500/50`)
- **Yellow (Warning):** Yellow border (`border-yellow-500/50`)
- **Green (Healthy):** Gray border (`border-gray-700`)

**Navigation:**
- Click section → Navigate to `/performance`
- Click member → Navigate to member's performance details

### 3.3 KPI Summary Strip

**Visibility:** Supervisor, Assistant Manager, Manager only

**Purpose:** Quick overview of team performance metrics

**Data Structure:**
```typescript
interface KPISummary {
  avg_score: number;  // 0-100
  completion_rate: number;  // 0.0-1.0
  needs_attention_count: number;  // Users with KPI < 70
}
```

**Metrics Display:**

**Average Score:**
- Range: 0-100
- Color coding:
  - 80-100: Green text
  - 60-79: Yellow text
  - Below 60: Red text

**Completion Rate:**
- Range: 0-100%
- Shows percentage of tasks completed in last 30 days

**Needs Attention:**
- Count of users with KPI score < 70
- Yellow text if count > 0
- Links to `/performance` with filter applied

**Navigation:**
- Click any metric → Navigate to `/performance`

### 3.4 Activity Feed Section

**Visibility:** All roles

**Purpose:** Show recent standup posts as team pulse

**Data Structure:**
```typescript
interface ActivityFeedItem {
  post_id: number;
  author_id: number;
  author_name: string;
  created_at: string;
  field_values: Record<string, string>;
}
```

**Visibility Scoping:**
- **Member:** Posts from own sub-team only
- **Supervisor:** Posts from visible sub-teams
- **Manager:** All posts

**Display:**
- Author avatar (initials or image)
- Author name
- Relative time (e.g., "2 hours ago")
- Post preview (first 120 characters)

**Navigation:**
- Click item → Navigate to `/updates` with post selected
- "View all updates" link → Navigate to `/updates`

## 4. KPI Calculation Methodology

### 4.1 KPI Score Formula

```
KPI Score = (Workload × 0.20) + (Velocity × 0.25) + (CycleTime × 0.20) + (OnTime × 0.20) + (DefectRate × 0.15)
```

### 4.2 Component Calculations

#### Workload (20%)

**Definition:** Balance of active task load

**Calculation:**
```python
def calculate_workload_score(active_tasks):
    if active_tasks == 0:
        return 0  # Underloaded
    if active_tasks <= 5:
        return 100  # Healthy
    if active_tasks <= 7:
        return 80  # Slightly overloaded
    return 50  # Overloaded
```

#### // TODO: Complete the rest of the KPI calculation section

## 5. Frontend Implementation

### 5.1 Dashboard Component Structure

```svelte
<!-- src/routes/+page.svelte -->
<script lang="ts">
  import { onMount } from 'svelte';
  import { dashboard } from '$lib/apis';
  import { isManagerOrLeader } from '$lib/stores/auth';
  
  let stats: DashboardPayload | null = null;
  let loading = true;
  
  onMount(async () => {
    stats = await dashboard.get();
    loading = false;
  });
</script>

{#if loading}
  <LoadingSpinner />
{:else if stats}
  <!-- KPI Summary (supervisor+) -->
  {#if $isManagerOrLeader && stats.kpi_summary}
    <KPISummaryStrip data={stats.kpi_summary} />
  {/if}
  
  <!-- My Tasks (all roles) -->
  <MyTasksSection tasks={stats.my_tasks} />
  
  <!-- Activity Feed (all roles) -->
  <ActivityFeed items={stats.recent_activity} />
  
  <!-- Team Health (supervisor+) -->
  {#if $isManagerOrLeader && stats.team_health}
    <TeamHealthSection members={stats.team_health} />
  {/if}
{/if}
```

### 5.2 API Client

```typescript
// lib/apis/dashboard.ts
export interface DashboardPayload {
  my_tasks: TaskCard[];
  team_health?: TeamHealthMember[];
  kpi_summary?: KPISummary;
  recent_activity: ActivityFeedItem[];
}

export const dashboard = {
  async get(): Promise<DashboardPayload> {
    const response = await fetch('/api/dashboard/');
    if (!response.ok) throw new Error('Failed to fetch dashboard');
    return response.json();
  }
};
```

### 5.3 Data Testids

For Playwright testing, sections include `data-testid` attributes:

```svelte
<div data-testid="kpi-summary-section">
  <p data-testid="kpi-avg-score">{avg_score}</p>
  <p data-testid="kpi-completion-rate">{completion_rate}%</p>
  <p data-testid="kpi-needs-attention">{needs_attention_count}</p>
</div>

<div data-testid="my-tasks-section">
  {#each my_tasks as task}
    <div data-testid="task-card" data-overdue={task.is_overdue} data-due-soon={task.is_due_soon}>
      ...
    </div>
  {/each}
</div>

<div data-testid="team-health-section">
  {#each team_health as member}
    <div data-testid="team-health-member" data-at-risk={member.status === 'red'}>
      ...
    </div>
  {/each}
</div>

<div data-testid="activity-feed-section">
  {#each recent_activity as activity}
    <div data-testid="activity-feed-item">
      ...
    </div>
  {/each}
</div>
```

## 6. Backend Implementation

### 6.1 Dashboard Route Handler

```python
# app/routers/dashboard.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.visibility import visible_sub_team_ids

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

@router.get("/")
async def get_dashboard(
    db: AsyncSession,
    current_user: User = Depends(get_current_user)
):
    # Get my tasks
    my_tasks = await get_my_tasks(db, current_user)
    
    # Get recent activity
    allowed_ids = await visible_sub_team_ids(db, current_user)
    recent_activity = await get_recent_activity(db, current_user, allowed_ids)
    
    payload = {
        "my_tasks": my_tasks,
        "recent_activity": recent_activity
    }
    
    # Add supervisor+ sections
    if is_manager_or_leader(current_user):
        payload["team_health"] = await get_team_health(db, current_user, allowed_ids)
        payload["kpi_summary"] = await get_kpi_summary(db, current_user, allowed_ids)
    
    return payload
```

### 6.2 My Tasks Query

```python
async def get_my_tasks(db: AsyncSession, user: User):
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    
    result = await db.execute(
        select(Task)
        .options(selectinload(Task.assignee))
        .where(
            Task.assignee_id == user.id,
            Task.status != TaskStatus.done
        )
        .order_by(
            Task.due_date.asc().nulls_last()
        )
    )
    tasks = result.scalars().all()
    
    # Calculate flags
    for task in tasks:
        task.is_overdue = task.due_date and task.due_date < now.date()
        task.is_due_soon = task.due_date and (task.due_date - now.date()).days <= 2
    
    return tasks
```

### 6.3 Team Health Query

```python
async def get_team_health(db: AsyncSession, user: User, allowed_ids):
    # Get users in visible sub-teams
    result = await db.execute(
        select(User).where(User.sub_team_id.in_(allowed_ids))
    )
    users = result.scalars().all()
    
    members = []
    for u in users:
        # Count active tasks
        active_result = await db.execute(
            select(func.count(Task.id))
            .where(
                Task.assignee_id == u.id,
                Task.status != TaskStatus.done
            )
        )
        active_tasks = active_result.scalar()
        
        # Count overdue tasks
        overdue_result = await db.execute(
            select(func.count(Task.id))
            .where(
                Task.assignee_id == u.id,
                Task.due_date < datetime.now(timezone.utc).date(),
                Task.status != TaskStatus.done
            )
        )
        overdue_tasks = overdue_result.scalar()
        
        # Calculate status
        status = calculate_health_status(active_tasks, overdue_tasks)
        
        members.append({
            "user_id": u.id,
            "full_name": u.full_name,
            "avatar_url": u.avatar_url,
            "active_tasks": active_tasks,
            "overdue_tasks": overdue_tasks,
            "status": status
        })
    
    return members
```

## 7. Testing

### 7.1 Backend Tests

```python
# tests/test_dashboard.py

async def test_member_dashboard_shape(db, member_user):
    response = await client.get("/api/dashboard/", headers=member_user["headers"])
    assert response.status_code == 200
    
    data = response.json()
    assert "my_tasks" in data
    assert "recent_activity" in data
    assert "team_health" not in data
    assert "kpi_summary" not in data

async def test_supervisor_dashboard_shape(db, supervisor_user):
    response = await client.get("/api/dashboard/", headers=supervisor_user["headers"])
    assert response.status_code == 200
    
    data = response.json()
    assert "my_tasks" in data
    assert "team_health" in data
    assert "kpi_summary" in data
    assert "recent_activity" in data
```

### 7.2 Frontend Playwright Tests

```typescript
// tests/dashboard-member.spec.ts

test('member sees tasks and activity feed, but not team health or KPI', async ({ page }) => {
  await loginAsMember(page);
  await page.goto('/');
  
  const taskSection = page.locator('[data-testid="my-tasks-section"]');
  await expect(taskSection).toBeVisible();
  
  const activityFeed = page.locator('[data-testid="activity-feed-section"]');
  await expect(activityFeed).toBeVisible();
  
  const teamHealth = page.locator('[data-testid="team-health-section"]');
  await expect(teamHealth).not.toBeVisible();
  
  const kpiSummary = page.locator('[data-testid="kpi-summary-section"]');
  await expect(kpiSummary).not.toBeVisible();
});
```

## 8. Performance Considerations

### 8.1 Query Optimization

- Use indexes on `assignee_id`, `sub_team_id`, `due_date`
- Limit activity feed to 5 items
- Cache KPI calculations (future)
- Use async database operations

### 8.2 Frontend Optimization

- Lazy load heavy sections
- Debounce dashboard refresh
- Use virtual scrolling for long lists (future)

## 9. Future Enhancements

### 9.1 Planned Features

- **Real-time Dashboard:** WebSocket updates for live data
- **Customizable Dashboard:** User can arrange sections
- **Drill-down Views:** Click metrics to see detailed breakdowns
- **Historical Trends:** KPI trends over time
- **Benchmarking:** Compare against team averages

### 9.2 Technical Debt

- Add caching layer for KPI calculations
- Implement real-time updates via WebSocket
- Add comprehensive error handling
- Optimize database queries for large teams
- Add loading states for better UX
