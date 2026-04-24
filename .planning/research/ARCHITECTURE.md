# Architecture Patterns

**Domain:** Multi-team task management with sprints, custom Kanban, and KPI analytics
**Researched:** 2026-04-24
**Milestone:** v2.0 — Adding to existing FastAPI + SvelteKit 5 + PostgreSQL 16 app

---

## Data Model Changes

### New Models (add to `backend/app/models.py`)

#### 1. `SubTeam`
Introduces the hierarchy layer between the flat "everyone is on one team" model and a proper multi-team org. `User` gains a nullable `sub_team_id` FK.

```
SubTeam
  id            PK
  name          String NOT NULL
  description   Text nullable
  supervisor_id Integer FK → users.id nullable   # one supervisor per sub-team
  created_at    DateTime
```

No parent `Team` model is needed: the PROJECT.md spec says "Organization → N sub-teams". The organization is the app instance itself (single-org deployment). Adding a `Team` wrapper model would be speculative complexity.

#### 2. `Sprint`
Time-boxed iteration belonging to a milestone within a project. Both FKs are present to allow filtering by either without joins.

```
Sprint
  id           PK
  name         String NOT NULL
  start_date   DateTime NOT NULL
  end_date     DateTime NOT NULL
  milestone_id Integer FK → milestones.id nullable
  project_id   Integer FK → projects.id NOT NULL
  created_at   DateTime
```

`milestone_id` is nullable because sprints may be created before milestone assignment, and some projects run sprints without milestone decomposition.

#### 3. `CustomTaskStatus`
Replaces the hard-coded `TaskStatus` enum on the Kanban board. Scoped to either a team or a project.

```
CustomTaskStatus
  id         PK
  name       String NOT NULL
  color      String NOT NULL  # hex color e.g. "#6366f1"
  order      Integer NOT NULL # display order within scope
  team_id    Integer FK → sub_teams.id nullable
  project_id Integer FK → projects.id nullable
  is_default Boolean default False  # marks the fallback "done-equivalent" for KPI
  created_at DateTime

  CHECK (team_id IS NOT NULL OR project_id IS NOT NULL)
```

Scope resolution precedence: project-scoped statuses override team-scoped statuses for a given board. Neither scope → show the five built-in defaults.

### Modified Models

#### `User` — add `sub_team_id`
```
+ sub_team_id  Integer FK → sub_teams.id nullable
```
Nullable so existing users remain valid after migration. A user with no sub_team_id belongs to the "root" org without a sub-team assignment.

#### `Task` — three changes
```
+ sprint_id        Integer FK → sprints.id nullable
+ task_type        Enum(TaskType) default "task"
+ custom_status_id Integer FK → custom_task_statuses.id nullable
```

The `status` column (`Enum(TaskStatus)`) is **retained** alongside `custom_status_id`. This is the safest migration path (see Migration Strategy below). New code writes both fields during the transition period; old code reads `status` unchanged.

Add new enum to `models.py`:
```python
class TaskType(str, enum.Enum):
    feature = "feature"
    bug = "bug"
    task = "task"
    improvement = "improvement"
```

### Relationship Additions

| Model | New Relationship |
|-------|-----------------|
| `SubTeam` | `supervisor` → `User`; `members` → `User` (back_populates `sub_team`) |
| `User` | `sub_team` → `SubTeam`; back_populates on `assigned_tasks`, `created_tasks` unchanged |
| `Sprint` | `project` → `Project`; `milestone` → `Milestone`; `tasks` → `Task` |
| `Task` | `sprint` → `Sprint`; `custom_status` → `CustomTaskStatus` |
| `Project` | `sprints` → `Sprint` (backref) |
| `Milestone` | `sprints` → `Sprint` (backref) |

---

## New API Routes

### `backend/app/routers/sub_teams.py` (new file)
Prefix: `/api/sub-teams`

| Method | Path | Auth | Purpose |
|--------|------|------|---------|
| GET | `/` | any authenticated | List all sub-teams |
| POST | `/` | supervisor/admin | Create sub-team |
| GET | `/{id}` | any authenticated | Get sub-team + members |
| PATCH | `/{id}` | supervisor/admin | Update name/description/supervisor |
| DELETE | `/{id}` | admin | Delete sub-team |
| GET | `/{id}/members` | any authenticated | List members of sub-team |
| POST | `/{id}/members/{user_id}` | supervisor/admin | Assign user to sub-team |
| DELETE | `/{id}/members/{user_id}` | supervisor/admin | Remove user from sub-team |

