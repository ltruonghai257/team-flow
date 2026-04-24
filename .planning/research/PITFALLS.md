# Domain Pitfalls: TeamFlow Milestone 2

**Domain:** Adding multi-team hierarchy, sprint model, custom Kanban statuses, task types, and advanced KPIs to an existing FastAPI + SvelteKit 5 + PostgreSQL 16 app
**Researched:** 2026-04-24
**Applies to:** Subsequent milestone on a working app with real data

---

## Risk 1: Multi-Team Hierarchy Migration — Unscoped Data Leakage After Re-association

**Problem**

The existing `Project`, `Task`, `User`, and `TeamInvite` models have no `team_id` or `organization_id` column. The current data model is flat: all users, all projects, and all tasks exist in one implicit global namespace. Adding `Organization → sub-team → member` hierarchy requires adding foreign key columns to `users`, `projects`, and possibly `tasks`.

The critical failure mode is **not the migration itself — it is forgetting to add WHERE clauses to the query layer after migration**. Every existing endpoint (`GET /api/tasks/`, `GET /api/projects/`, `GET /api/performance/team`, `GET /api/timeline/`) returns data without any team-scoping filter. Once hierarchy is introduced, a supervisor in Sub-Team A can still query `/api/tasks/?project_id=7` and get tasks belonging to Sub-Team B's project if the API is not updated.

The existing `require_supervisor` guard in `auth.py` only validates role — it does not validate team membership. It is easy to add hierarchy to models and migrations but miss six query endpoints that need a `WHERE project.team_id = current_user.team_id` predicate.

**Signs**

- A supervisor can hit `/api/tasks/` and see tasks from another team's project when filtered by `project_id`
- The `GET /api/performance/team` endpoint (which does a full `User` table scan joined to `Task`) returns members who belong to other sub-teams
- The timeline endpoint returns all projects (current implementation: `select(Project)` with no team filter)
- Dashboard stats (`/api/dashboard/`) aggregate across all teams

**Prevention**

- Add a `team_id` column to `projects` first (nullable initially; then backfill; then NOT NULL)
- Write a helper `get_team_for_user(current_user)` that returns the user's team_id; use this as a mandatory join/filter in every endpoint that touches Projects or Tasks
- Audit every `select(Task)` and `select(Project)` call in all routers before marking the phase complete — there are currently 7 files to check: `tasks.py`, `projects.py`, `milestones.py`, `timeline.py`, `performance.py`, `dashboard.py`, `ai.py`
- Write a test: authenticate as Supervisor-A, create a task under Team-B's project via `project_id`, assert 403 or 404

**Phase to address:** Phase that introduces multi-team hierarchy models and migration

---

## Risk 2: Custom Kanban Statuses — Hardcoded Enum Breaks the Frontend and AI Layer

**Problem**

`TaskStatus` is a Python enum with five hardcoded values (`todo`, `in_progress`, `review`, `done`, `blocked`). This enum is used in:

- `models.py` — the `status` DB column is typed `Enum(TaskStatus)`
- `schemas.py` — `TaskCreate`, `TaskUpdate`, `TaskOut` all accept/emit `TaskStatus`
- `tasks.py` — the `_AI_PARSE_SYSTEM_PROMPT` explicitly lists `todo|in_progress|review|done|blocked` as valid values
- `KanbanBoard.svelte` — `const columns = ['todo', 'in_progress', 'review', 'done', 'blocked']` is hardcoded
- `AgileView.svelte` — `statusCycle` is a hardcoded map of status transitions
- `utils` — `statusLabels` and `statusColors` are hardcoded maps

Migrating to DB-driven statuses requires changing the PostgreSQL column type from an `ENUM` type (PostgreSQL native enum `taskstatus`) to a `VARCHAR` referencing a `kanban_statuses` table. PostgreSQL `ALTER TYPE` cannot remove enum values. The migration to drop the `taskstatus` type requires: create new VARCHAR column, copy data, drop old column, rename — a three-step destructive migration that must be done correctly or existing rows get NULL statuses.

Additionally, the AI parse prompt must be updated dynamically (or prompted with the current status list at runtime) otherwise the AI will still produce only the old five values.

**Signs**

- Alembic migration fails with `cannot drop type taskstatus because other objects depend on it`
- AI task parse returns `status: "todo"` even after old enum values are deprecated
- KanbanBoard renders only five hardcoded columns regardless of DB-configured statuses
- Drag-and-drop assigns a status string that no longer exists in the status list, silently setting invalid state

**Prevention**

