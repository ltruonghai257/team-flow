# Technology Stack — Milestone 2 Additions

**Project:** TeamFlow v2.0
**Researched:** 2026-04-24
**Scope:** NEW dependencies only — what the existing FastAPI + SvelteKit 5 + PostgreSQL 16 stack needs to support the six new feature areas.

---

## New Dependencies

### Frontend

| Library | Version | Feature | Why |
|---------|---------|---------|-----|
| `layerchart` | `next` (already installed) | KPI charts (burndown, velocity, cycle time) | Already in `package.json`; was removed from performance pages in favour of inline SVG but is available. Provides Chart.js-quality composable charts built on top of `d3` with native Svelte 5 rune support. Use it instead of adding a separate charting lib. |
| `d3-shape` | `^3.2.0` (already installed) | KPI charts | Already in `package.json`; `layerchart` consumes it internally. No separate install. |
| `svelte-dnd-action` | `^0.9.69` (already installed) | Custom status column reordering | Already in `package.json` and used on the Kanban board. The same library handles horizontal column drag-reorder — no new DnD dependency needed. |

**Net new frontend packages: zero.** All charting and DnD needs are covered by what is already installed.

Note on `layerchart` version tag: the `"next"` dist-tag on npm points to layerchart v2 pre-release (the Svelte 5 / runes-compatible major). Confidence: MEDIUM — based on `package.json` presence and the comment in the performance page noting it was temporarily removed. Before using it, verify the installed version with `yarn list layerchart` and consult https://layerchart.com/docs.

### Backend

| Library | Version | Feature | Why |
|---------|---------|---------|-----|
| No new packages required | — | All features | `apscheduler` covers sprint reminders; `sqlalchemy` + `alembic` covers all new schema; `pydantic` covers validation for new types. |

**Net new backend packages: zero.**

The only backend concern is Alembic migration files — the schema additions below must be expressed as Alembic revisions, not `create_all`. The project's own docs note that `create_all` is not production-safe; Milestone 2 must fix this.

---

## Schema Additions

All additions go into `backend/app/models.py` and generate Alembic migrations. No new ORM or DB driver is needed.

### 1. Team Hierarchy

```
Organization (1)
  └── Team (N)       -- each Team has 1 supervisor_id FK → users.id
        └── TeamMember (N)  -- join table: team_id, user_id, joined_at
```

**New tables:**

- `organizations` — `id`, `name`, `created_at`. Single-row in practice (private deployment), but the table enforces the hierarchy cleanly without special-casing.
- `teams` — `id`, `name`, `organization_id FK`, `supervisor_id FK → users.id`, `created_at`. Replaces the implicit "one global team" assumption.
- `team_members` — `id`, `team_id FK`, `user_id FK`, `joined_at`. Composite unique on `(team_id, user_id)`.

**Existing model changes:**

- `User` — add optional `team_id FK → teams.id` for fast denormalized lookup of a user's primary team. (A user belongs to exactly one sub-team in this model; the `team_members` table is the authoritative join but `team_id` shortcut avoids joins on common queries.)
- `Project` — add `team_id FK → teams.id` (nullable for backward compat during migration). Projects belong to a team.

**Pattern rationale:** A flat adjacency list (org → team → user) is sufficient for this depth. Recursive CTEs (for arbitrary depth hierarchies) are unnecessary complexity given the fixed two-level structure.

### 2. Sprint Model

```
Project (1)
  └── Milestone (N)
        └── Sprint (N)    -- time-boxed iteration within a milestone
              └── Task (N) -- tasks assigned to a sprint
```

**New table: `sprints`**

| Column | Type | Notes |
|--------|------|-------|
| `id` | Integer PK | |
| `name` | String | e.g. "Sprint 3" |
| `milestone_id` | FK → milestones.id | |
| `start_date` | DateTime | |
| `end_date` | DateTime | |
| `goal` | Text nullable | sprint goal statement |
| `status` | Enum(`planned`, `active`, `completed`) | |
| `created_at` | DateTime | |

**Existing model changes:**

- `Task` — add `sprint_id FK → sprints.id` (nullable; tasks not in any sprint remain valid).

### 3. Custom Kanban Statuses