### `backend/app/routers/sprints.py` (new file)
Prefix: `/api/sprints`

| Method | Path | Auth | Purpose |
|--------|------|------|---------|
| GET | `/` | any authenticated | List sprints (filter: project_id, milestone_id, active) |
| POST | `/` | supervisor/admin | Create sprint |
| GET | `/{id}` | any authenticated | Get sprint + task summary |
| PATCH | `/{id}` | supervisor/admin | Update sprint |
| DELETE | `/{id}` | supervisor/admin | Delete sprint |
| GET | `/{id}/tasks` | any authenticated | Tasks in sprint |

### `backend/app/routers/task_statuses.py` (new file)
Prefix: `/api/task-statuses`

| Method | Path | Auth | Purpose |
|--------|------|------|---------|
| GET | `/` | any authenticated | List statuses (filter: team_id, project_id) |
| POST | `/` | supervisor/admin | Create custom status |
| PATCH | `/{id}` | supervisor/admin | Update name/color/order |
| DELETE | `/{id}` | supervisor/admin | Delete custom status |
| POST | `/reorder` | supervisor/admin | Bulk reorder (list of {id, order}) |

### `backend/app/routers/kpi.py` (new file)
Prefix: `/api/kpi`

| Method | Path | Auth | Purpose |
|--------|------|------|---------|
| GET | `/velocity` | supervisor/admin | Sprint velocity (story points or task count per sprint) |
| GET | `/burndown` | supervisor/admin | Burndown for a sprint (computed from task state) |
| GET | `/cycle-time` | supervisor/admin | Avg cycle time by task_type |
| GET | `/throughput` | supervisor/admin | Tasks completed per week/sprint |
| GET | `/defect-rate` | supervisor/admin | Bug tasks as % of total completed |
| GET | `/mttr` | supervisor/admin | Mean time to resolve bug tasks |

All KPI endpoints accept query params: `project_id`, `sprint_id`, `team_id`, `from_date`, `to_date`.

### Modified Existing Routes

#### `backend/app/routers/tasks.py`
- `GET /api/tasks/` — add `sprint_id` and `task_type` filter params
- `POST /api/tasks/` — `TaskCreate` schema gains `sprint_id` and `task_type` fields
- `PATCH /api/tasks/{id}` — `TaskUpdate` schema gains `sprint_id`, `task_type`, `custom_status_id`
- Status transition logic: when `custom_status_id` is provided AND the referenced status `is_default=True` (done-equivalent), set `completed_at`; otherwise clear it. Preserve existing `status` enum write for backward compat.

#### `backend/app/routers/dashboard.py`
- Dashboard stats queries that count by `status == TaskStatus.done` continue to work unchanged because `status` enum column is retained.
- Add `upcoming_sprints` list (sprints ending within 7 days) to `DashboardStats` response.

#### `backend/app/scheduler_jobs.py`
Add a second job `process_sprint_reminders()` alongside the existing `process_due_notifications()`:
- Runs on same 60s interval (add second `sched.add_job(...)` call)
- Queries `Sprint` where `end_date` is within N days and no reminder notification already exists for that sprint+user pair
- Creates `EventNotification` rows — re-uses existing notification delivery pipeline without any new infrastructure

---

## Frontend Routes & Components

### New Routes

#### `/sprints` — Sprint management page
**File:** `frontend/src/routes/sprints/+page.svelte`
- List sprints grouped by project
- Create/edit/delete sprint (supervisor only)
- Click through to sprint board (filtered Kanban for that sprint)

#### `/kpi` — KPI analytics dashboard (supervisor only)
**File:** `frontend/src/routes/kpi/+page.svelte`
- Tab bar: Velocity | Burndown | Cycle Time | Throughput | Defect Rate | MTTR
- Each tab fetches from `/api/kpi/{metric}`
- Charts: use existing pattern (no new chart library introduced unless one is already present; use CSS bars or SVG paths to stay consistent)

### Modified Routes