- The migration must use a multi-step approach:
  1. Add `status_new VARCHAR(50)` column with default `'todo'`
  2. `UPDATE tasks SET status_new = status::text`
  3. Add FK constraint `status_new REFERENCES kanban_statuses(slug)`
  4. Drop old `status` column (this releases the enum type dependency)
  5. Rename `status_new` to `status`
  6. Drop `taskstatus` enum type
- Keep `done` as a reserved slug that the system recognizes for completion logic — the `completed_at` field is populated when status transitions to `done`, so this slug must always exist and never be renamed
- The frontend `statusLabels`, `statusColors`, and `statusCycle` maps must become API-driven; fetch statuses once at app init and store in a Svelte store
- Add a `is_terminal` boolean to the `kanban_statuses` table to replace the hardcoded `done` check in `update_task`
- Update the AI parse prompt to inject current valid status slugs at request time rather than hardcoding them in the system prompt string

**Phase to address:** Phase that adds custom Kanban statuses; must run the multi-step migration in a single Alembic revision

---

## Risk 3: Sprint Model — Orphaned Tasks When Sprints End

**Problem**

A sprint is a time-boxed container. Tasks assigned to a sprint that are not completed when the sprint ends become "orphaned" — they have a `sprint_id` pointing to a closed sprint. Without an explicit policy, these tasks remain assigned to the old sprint indefinitely. Velocity calculations (tasks completed per sprint) then reflect only what was finished, and the backlog never surfaces these orphaned tasks in the next sprint's burndown.

The burndown accuracy problem compounds this: if burndown is computed as `(tasks_in_sprint WHERE status != done) / total_tasks_in_sprint`, adding tasks to a sprint mid-sprint inflates the starting point retroactively, making the burndown chart show an impossible "upward" movement (scope creep without documentation).

**Signs**

- Tasks with `sprint_id = 5` (a closed sprint) still appear with `status = 'in_progress'`
- Burndown chart shows total work going up mid-sprint (new tasks added without recording a scope-change event)
- Velocity metric overstates the team's throughput because it counts tasks from multiple sprints

**Prevention**

- Add a `sprint_id` column to `tasks` (nullable; `SET NULL ON DELETE` is wrong here — use `RESTRICT` or keep a soft reference and handle in application logic)
- Add a `sprint_status` enum to `Sprint` (`planning`, `active`, `completed`) and enforce at the API level: once a sprint is `completed`, tasks cannot be added to it
- Implement an explicit "sprint close" operation that: sets unfinished tasks' `sprint_id` to the next sprint (or NULL if no next sprint exists), records a `SprintSnapshot` row capturing the state at close time for accurate historical burndown
- For burndown accuracy, use a **snapshot model**: on sprint start, write a `sprint_daily_snapshots` table with `(sprint_id, date, remaining_count)` via the scheduler job. Compute burndown from snapshots, not live task counts
- Add a `scope_change_log` table or a `scope_change_count` field on `Sprint` so the UI can flag sprints where scope changed

**Phase to address:** Phase that introduces the Sprint model; burndown snapshot job added in the same phase as sprint creation

---

## Risk 4: Task Types — Backfill Strategy Causes KPI Skew

**Problem**

Every existing task has no `task_type` field. When task types (`feature`, `bug`, `task`, `improvement`) are added, the backfill decision determines how useful historical KPI data will be. There are three choices, all with drawbacks:

1. **Default all existing tasks to `task`** — cycle time and defect rate by type will show zero bugs in history, making historical defect-rate metrics meaningless
2. **Leave existing tasks NULL** — KPI queries must handle NULL in GROUP BY aggregations; easy to forget, producing misleading percentages (e.g., defect rate = bugs/total where total excludes NULL-typed tasks)
3. **Force users to classify retroactively** — operationally impractical; supervisors will not do it

The third option (AI classification at migration time) is attractive but risky: the AI classifies based on task title and description, and a wrong batch classification corrupts historical KPI baselines permanently.

**Signs**

- `GET /api/kpi/defect-rate` returns 0% for all historical periods (because all old tasks are `task` type)
- Velocity-by-type chart shows only `feature` and `bug` types for recent tasks, making the chart look empty for older sprints
- GROUP BY `task_type` returns a mix of `NULL` and valid values, inflating the `task` bucket

**Prevention**