The existing `TaskStatus` Python enum (`todo/in_progress/review/done/blocked`) is hardcoded. Custom statuses require moving status definitions to the database.

**New table: `kanban_statuses`**

| Column | Type | Notes |
|--------|------|-------|
| `id` | Integer PK | |
| `name` | String | display label, e.g. "In QA" |
| `slug` | String unique | URL/API-safe key, e.g. "in_qa" |
| `color` | String | hex color for board column |
| `position` | Integer | column order, mutable by drag |
| `scope` | Enum(`global`, `project`) | global = team default; project = per-project override |
| `project_id` | FK → projects.id nullable | null when scope=global |
| `team_id` | FK → teams.id nullable | null when scope=project (inherits from team) |
| `is_terminal` | Boolean default false | marks "done"-equivalent statuses for KPI calculations |
| `created_at` | DateTime | |

**Existing model changes:**

- `Task.status` — migrate from `Enum(TaskStatus)` column to `String` column referencing `kanban_statuses.slug`. This is the breaking change. The migration path: add `String` column `status_slug`, backfill from existing enum values, drop old column, rename.
- The Python `TaskStatus` enum becomes a thin set of sentinel constants for the seed/defaults, not an ORM column type.

**Why slug not FK:** Storing the slug string on the task avoids a join on every task read and survives status renaming gracefully (slug stays stable, display name can change). FK enforcement is done at the application layer (validate slug exists before saving).

### 4. Task Types

Simple enum addition to the `tasks` table.

**New column on `tasks`:**

- `task_type` — `Enum('feature', 'bug', 'task', 'improvement')` default `'task'`, not nullable after backfill migration.

No new table needed.

### 5. Advanced KPIs

KPI metrics (velocity, burndown, cycle time, throughput, defect rate, MTTR) are **computed queries, not stored data**. No new schema tables are required.

The inputs are already present or added above:
- Velocity: count of `done` tasks per sprint (needs `sprint_id` on tasks + `is_terminal` on status)
- Burndown: count of open vs closed tasks over time using `tasks.updated_at` + `tasks.completed_at`
- Cycle time: `tasks.completed_at - tasks.created_at` (or a `started_at` column if needed — see note below)
- Throughput: tasks completed per time window
- Defect rate: tasks with `task_type='bug'` / total tasks per sprint
- MTTR: mean of `completed_at - created_at` for bug-type tasks

**Optional addition:** `tasks.started_at` — timestamp set when status first moves to `in_progress`. Without this, cycle time approximations using `created_at` overcount queue time. Recommended: add as nullable DateTime, set by a backend hook on status transition.

**KPI data delivered via new `/api/analytics` router**, returning pre-aggregated JSON from SQL window functions. No separate analytics DB or time-series store is needed at this scale (< 10K tasks).

### 6. Sprint/Release Reminders

The existing `EventNotification` model and `apscheduler` loop already handle time-based reminder delivery. The only changes needed:

- Add `'sprint'` and `'milestone_release'` to the `NotificationEventType` enum (currently only `schedule` and `task`).
- The scheduler job `process_due_notifications` already polls on 60s intervals and flips `pending → sent` — no changes to the job itself.
- Auto-creation of sprint-end reminders: when a sprint is created or its `end_date` changes, create/update an `EventNotification` row with `remind_at = end_date - 24h` for each team supervisor. Done in the sprint router, not a new scheduler job.

---

## What NOT to Add

| Temptation | Why to Avoid |
|-----------|--------------|
| **A separate charting library (Chart.js, Recharts, Visx, etc.)** | `layerchart` is already installed and purpose-built for SvelteKit. Adding Chart.js on top creates two charting systems. |
| **A dedicated time-series database (InfluxDB, TimescaleDB)** | Overkill for < 10K tasks in a single-org tool. SQL window queries on PostgreSQL are sufficient and already fast. |
| **GraphQL / Hasura for KPI queries** | Adds an entire query layer when REST endpoints returning JSON aggregates work fine. |
| **A separate job queue (Celery, Redis, RQ) for reminders** | `apscheduler` with `AsyncIOScheduler` already handles the notification delivery loop. The scheduler is in-process, adequate for this load, and already deployed. Redis would require a new infrastructure dependency for no gain. |
| **Separate `team_roles` table** | The existing `UserRole` enum (`admin/supervisor/member`) is sufficient. Supervisors are identified by `role = supervisor` scoped to a team via `teams.supervisor_id`. A full role-per-team RBAC table is unnecessary complexity for a two-level hierarchy. |
| **Recursive CTE / adjacency list for hierarchy** | The hierarchy is exactly two levels (org → team). A self-referencing recursive structure adds query complexity for no benefit. |
| **Soft-delete framework** | Status fields (`sprint.status`, `kanban_statuses`) already handle logical deletion. A generic soft-delete library is unnecessary abstraction. |
| **`@dnd-kit/svelte` or other DnD libraries** | `svelte-dnd-action` already handles Kanban column drag-reorder. Do not introduce a second DnD library. |