#### `/tasks` (`frontend/src/routes/tasks/+page.svelte`)
- Task form gains three new fields: `sprint_id` selector, `task_type` selector, `custom_status_id` selector (optional, shown when custom statuses exist for current project/team)
- Status filter dropdown: populate from `customStatuses` store when available, fall back to hard-coded list
- `changeStatus()` handler: send `custom_status_id` instead of `status` string when custom statuses are active

#### `/team` (`frontend/src/routes/team/+page.svelte`)
- Add sub-team list panel
- Allow supervisor to create sub-teams and assign members to them
- Show sub-team badge on member cards

### New Components

#### `frontend/src/lib/components/sprints/SprintCard.svelte`
Shows sprint name, date range, progress bar (done/total tasks), days remaining.

#### `frontend/src/lib/components/sprints/SprintSelector.svelte`
Dropdown to pick a sprint within a project; used in the task form and as a board filter.

#### `frontend/src/lib/components/kpi/BurndownChart.svelte`
SVG line chart of remaining tasks over sprint days. Data shape: `{day: number, remaining: number}[]`.

#### `frontend/src/lib/components/kpi/VelocityBar.svelte`
Horizontal bar chart of completed task count per sprint. Reusable; driven by props only.

#### `frontend/src/lib/components/tasks/TaskTypeSelect.svelte`
Single-purpose select for feature/bug/task/improvement. Extracted to keep task form readable.

### Modified Components

#### `frontend/src/lib/components/tasks/KanbanBoard.svelte`
- `columns` array currently hardcoded to `['todo', 'in_progress', 'review', 'done', 'blocked']`
- Change to accept a `statuses` prop: `{ id: number | string, name: string, color: string }[]`
- Derive columns from prop; fall back to the existing hardcoded list when prop is empty
- `handleFinalize`: when custom statuses active, call `onStatusChange(taskId, status.id)` with the numeric ID instead of a string slug

#### `frontend/src/lib/components/tasks/AgileView.svelte`
- `statusCycle` record is hardcoded — make it dynamic by computing next status from the ordered `statuses` prop
- `progressFor()` currently counts `t.status === 'done'`; change to check against the status marked `is_default: true` in the statuses list

#### `frontend/src/lib/utils.ts`
- `statusLabels` and `statusColors` are static records keyed by string slug
- Add a `buildStatusMaps(statuses)` utility that builds equivalent maps from a `CustomTaskStatus[]` array
- Existing static records remain for components that have not yet migrated

#### `frontend/src/lib/api.ts`
Add new API modules: `subTeams`, `sprints`, `taskStatuses`, `kpi` following existing domain pattern.

### New Stores

#### `frontend/src/lib/stores/statuses.ts`
```typescript
// Writable; populated on tasks page load and on team/project switch
export const customStatuses = writable<CustomTaskStatus[]>([]);
```
Avoids fetching statuses on every component mount. All Kanban/AgileView/filter components read from this store.

---

## Migration Strategy

### The Core Problem

`Task.status` is a PostgreSQL `ENUM` type (`taskstatus` in pg_catalog). Dropping it requires:
1. Converting all existing task rows to a new representation
2. All query code that filters/groups by `status` must be updated simultaneously

A single cutover migration that drops the column is high risk during active development.

### Recommended: Dual-Write with Deferred Drop

**Phase A — Add without removing (one migration)**

```sql
-- migration: add sprint, type, custom_status columns

ALTER TABLE tasks ADD COLUMN sprint_id INTEGER REFERENCES sprints(id) ON DELETE SET NULL;
ALTER TABLE tasks ADD COLUMN task_type VARCHAR(20) NOT NULL DEFAULT 'task';
ALTER TABLE tasks ADD COLUMN custom_status_id INTEGER REFERENCES custom_task_statuses(id) ON DELETE SET NULL;

-- Seed default custom statuses that mirror existing enum values
INSERT INTO custom_task_statuses (name, color, "order", is_default, team_id, project_id)
VALUES
  ('To Do',       '#6b7280', 1, false, NULL, NULL),
  ('In Progress', '#3b82f6', 2, false, NULL, NULL),
  ('Review',      '#f59e0b', 3, false, NULL, NULL),
  ('Done',        '#22c55e', 4, true,  NULL, NULL),
  ('Blocked',     '#ef4444', 5, false, NULL, NULL);

-- Backfill custom_status_id from existing status enum
UPDATE tasks SET custom_status_id = (
  SELECT id FROM custom_task_statuses WHERE name = CASE tasks.status
    WHEN 'todo'        THEN 'To Do'
    WHEN 'in_progress' THEN 'In Progress'
    WHEN 'review'      THEN 'Review'
    WHEN 'done'        THEN 'Done'
    WHEN 'blocked'     THEN 'Blocked'
  END AND team_id IS NULL AND project_id IS NULL
);
```

