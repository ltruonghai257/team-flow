# Phase 31: Dashboard API & Data Contract — Research

**Date:** 2026-05-07
**Status:** Complete

---

## RESEARCH COMPLETE

---

## Summary

Phase 31 is backend-only. The UI keyword gate detects "dashboard" in the phase name, but CONTEXT.md explicitly states: "This phase does not redesign the frontend dashboard — that is Phase 32." No UI-SPEC required.

---

## Existing Dashboard Endpoint

**File:** `backend/app/routers/dashboard.py` (111 lines)

- `GET /api/dashboard/` returns `DashboardStats` — 8 generic aggregate fields: `total_tasks`, `todo_tasks`, `in_progress_tasks`, `done_tasks`, `overdue_tasks`, `total_team_members`, `upcoming_milestones`, `recent_tasks`
- No role-gating — same response for all roles
- Already uses `Depends(get_current_user)` + `Depends(get_sub_team)` — both dependencies stay
- `DashboardStats` is in `backend/app/schemas/work.py` line 439–448 and exported from `schemas/__init__.py`
- Full replacement per D-01 — all old fields drop, no backward-compat needed (pre-release)

---

## KPI Computation

**File:** `backend/app/routers/performance.py` lines 440–596

### Structure

- `get_kpi_overview` (lines 443–596): runs a per-member aggregate SQL query, scores each member with five helper functions, derives `scorecards`, `avg_score`, `needs_attention`, `total_active`, `total_completed`
- Helper functions (lines 379–437):
  - `_completed_task_filter()` — returns `[CustomStatus.is_done.is_(True)]` conditions
  - `_active_task_filter()` — returns `[CustomStatus.is_done.is_(False)]` conditions
  - `_score_workload(active_tasks: int) -> int` — ≤7 → 100, ≤10 → 70, else → 40
  - `_score_velocity(completed_30d: int) -> int` — min(100, count × 10)
  - `_score_cycle_time(avg_hours: Optional[float]) -> int`
  - `_score_on_time(on_time_pct: float) -> int`
  - `_score_defects(mttr_hours: Optional[float]) -> int`
- `_get_or_create_kpi_weights(db, sub_team)` (lines 42–56) — DB helper, returns `KPIWeightSettings`

### Extraction Plan

Create `backend/app/services/kpi.py` with:
1. All helper functions (move from performance.py)
2. `get_or_create_kpi_weights(db, sub_team)` (rename from private to public)
3. `compute_kpi_overview(db, sub_team) -> KpiComputeResult` — main async function

**`KpiComputeResult` dataclass fields:**
- `scorecards: list[KPIMemberScorecard]` — full per-member KPI scorecards
- `avg_score: int` — weighted average KPI score
- `needs_attention_count: int` — members with kpi_score < 70 or any critical reason
- `completion_rate: float` — `total_completed_30d / (total_active + total_completed_30d)` or 0.0
- `per_member: list[dict]` — lightweight dicts for team_health assembly: `{user_id, full_name, avatar_url, active_tasks, completed_30d, overdue_tasks, kpi_score}`

**`overdue_tasks` addition to aggregate query:**

The existing KPI aggregate query needs one extra aggregate added per member:
```python
func.count(Task.id).filter(
    Task.due_date < now,
    Task.custom_status_id == CustomStatus.id,
    CustomStatus.is_done.is_(False),
).label("overdue_tasks"),
```

**`status` derivation for team_health (D-06):**
Derived from workload score boundaries (same as `_score_workload`):
- `active_tasks > 10` → `"red"`
- `active_tasks > 7` → `"yellow"`
- else → `"green"`

**`performance.py` refactor:** `get_kpi_overview` calls `compute_kpi_overview(db, sub_team)` and wraps result into `KPIOverviewResponse` — no behavior change, only extraction.

---

## Schema Analysis

### To Create: `backend/app/schemas/dashboard.py`

Five new Pydantic schemas (D-02, D-07, D-11, D-14, D-01):

```
DashboardTaskItem:
  id: int, title: str, project_name: Optional[str],
  status: TaskStatus, priority: Optional[TaskPriority],
  due_date: Optional[date], is_overdue: bool, is_due_soon: bool

DashboardTeamHealthMember:
  user_id: int, full_name: str, avatar_url: Optional[str],
  status: str,  # "green" | "yellow" | "red"
  active_tasks: int, completed_30d: int, overdue_tasks: int

DashboardKpiSummary:
  avg_score: int, completion_rate: float, needs_attention_count: int

DashboardActivityItem:
  post_id: int, author_id: int, author_name: str,
  created_at: datetime, field_values: dict

DashboardPayload:
  my_tasks: List[DashboardTaskItem]
  team_health: Optional[List[DashboardTeamHealthMember]] = None
  kpi_summary: Optional[DashboardKpiSummary] = None
  recent_activity: List[DashboardActivityItem]
  model_config = {"exclude_none": True}   # D-09, D-12 — keys absent (not null) for members
```

