# Phase 31: Dashboard API & Data Contract - Context

**Gathered:** 2026-05-06
**Status:** Ready for planning

<domain>
## Phase Boundary

Extend `GET /api/dashboard/` to return a single role-aware payload in one call, replacing the existing generic `DashboardStats` response. The new payload contains: `my_tasks` (all roles), `team_health` (supervisor/assistant_manager/manager), `kpi_summary` (supervisor/assistant_manager/manager), and `recent_activity` (all roles). The phase also ships typed Pydantic schemas for the new payload and pytest backend test coverage for role-conditional payload shape.

This phase does not redesign the frontend dashboard (`+page.svelte`) — that is Phase 32. It does not introduce new database tables; all data is derived from existing Task, User, StandupPost, and KPI models.

</domain>

<decisions>
## Implementation Decisions

### Schema Migration
- **D-01:** Replace `DashboardStats` in place — the existing schema and endpoint shape are dropped entirely. Old fields (`total_tasks`, `todo_tasks`, `in_progress_tasks`, `done_tasks`, `overdue_tasks`, `total_team_members`, `upcoming_milestones`, `recent_tasks`) are removed. The new `DashboardPayload` schema replaces them. Phase 32 targets the new shape exclusively.

### my_tasks
- **D-02:** Each task item uses a new slim `DashboardTaskItem` schema with fields: `id` (int), `title` (str), `project_name` (str | None), `status` (TaskStatus), `priority` (TaskPriority | None), `due_date` (date | None), `is_overdue` (bool), `is_due_soon` (bool).
- **D-03:** Max 20 items returned. Sort order: overdue tasks first (due_date ascending), then not-yet-due tasks (due_date ascending), then tasks with no due date last.
- **D-04:** `is_overdue` = `due_date < now` AND task is not in a done/completed custom status. `is_due_soon` = `due_date` within 48 hours AND not already overdue. (Matches TASKS-02 requirement.)
- **D-05:** Filtered to tasks where `Task.assignee_id == current_user.id`. Excludes tasks in done/completed status (i.e. tasks the user still needs to act on).

### team_health (supervisor / assistant_manager / manager only)
- **D-06:** Reuse the existing performance computation from `performance.py` — each team member entry includes `user_id`, `full_name`, `avatar_url`, `status` (green/yellow/red), `active_tasks` (int), `completed_30d` (int).
- **D-07:** Add `overdue_tasks` (int) per member so Phase 32 can specifically highlight at-risk members. This field augments the existing `TeamMemberPerformance` shape for the dashboard context.
- **D-08:** Results are scoped to the caller's visible sub-team(s) using the existing `visible_sub_team_ids` service. A manager with no `X-SubTeam-ID` header sees all teams.
- **D-09:** `team_health` key is absent from the response for `member` role (not null, not empty list — key omitted entirely).

### kpi_summary (supervisor / assistant_manager / manager only)
- **D-10:** Extract the KPI scorecard computation from `backend/app/routers/performance.py` (the scorecard-building logic) into a shared service at `backend/app/services/kpi.py`. Both the dashboard endpoint and the performance router call this shared function — the dashboard KPI strip always shows numbers consistent with `/performance`.
- **D-11:** `kpi_summary` shape: `{ avg_score: int, completion_rate: float, needs_attention_count: int }`.
  - `avg_score`: average KPI score across visible team members (same formula as Phase 16).
  - `completion_rate`: completed tasks / total tasks for visible scope, as a float 0.0–1.0.
  - `needs_attention_count`: count of members where `kpi_score < 70` (Phase 16 D-22 threshold).
- **D-12:** `kpi_summary` key is absent from the response for `member` role.

### recent_activity (all roles)
- **D-13:** Returns the 5 most recent standup posts scoped to the caller's visibility rules (same sub-team scoping logic as `updates.py` `list_posts`).
- **D-14:** Each activity item includes: `post_id` (int), `author_id` (int), `author_name` (str), `created_at` (datetime), `field_values` (dict — full JSONB, Phase 32 decides what to render as preview).
- **D-15:** New slim schema `DashboardActivityItem` for these fields.

### Backend Tests
- **D-16:** Extend `backend/tests/test_dashboard.py` with pytest async tests covering:
  - Member role: response contains `my_tasks` and `recent_activity`; `team_health` and `kpi_summary` keys are absent.
  - Supervisor role: response contains all four keys (`my_tasks`, `team_health`, `kpi_summary`, `recent_activity`).
  - Shape validation for each section (field presence, not just HTTP 200).
  - `my_tasks` urgency sort: overdue tasks appear before upcoming tasks.