- Add `task_type VARCHAR(20) DEFAULT 'task' NOT NULL` in the migration; backfill all existing rows to `'task'`
- Make KPI queries that break down by type explicitly exclude or document the historical baseline period: `WHERE created_at >= [milestone2_start_date]`
- Add a database constraint (`CHECK task_type IN (...)`) so future inserts cannot produce NULL types
- Document the limitation in the KPI dashboard UI: "Historical data before [date] is classified as 'task'; type breakdown is accurate from [date] forward"
- Do not use AI batch-classification during migration; the risk of silent mis-classification on hundreds of rows with no rollback path outweighs the benefit

**Phase to address:** Phase that adds task types; migration must include a backfill, and KPI queries must account for the historical gap

---

## Risk 5: Advanced KPIs — N+1 Queries on Analytics Endpoints

**Problem**

The existing `performance.py` already issues two separate queries per page load (metrics + collaboration count). Milestone 2 KPI endpoints (velocity per sprint, burndown per sprint, cycle time by type, defect rate) will need data from `sprints`, `tasks`, `task_type`, and potentially `sprint_daily_snapshots`. The N+1 pattern emerges when:

- Velocity is computed by iterating over sprints and issuing a `SELECT count(*) FROM tasks WHERE sprint_id = ?` per sprint
- Cycle time by type issues a per-type query inside a loop
- Burndown fetches snapshot rows per sprint in a loop
- The timeline endpoint already has a secondary query inside its project loop (`unassigned_stmt` is executed per project — this is an existing N+1)

For a team of 5-15 people with 10 sprints and 4 task types, N+1 patterns produce 40-100 queries on a single analytics page load. On Azure App Service B1 with a remote PostgreSQL instance (10-20ms round-trip per query), this adds 400ms-2000ms latency to dashboard loads.

**Signs**

- KPI endpoint takes >1 second for a team with 50+ tasks
- SQLAlchemy debug logs show repeated `SELECT count(*) FROM tasks WHERE sprint_id = X` for each sprint
- Adding a second supervisor causes analytics page to become noticeably slower

**Prevention**

- Write all KPI aggregations as single GROUP BY queries: `SELECT sprint_id, count(*), avg(cycle_time) FROM tasks GROUP BY sprint_id` rather than per-sprint subqueries
- Use `func.count(Task.id).filter(...)` with aggregate filters (pattern already used in `performance.py`) — replicate this pattern for sprint and type breakdowns
- Fix the existing N+1 in `timeline.py`: the `unassigned_stmt` inside the project loop is a pre-existing issue; fix it in the same phase by fetching all unassigned tasks in one query keyed by `project_id`
- Add a `EXPLAIN ANALYZE` test in the phase review for any new analytics endpoint with >5 tasks in the dataset
- For burndown, do not recompute from raw task history on each request; read from the `sprint_daily_snapshots` table (written by the scheduler) instead

**Phase to address:** Phase that adds KPI analytics endpoints; timeline N+1 fix can be included as a related data-access improvement

---

## Risk 6: Timeline Visibility — Role-Scoped Filtering Forgotten at the API Level

**Problem**

The requirement states: members see only projects they are assigned to; supervisors see their team-wide view. The current `GET /api/timeline/` implementation does `select(Project)` with no filter — it returns all projects to any authenticated user regardless of role.

The SvelteKit frontend enforces visibility via UI (hiding sections, conditional rendering), but the API returns all data. Frontend-only filtering is not a security boundary: any team member can call `GET /api/timeline/` directly and see all projects, milestones, and assignee information for other teams.

This pattern will silently persist into Milestone 2 if the team hierarchy phase only adds the data models without auditing the timeline router. The `require_supervisor` guard is used correctly in `performance.py` but is absent from `timeline.py` (which currently accepts any authenticated user).

**Signs**

- A member (not supervisor) hits `GET /api/timeline/` and receives projects they have no tasks in
- After adding team hierarchy, a member from Sub-Team A can view timeline data for Sub-Team B's projects
- The SvelteKit timeline component is conditionally rendering things the API should never have sent in the first place

**Prevention**

- Add the team-scoping filter to `GET /api/timeline/` in the same phase that adds team hierarchy — not as a separate phase
- For members: filter to `projects WHERE id IN (SELECT DISTINCT project_id FROM tasks WHERE assignee_id = current_user.id)`
- For supervisors: filter to `projects WHERE team_id = current_user.team_id`
- Write an integration test: authenticate as member, assert that timeline only contains projects with assigned tasks
- Never rely on frontend conditional rendering as a data boundary; the test is "what does the raw API response contain?"

**Phase to address:** Phase that adds multi-team hierarchy; timeline visibility enforcement must be a checklist item in that phase's completion criteria, not deferred

---

## Risk 7: APScheduler Job Persistence — Sprint/Release Reminders Lost on Restart

**Problem**