### To Remove: `DashboardStats` from `schemas/work.py` and `schemas/__init__.py`

Remove the 8 old fields. Plan 2 handles this alongside the router rewrite.

### `schemas/__init__.py` Updates

- Plan 1 adds: `DashboardPayload`, `DashboardTaskItem`, `DashboardTeamHealthMember`, `DashboardKpiSummary`, `DashboardActivityItem`
- Plan 2 removes: `DashboardStats`

---

## New Endpoint Logic

### `my_tasks` (D-02 to D-05)

Query tasks where `assignee_id == current_user.id` excluding done:
```
NOT (Task.status == TaskStatus.done)
AND (Task.custom_status_id IS NULL OR CustomStatus.is_done != True)
```
Needs `outerjoin(CustomStatus, Task.custom_status_id == CustomStatus.id)`.

Compute per task in Python:
- `is_overdue = due_date is not None and due_date < now`
- `is_due_soon = due_date is not None and now <= due_date <= now + 48h`

Sort (Python, after fetch):
1. Overdue tasks (is_overdue=True) by due_date ASC
2. Upcoming tasks (is_overdue=False, due_date not None) by due_date ASC
3. No due_date tasks last

Limit: 20 items.

### `team_health` (supervisor/assistant_manager/manager only — D-06 to D-09)

Built from `KpiComputeResult.per_member` returned by `services.kpi.compute_kpi_overview(db, sub_team)`.
Absent from response for `member` role (key omitted via `exclude_none`).

### `kpi_summary` (supervisor/assistant_manager/manager only — D-10 to D-12)

Built from `KpiComputeResult.avg_score`, `needs_attention_count`, `completion_rate`.
Absent from response for `member` role.

### `recent_activity` (all roles — D-13 to D-15)

Query `StandupPost` with sub-team scoping matching `updates.py list_posts` pattern:
```python
query = select(StandupPost)
if sub_team is not None:
    query = query.where(StandupPost.sub_team_id == sub_team.id)
query = query.order_by(StandupPost.id.desc()).limit(5)
```
Join/refresh author for `author_name`. Returns `DashboardActivityItem`.

---

## Visibility & Auth Patterns

- `is_leader(user) or is_manager(user)` — supervisor+ gate for team_health + kpi_summary
- `get_sub_team` dependency already resolves `X-SubTeam-ID` header via `resolve_visible_sub_team`
- Manager with no header: `sub_team = None` → KPI query sees all teams, standup query sees all posts

---

## Test Infrastructure

**File:** `backend/tests/conftest.py`

- `async_client` + `db_session` fixtures exist (SQLite in-memory)
- `sub_team`, `user_with_sub_team` fixtures exist
- No supervisor/member JWT fixtures — new tests create users inline via `_create_user` helper pattern (seen in `test_visibility.py`)
- Token pattern: `create_access_token({"sub": str(user.id)})` then `headers={"Cookie": f"access_token={token}"}`
- Existing `test_dashboard.py` has one broken placeholder test using `admin_user.token` (no such fixture) — safe to replace all tests

---

## Phase Decomposition

### Wave 1 — Plan 31-01: Foundation (schemas + KPI service)

**Files:**
- `backend/app/schemas/dashboard.py` (NEW)
- `backend/app/services/kpi.py` (NEW)
- `backend/app/schemas/__init__.py` (add exports)
- `backend/app/routers/performance.py` (refactor to use KPI service)

**Safe to run before Plan 2**: adds new code only, does not remove anything existing.

### Wave 2 — Plan 31-02: Endpoint Rewrite

**Files:**
- `backend/app/routers/dashboard.py` (full rewrite)
- `backend/app/schemas/work.py` (remove DashboardStats)
- `backend/app/schemas/__init__.py` (remove DashboardStats, add DashboardPayload export)

**Depends on Plan 31-01**: needs new schemas and KPI service.

### Wave 3 — Plan 31-03: Backend Test Coverage

**Files:**
- `backend/tests/test_dashboard.py` (rewrite with D-16 coverage)

**Depends on Plan 31-02**: tests the complete endpoint.

---

## Validation Architecture

Test scenarios required by D-16:
1. **Member role** — response has `my_tasks` + `recent_activity`; `team_health` and `kpi_summary` keys **absent**
2. **Supervisor role** — response has all 4 keys (`my_tasks`, `team_health`, `kpi_summary`, `recent_activity`)
3. **Shape validation** — field presence checks on each section (not just HTTP 200)
4. **`my_tasks` sort** — overdue task (due_date < now) appears before upcoming task (due_date > now)

Test infrastructure notes:
- SQLite test DB works with `JSON` type (not native JSONB)
- `StandupPost.field_values` uses `JSON().with_variant(JSONB(), "postgresql")` — compatible with SQLite
- Need `Project` fixture for `my_tasks.project_name`; can use `project_name = None` for simplicity

---

*Phase: 31-dashboard-api-data-contract*
*Research completed: 2026-05-07*