After this migration, both `status` (enum) and `custom_status_id` (FK) are populated. Application code dual-writes both on task create/update during the transition.

**Phase B — Confirm custom status is the source of truth**

When all board views and KPI queries read from `custom_status_id`, and the `status` enum column is no longer read by any application code, drop it:

```sql
ALTER TABLE tasks DROP COLUMN status;
DROP TYPE taskstatus;
```

This is a separate migration run only after full feature completion and QA.

**Why not use Alembic autogenerate for the enum drop?**

Alembic autogenerate handles column additions well but can mis-sequence enum type drops in PostgreSQL (it may try to drop the type before the column referencing it). The `status` column drop must be written as an explicit migration with `op.execute("ALTER TABLE tasks DROP COLUMN status")` followed by `op.execute("DROP TYPE taskstatus")` — do not rely on autogenerate for this step.

### Alembic Initialization

The codebase currently uses `create_all` (no migrations directory exists). Before writing any Phase A migration, the team must initialize Alembic:

```bash
cd backend
alembic init alembic
# Set sqlalchemy.url in alembic.ini (or use env var approach)
# Set target_metadata = Base.metadata in alembic/env.py
alembic revision --autogenerate -m "baseline_existing_schema"
alembic upgrade head
```

The baseline migration captures the current schema. All v2 migrations build on top of it.

---

## Build Order

Dependencies flow downward. Each phase can only start when the phase above it is complete.

```
Phase 1: Alembic initialization + baseline migration
         ↓ unblocks all subsequent migrations
Phase 2: SubTeam model + migration + /api/sub-teams router + /team UI update
         ↓ User.sub_team_id must exist before sprint/KPI scoping by team
Phase 3: Sprint model + migration + /api/sprints router + Sprint UI (/sprints route)
         ↓ tasks.sprint_id FK requires sprints table to exist
Phase 4: Task type + Custom status + Phase A migration (dual-write)
         ↓ custom_status_id must exist and be populated before KPIs use it
         ↓ Kanban/AgileView component update (statuses prop, dynamic columns)
Phase 5: KPI router + KPI dashboard (/kpi route)
         ↓ requires sprint_id on tasks, task_type, and custom_status is_default flag
Phase 6: Sprint reminders (scheduler job)
         ↓ requires Sprint model (Phase 3) and existing notification pipeline
Phase 7: Phase B migration (drop status enum) — deferred until KPIs + board verified
```

### Rationale

- **Alembic first** — every other phase produces a migration. Without Alembic in place, migrations are applied manually or via `create_all` race conditions. This is the single highest-risk infrastructure gap.
- **SubTeam before Sprint** — KPI scoping by team (`/api/kpi?team_id=3`) and timeline visibility gating both reference `sub_team_id` on User. Sprint queries that filter by team need this.
- **Sprint before Task changes** — `tasks.sprint_id` is a FK. The `sprints` table must exist before the tasks migration adds the FK.
- **Task type + custom status together** — both are additive column additions in the same migration. Splitting them saves nothing and doubles migration risk.
- **KPI after all task fields** — velocity, burndown, and cycle time by type all require `sprint_id`, `task_type`, and the `is_default` flag on `CustomTaskStatus` to be meaningful. Running KPI phase earlier produces queries that return zeros or require workarounds.
- **Sprint reminders after Sprint model** — the scheduler job is simple once Sprint rows exist. It shares the existing `EventNotification` + polling pipeline so no new delivery infrastructure is needed.
- **Enum drop last** — the enum column is read by existing dashboard, performance, and timeline queries. Dropping it before those queries are updated to use `custom_status_id` breaks production. Phase B migration is a cleanup step after full QA.

---

## Component Boundaries: New vs Modified