### Claude's Discretion
- Exact Pydantic schema file placement (extend `schemas/work.py` or create `schemas/dashboard.py`).
- Whether to use `Optional` fields with `None` or structural omission for role-gated sections (either is acceptable; `Optional[X] = None` is simpler to type).
- Exact KPI service function signature and file structure within `services/kpi.py`.
- Whether `my_tasks` excludes only `TaskStatus.done` or also done-equivalent custom statuses — planner should check `custom_status.is_done` join if feasible without over-engineering.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase Scope & Requirements
- `.planning/ROADMAP.md` — Phase 31 goal, success criteria, and dependency on Phase 30
- `.planning/REQUIREMENTS.md` — API-01 through API-05 (backend API requirements for this phase)
- `.planning/PROJECT.md` — v2.4 milestone target features and out-of-scope constraints

### Existing Dashboard Endpoint
- `backend/app/routers/dashboard.py` — Current endpoint to replace; uses `get_sub_team` dependency and returns old `DashboardStats`
- `backend/app/schemas/work.py` line 439 — Current `DashboardStats` definition to replace

### KPI & Performance Computation
- `backend/app/routers/performance.py` lines 532–589 — KPI scorecard logic to extract into shared service
- `backend/app/schemas/kpi.py` — `KPIMemberScorecard`, `KPIOverviewSummary`, `KPIScoreBreakdown` schemas
- `backend/app/schemas/performance.py` — `TeamMemberPerformance` schema (reused for team_health)
- `.planning/phases/16-advanced-kpi-dashboard/16-CONTEXT.md` — KPI scoring decisions: needs_attention threshold = kpi_score < 70; completion uses `custom_status.is_done` (D-10)

### Visibility & Auth
- `backend/app/services/visibility.py` — `visible_sub_team_ids`, `is_leader`, `is_manager`, `is_member`; visibility scoping patterns
- `backend/app/utils/auth.py` — `get_current_user`, `get_sub_team`, `require_leader_or_manager` dependencies
- `.planning/phases/29-scoped-team-visibility-leadership-rbac/29-CONTEXT.md` — Four-role model, visibility rules, and cross-surface enforcement pattern

### Standup Posts (recent_activity)
- `backend/app/routers/updates.py` — `list_posts` scoping pattern: `sub_team_id` filter, manager sees all with no header
- `backend/app/models/updates.py` — `StandupPost` model fields

### Tests
- `backend/tests/test_dashboard.py` — Existing (nearly empty) test file to extend
- `backend/tests/conftest.py` — Test fixtures: `async_client`, `db_session`, user role fixtures

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `backend/app/routers/performance.py`: Scorecard computation (lines 532–589) produces `avg_score`, `needs_attention`, and per-member KPI scores — extract this into `services/kpi.py` and call from both routers.
- `backend/app/services/visibility.py`: `visible_sub_team_ids(session, user)` and `resolve_visible_sub_team` already implement the full Phase 29 visibility model. Dashboard must use these, not write new scope logic.
- `backend/app/routers/updates.py` `list_posts`: Sub-team scoping pattern — `sub_team=None` for managers, `sub_team.id` filter for everyone else. Dashboard `recent_activity` should mirror this exactly.
- `backend/app/schemas/performance.py` `TeamMemberPerformance`: Has `status`, `active_tasks`, `completed_30d`, `avg_cycle_time`, `on_time_rate`. Dashboard adds `overdue_tasks` on top.
- `backend/app/utils/auth.py` `get_sub_team` dependency: Already resolves the Phase 29 sub-team context via `X-SubTeam-ID` header. Re-use in the dashboard endpoint.

### Established Patterns
- Router pattern: async FastAPI with `Depends(get_current_user)`, `Depends(get_db)`, `Depends(get_sub_team)`, Pydantic response model.
- Role-gated sections: check `is_leader(current_user) or is_manager(current_user)` from `services/visibility.py`.
- Schema changes for response models only (no new DB tables): add to existing schema files or new `schemas/dashboard.py`.
- Test pattern: `@pytest.mark.asyncio`, `async_client: AsyncClient`, JWT cookie in headers, fixture-based users from `conftest.py`.

### Integration Points
- `backend/app/routers/dashboard.py`: Replace existing `get_dashboard` handler and `DashboardStats` import with new `DashboardPayload` schema and role-aware logic.
- `backend/app/schemas/work.py` or new `schemas/dashboard.py`: Add `DashboardTaskItem`, `DashboardActivityItem`, `DashboardTeamHealthMember`, `DashboardKpiSummary`, `DashboardPayload`.
- `backend/app/schemas/__init__.py`: Export new dashboard schemas.
- `backend/app/services/kpi.py` (new): Extracted KPI scorecard service function, called by both `performance.py` and `dashboard.py`.
- `backend/tests/test_dashboard.py`: Extend with role-conditional shape tests.

</code_context>

<specifics>
## Specific Ideas

- The dashboard endpoint should feel like a single fast call — all four sections computed in one async handler, no client-side fan-out.
- `team_health` and `kpi_summary` should be completely absent from the JSON response (key not present) for members, not `null` — this is cleaner for Phase 32 role-conditional rendering.
- The KPI scorecard extraction is the most architecturally interesting part of this phase: it creates a reusable service that keeps the performance page and dashboard strip in sync automatically.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 31-dashboard-api-data-contract*
*Context gathered: 2026-05-06*