---

## Integration Notes

### Charting (layerchart)

`layerchart` was installed as `"next"` and is present in `node_modules` but is currently bypassed in both performance pages (comments say "layerchart removed — using inline SVG"). Before using it for KPI charts, confirm the installed version is Svelte-5-compatible by checking `node_modules/layerchart/package.json`. If it is the v2 runes-compatible build, use it. If it is the old v1 (Svelte 4), upgrade: `yarn add layerchart@next` again to pull the latest pre-release.

The existing inline SVG bar chart in `/performance` is simple enough to leave as-is. Use `layerchart` only for the new, more complex charts: burndown line chart, velocity bar chart, cycle time histogram.

### Custom Statuses and Existing Kanban DnD

`svelte-dnd-action` currently drives row (task card) DnD. Column reordering uses the same library with a horizontal `flipDurationMs` variant applied to the status columns array. The `position` integer on `kanban_statuses` is the persistence target — on drop, PATCH the updated position values for the affected columns.

### Task Status Migration (Breaking Change)

Changing `tasks.status` from a PostgreSQL enum type to a `VARCHAR` is a multi-step Alembic migration:
1. Add `status_slug VARCHAR` column.
2. `UPDATE tasks SET status_slug = status::text`.
3. `ALTER TABLE tasks DROP COLUMN status`.
4. `ALTER TABLE tasks RENAME COLUMN status_slug TO status`.
5. Seed `kanban_statuses` table with the five defaults matching the old enum values.

This migration must run before any code changes that reference `status` as a string. Flag this as the first migration in the milestone.

### Notification System

The `NotificationEventType` Python enum must be extended with `sprint` and `milestone_release` values. Because this is a PostgreSQL `ENUM` column, the Alembic migration must use `ALTER TYPE` to add the new values before the application code references them.

```sql
ALTER TYPE notificationeventtype ADD VALUE IF NOT EXISTS 'sprint';
ALTER TYPE notificationeventtype ADD VALUE IF NOT EXISTS 'milestone_release';
```

### RBAC Scoping

The existing `get_current_user` dependency enforces `role`-based access. New endpoints for sprint management, status configuration, and KPI analytics should add team-scoped checks: the requesting user's `team_id` must match the resource's `team_id`. This is application-layer logic, not a new library.

### Alembic Migration Requirement

The existing codebase uses `create_all` for schema setup (documented in ARCHITECTURE.md as "not production-safe"). Milestone 2 adds schema that cannot be expressed safely with `create_all` (enum extensions, column type changes). **The first phase of this milestone must convert the project to Alembic-driven migrations** before any schema additions land.

---

## Confidence Assessment

| Area | Confidence | Basis |
|------|------------|-------|
| Frontend — no new packages needed | HIGH | Verified against `package.json`; `layerchart` and `svelte-dnd-action` confirmed present |
| Backend — no new packages needed | HIGH | Verified against `requirements.txt`; `apscheduler` and `sqlalchemy` cover all needs |
| Schema design (hierarchy, sprints, statuses) | HIGH | Derived from reading actual `models.py`; patterns are standard SQL |
| layerchart v2 Svelte 5 compatibility | MEDIUM | Package installed as `"next"` tag; code comments suggest it was tried and bypassed; needs verification at implementation time |
| KPI query complexity (SQL only) | MEDIUM | Standard window functions; verified the task table has `completed_at` and `updated_at`; `started_at` addition is recommended but optional |