| Component | Status | Notes |
|-----------|--------|-------|
| `backend/app/models.py` | **Modified** | Add SubTeam, Sprint, CustomTaskStatus models; modify Task, User |
| `backend/app/schemas.py` | **Modified** | New schema classes for all new models; extend TaskCreate/Update/Out |
| `backend/app/routers/sub_teams.py` | **New** | — |
| `backend/app/routers/sprints.py` | **New** | — |
| `backend/app/routers/task_statuses.py` | **New** | — |
| `backend/app/routers/kpi.py` | **New** | — |
| `backend/app/routers/tasks.py` | **Modified** | Add filter params; dual-write status + custom_status_id |
| `backend/app/routers/dashboard.py` | **Modified** | Add upcoming_sprints to stats |
| `backend/app/scheduler_jobs.py` | **Modified** | Add sprint reminder job |
| `backend/app/main.py` | **Modified** | Register three new routers |
| `frontend/src/lib/api.ts` | **Modified** | Add subTeams, sprints, taskStatuses, kpi modules |
| `frontend/src/lib/utils.ts` | **Modified** | Add buildStatusMaps() utility |
| `frontend/src/lib/stores/statuses.ts` | **New** | — |
| `frontend/src/lib/components/tasks/KanbanBoard.svelte` | **Modified** | Accept statuses prop; dynamic columns |
| `frontend/src/lib/components/tasks/AgileView.svelte` | **Modified** | Dynamic status cycle; is_default for progress |
| `frontend/src/lib/components/tasks/TaskTypeSelect.svelte` | **New** | — |
| `frontend/src/lib/components/sprints/SprintCard.svelte` | **New** | — |
| `frontend/src/lib/components/sprints/SprintSelector.svelte` | **New** | — |
| `frontend/src/lib/components/kpi/BurndownChart.svelte` | **New** | — |
| `frontend/src/lib/components/kpi/VelocityBar.svelte` | **New** | — |
| `frontend/src/routes/sprints/+page.svelte` | **New** | — |
| `frontend/src/routes/kpi/+page.svelte` | **New** | — |
| `frontend/src/routes/tasks/+page.svelte` | **Modified** | New form fields; custom status filter |
| `frontend/src/routes/team/+page.svelte` | **Modified** | Sub-team panel and member assignment |
| `frontend/src/routes/+layout.svelte` | **Modified** | Add Sprints and KPI nav links |

---

## WebSocket Constraint Note

The existing `ConnectionManager` is in-memory and single-instance. Sprint reminder notifications are delivered through the existing `EventNotification` → scheduler poll → frontend polling store pipeline. They do **not** use WebSocket push.

This is the correct approach for this deployment: the polling store already exists (`notifications.ts`), the scheduler already runs, and the single-instance constraint makes in-memory WS state safe. Do not introduce WebSocket broadcast for sprint reminders — it adds nothing for a single-instance app and would break under any future horizontal scale.

If real-time sprint reminder push is needed later, the correct path is: store reminder state in `EventNotification` (already done), and have the frontend poll or use Server-Sent Events rather than WebSocket broadcast.

---

## KPI Query Implementation Notes

**Burndown:** Computed on-the-fly, not snapshotted. For a sprint with N total tasks, query tasks in that sprint, group by `date(completed_at)`, accumulate. This is accurate but not historical — a task re-opened after completion will shift the curve. Snapshot-based burndown requires a `task_snapshots` table (daily cron); defer to a future milestone if historical accuracy is required.

**Velocity:** `COUNT(task_id) WHERE sprint_id = X AND custom_status.is_default = true` (done-equivalent). If `estimated_hours` is populated consistently, use `SUM(estimated_hours)` instead for story-point-style velocity.

**Cycle Time:** `AVG(completed_at - created_at)` for tasks with `custom_status.is_default = true`, grouped by `task_type`. Only meaningful for tasks that have a `completed_at` value.

**MTTR:** Same as cycle time but filtered to `task_type = 'bug'`.

All KPI queries are read-only and run against existing `tasks` table data. No new event-sourcing or snapshot tables are needed for v2.0.

---

## Sources

- Codebase analysis: `backend/app/models.py`, `backend/app/routers/tasks.py`, `backend/app/scheduler_jobs.py`, `frontend/src/lib/components/tasks/KanbanBoard.svelte`, `frontend/src/lib/utils.ts`
- Project specification: `.planning/PROJECT.md`
- Existing architecture: `.planning/codebase/ARCHITECTURE.md`, `.planning/codebase/STRUCTURE.md`
- Confidence: HIGH — all findings derived from direct codebase inspection, not inferred