The existing `scheduler_jobs.py` creates an `AsyncIOScheduler` with a single in-memory job (`process_due_notifications` every 60 seconds). The scheduler state is held in the Python process — there is no `APScheduler` job store configured, so `_scheduler` is an in-memory object. This is acceptable for the existing notification job because the `EventNotification` rows are in PostgreSQL; a restart only means a one-minute processing gap.

Sprint and release reminders are different: if reminders are implemented as one-off `scheduler.add_job(send_reminder, run_date=sprint.end_date - timedelta(days=1))` calls, those jobs are lost on every app restart. Azure App Service restarts instances on deployment, scale events, and occasional platform recycling. A sprint ending on Friday that had a reminder scheduled on Thursday will silently never fire if the app was restarted after the job was added but before it ran.

**Signs**

- Sprint-end reminders fire inconsistently; sometimes they work, sometimes they do not
- After deploying a new version, all pending sprint reminders for the next 24 hours fail to fire
- No mechanism to reconstruct which sprint reminders have already been sent vs are pending

**Prevention**

- Do not store sprint/release reminders as APScheduler `run_date` jobs; store them as rows in the existing `EventNotification` table (the infrastructure already exists: `event_type`, `event_ref_id`, `remind_at`, `status`)
- The existing `process_due_notifications` job already polls `EventNotification WHERE status = pending AND remind_at <= now` every 60 seconds — sprint reminders are free to use this system with no new scheduler infrastructure
- When a sprint is created or its `end_date` is updated, insert/update `EventNotification` rows for the relevant users (e.g., supervisor gets a reminder 24 hours before sprint end)
- If a sprint `end_date` changes, delete old `EventNotification` rows for that sprint's `event_ref_id` and re-insert with the new `remind_at`
- Add a `(event_type, event_ref_id, user_id)` unique constraint to `EventNotification` to prevent duplicate reminder rows on repeated saves

**Phase to address:** Phase that adds sprint model and reminder notifications; no new APScheduler jobs needed — use the existing EventNotification row-poll pattern

---

## Risk 8: Alembic Migration Chain — Enum Type Operations Break Multi-Step Migrations

**Problem**

The codebase has three Alembic revisions so far; `a1b2c3d4e5f6_add_role_enum.py` shows the pattern for changing an existing enum column on `users`. That migration works because `userrole` was not yet a PostgreSQL native type — it was added from scratch.

Milestone 2 faces a harder problem: `taskstatus` is already a PostgreSQL native ENUM type (created implicitly by SQLAlchemy from `Enum(TaskStatus)` on the `tasks.status` column). Adding new values to a PostgreSQL ENUM is safe (`ALTER TYPE taskstatus ADD VALUE 'custom'`). But the custom Kanban statuses feature requires removing the enum entirely and switching to a VARCHAR foreign key — you cannot remove values from a PostgreSQL ENUM, only add them. Attempting to run `DROP TYPE taskstatus` while the `tasks.status` column still references it will fail with a dependency error.

A second risk: if Milestone 2 adds an `Organization` table, `Team` table (with FK to org), `team_id` on `users` (with FK to team), and `team_id` on `projects` (with FK to team), all in separate migrations, the ordering constraint between migrations matters — deploying them out of order will fail with FK constraint violations.

**Signs**

- `alembic upgrade head` fails on the custom-status migration with `ERROR: cannot drop type taskstatus because other objects depend on it`
- A migration adding `team_id` FK to `projects` runs before the migration creating the `teams` table, causing a foreign key error
- Rollback (`alembic downgrade`) fails midway because the down path was not tested

**Prevention**

- Plan the Milestone 2 migration sequence explicitly before writing any migration file:
  1. `organizations` table
  2. `teams` table (FK to organizations)
  3. `team_id` nullable column on `users` (FK to teams)
  4. `team_id` nullable column on `projects` (FK to teams)
  5. Backfill: assign all existing users and projects to a default team
  6. `kanban_statuses` table (slug, label, order, is_terminal, team_id nullable)
  7. Seed default five statuses
  8. Multi-step taskstatus→VARCHAR migration (columns approach described in Risk 2)
  9. `sprints` table (FK to milestones)
  10. `sprint_id` nullable column on `tasks`
  11. `task_type` VARCHAR column with default 'task', NOT NULL
- Test each migration file's `downgrade()` path locally before merging
- Never use `op.execute("ALTER TYPE ... ADD VALUE")` in a transaction block — PostgreSQL requires enum value additions to run outside a transaction; use `op.execute(...); op.get_bind().dialect.do_commit(op.get_bind().connection)` or set `transaction_per_migration = False` in Alembic env

**Phase to address:** All phases that touch schema; the migration sequence must be drafted as a team artifact at the start of Milestone 2, not planned per-phase in isolation

---

## Risk 9: Burndown Accuracy — Computed vs Snapshot

**Problem**

Burndown charts are almost always implemented naively as: "query tasks in sprint, group by day of `completed_at`". This only works if no tasks are added or removed from the sprint after it starts. In practice, scope changes (adding tasks, removing tasks, changing estimates) mean the denominator of the burndown changes retroactively. A computed burndown from live data cannot accurately reconstruct "what was the state on day 3 of the sprint?"

The existing `performance.py` uses live computation for all metrics. For trend data (8-week history), this works because historical task state does not change. But sprint burndown is different: a task added on day 5 of a 10-day sprint was not in scope on day 1, and the burndown chart should not back-project it.

**Signs**

- The burndown chart for a completed sprint looks different each time it is loaded (if tasks were retroactively re-assigned)
- Adding a task to a sprint mid-sprint makes the burndown chart start higher than it actually started, making the team look less productive than they were
- Sprint velocity inconsistently changes for historical sprints (tasks re-assigned after sprint closed)

**Prevention**

- Write a daily snapshot job: extend `process_due_notifications` in `scheduler_jobs.py` (or add a second job) that runs at midnight UTC and writes one row per active sprint to `sprint_daily_snapshots (sprint_id, date, total_tasks, remaining_tasks, added_today, completed_today)`
- Burndown API endpoint reads from `sprint_daily_snapshots`, not from live task counts
- On sprint start, write the initial snapshot immediately (do not wait for the first midnight job)
- Velocity is computed from the snapshot table's `completed_today` sum for the sprint, not from a live count of `completed_at` within the sprint's date range

**Phase to address:** Phase that adds sprint model; the snapshot job must be added in the same phase as the sprint creation endpoint, not deferred to the KPI phase

---

## Risk 10: TaskStatus / Completion Logic Tied to Hardcoded 'done' Slug

**Problem**

In `tasks.py`, the `update_task` endpoint has logic that checks `if new_status == TaskStatus.done` to set `completed_at`. This works because `TaskStatus.done` is a known enum value. After migrating to DB-driven statuses, this check must use a different mechanism — either:
- A hardcoded string `'done'` (fragile if the terminal status slug is renamed)
- A lookup of the `is_terminal = true` status from `kanban_statuses` (correct but adds a DB lookup on every status update)

If this logic is missed during the custom-status migration, tasks marked with a custom terminal status (e.g., `'released'`) will never have `completed_at` set. This corrupts cycle time, on-time rate, and all performance metrics that depend on `completed_at`.

**Signs**

- Tasks transitioned to a custom terminal status show `completed_at = NULL`
- KPI cycle time metric returns NULL for tasks completed with non-`done` statuses
- Burndown chart never shows those tasks as "completed"

**Prevention**

- Add `is_terminal BOOLEAN NOT NULL DEFAULT FALSE` to the `kanban_statuses` table
- In `update_task`, replace `if new_status == TaskStatus.done` with `if new_status_row.is_terminal`; the status row must be fetched or cached per request
- The default five statuses seed should mark `done` as `is_terminal = true`; all others `false`
- Cache the `is_terminal` flag on the task status string level (e.g., a `terminal_slugs` set loaded at startup from the DB) to avoid a per-update lookup
- Test: create a custom `released` status with `is_terminal=true`, transition a task to it, assert `completed_at` is set

**Phase to address:** Phase that adds custom Kanban statuses; must be addressed in the same migration that removes the `TaskStatus` enum

---

## Summary: Phase Assignment Matrix

| Pitfall | Phase | Severity |
|---------|-------|----------|
| Multi-team data leakage (unscoped queries) | Team hierarchy phase | Critical |
| Custom status enum migration (multi-step) | Custom Kanban status phase | Critical |
| Alembic migration sequence planning | Before Milestone 2 begins | Critical |
| Timeline visibility enforcement | Team hierarchy phase (same phase, not deferred) | High |
| Sprint orphaned tasks + burndown snapshots | Sprint model phase | High |
| APScheduler job loss on restart (reminders) | Sprint model phase | High |
| Completion logic tied to hardcoded 'done' | Custom Kanban status phase | High |
| Task type backfill + KPI historical gap | Task types phase | Medium |
| N+1 queries on analytics endpoints | KPI analytics phase | Medium |
| Burndown computed vs snapshot accuracy | Sprint model phase | Medium |
