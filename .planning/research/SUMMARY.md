# Project Research Summary

**Project:** TeamFlow v2.0
**Domain:** Multi-team task management with sprint-driven project management and KPI analytics
**Researched:** 2026-04-24
**Confidence:** HIGH

## Executive Summary

TeamFlow v2.0 adds six interdependent features to a working FastAPI + SvelteKit 5 + PostgreSQL 16 app: multi-team hierarchy, sprint model, custom Kanban statuses, task types, advanced KPIs, and sprint/release reminders. The research is grounded in direct codebase inspection — all schema recommendations derive from reading the actual models.py, all frontend recommendations from reading the actual components. Zero new dependencies are needed. layerchart, svelte-dnd-action, apscheduler, and sqlalchemy already cover everything. The build is schema additions and logic, not infrastructure.

The recommended approach sequences features by hard dependency: Alembic baseline first (the codebase uses create_all today, which is a known gap), then team hierarchy (gates all scoping), then sprints (requires team context), then custom statuses (the riskiest migration — Postgres enum to VARCHAR), then KPIs (requires all prior features), then reminders. Task types are fully isolated and can run in parallel with team hierarchy. The enum drop is deferred cleanup after full QA.

The top three risks are data leakage from unscoped queries after hierarchy is added, the multi-step Postgres enum migration for custom statuses, and the completed_at completion logic still tied to the hardcoded done slug. All three are preventable with explicit completion criteria per phase: audit all seven query files when hierarchy lands, write the 5-step migration plan before coding the status feature, and replace the hardcoded done check with is_terminal in the same phase as the enum migration.

---

## Stack Additions

**Net new dependencies: zero.** All needs are covered by what is already installed.

| Layer | Package | Status | Use |
|-------|---------|--------|-----|
| Frontend | layerchart@next | Already in package.json | Burndown, velocity, cycle time charts |
| Frontend | svelte-dnd-action | Already in package.json | Kanban column reorder (same lib, horizontal variant) |
| Backend | apscheduler | Already in requirements.txt | Sprint reminders via existing poll loop |
| Backend | alembic | Already in requirements.txt | All schema migrations |

**Verify before using layerchart:** The next dist-tag was installed but code comments indicate it was bypassed. Run `yarn list layerchart` to confirm it is the Svelte-5-compatible v2 build before the KPI phase begins.

### Schema Additions Required

All expressed as Alembic revisions — never create_all.

| Migration | What | Breaking? |
|-----------|------|-----------|
| Alembic baseline | Capture current schema as revision 0 | No |
| sub_teams table | New hierarchy model | No |
| sub_team_id on users, team_id on projects | FK additions (nullable, then backfilled) | No |
| sprints table | New sprint model | No |
| sprint_id (nullable) + story_points (nullable) on tasks | FK and field additions | No |
| task_type VARCHAR NOT NULL DEFAULT task on tasks | New column with backfill | No |
| custom_task_statuses table + seed 5 defaults | New status model | No |
| custom_status_id (nullable) on tasks + backfill | Dual-write start; old status enum retained | No |
| ALTER TYPE notificationeventtype ADD VALUE sprint | Postgres enum extension | No |
| Drop tasks.status enum + DROP TYPE taskstatus | Phase B cleanup — deferred until KPIs verified | Yes (deferred) |

**Migration ordering constraint:** The full sequence must be drafted as a team artifact before writing any migration file. FK violations from out-of-order migrations require manual DB intervention to fix.

### Task Status Migration Detail (Dual-Write Strategy)

The tasks.status Postgres ENUM cannot be dropped while the column references it. The safe path:

1. Add custom_status_id INTEGER FK to custom_task_statuses.id (nullable)
2. Seed the 5 default statuses matching existing enum values
3. Backfill custom_status_id from existing status enum values
4. Application dual-writes both columns during transition
5. When all read paths use custom_status_id, run Phase B: drop old column, then DROP TYPE taskstatus

Do not use alembic autogenerate for the enum drop step — write it as explicit op.execute() calls.

---

## Feature Table Stakes

For a 5-15 person dev team, all six features should ship. Sprints, task types, and burndown are daily-use features, not nice-to-haves.

### Multi-Team Hierarchy

| Category | Feature |
|----------|---------|
| Table stakes | Org to sub-teams; 1 supervisor per sub-team; admin sees all; members see only their team projects; supervisor scoped to own team |
| Differentiator | Supervisor can compare their team KPIs against org-level aggregate |
| Anti-feature | Multi-team membership per user; nested sub-team hierarchy; auto-created team chat channels |

### Sprint Model

| Category | Feature |
|----------|---------|
| Table stakes | Sprint with start/end/name/status; belongs to milestone; tasks assigned to sprint (nullable); only one active sprint per milestone (API-enforced); backlog = sprint_id IS NULL; move tasks between sprints |
| Differentiator | Sprint close action that moves incomplete tasks to next sprint or backlog; drag tasks from backlog into sprint during planning |
| Anti-feature | Automatic sprint scheduling; locking tasks once sprint is active; sub-tasks |

### Custom Kanban Statuses

| Category | Feature |
|----------|---------|
| Table stakes | Supervisor/admin defines team-wide status set; configurable column order; name and color per status; existing 5 statuses seeded as defaults |
| Differentiator | is_terminal flag drives KPI completion logic; is_blocked flag for MTTR distinction |
| Anti-feature | Per-member status sets; more than 10 columns (soft cap); delete status with tasks (block delete, require reassign first) |

### Task Types

| Category | Feature |
|----------|---------|
| Table stakes | task_type field (feature/bug/task/improvement) default task; visible on task cards; filterable; required on creation |
| Differentiator | AI task input pre-classifies type using existing NLP (low-effort prompt extension) |
| Anti-feature | User-defined types (breaks metric comparability); mandatory type change on status transition |

### Advanced KPIs

| Category | Feature |
|----------|---------|
| Table stakes | Velocity per sprint (task count or story points); sprint burndown chart; cycle time by task type; throughput per member; defect metrics; MTTR |
| Differentiator | Velocity trend across sprints (simple once per-sprint velocity works) |
| Anti-feature | Per-member burndown; ML-based predictive completion; real-time WebSocket refresh (5-min poll is sufficient) |

### Sprint/Release Reminders

| Category | Feature |
|----------|---------|
| Table stakes | In-app notification for sprint end (24-48h before); milestone release date reminder; supervisor and members receive reminders; reminders dismissible |
| Differentiator | Configurable reminder offset; auto-creation when sprint is activated |
| Anti-feature | Email notifications (out of scope per PROJECT.md); push/browser notifications; reminder on every status transition |

### Defer to v3+

- Per-project Kanban status override (team-wide default covers 90% of teams)
- Defect escape rate (requires knowing when a bug was filed vs when its sprint closed)
- Daily snapshot table for burndown historical accuracy (on-the-fly computation sufficient for v2)

---

## Architecture Decisions

**1. SubTeam not Team.** The app is a single-org deployment. An Organization wrapper model adds a join with zero value. The correct model is SubTeam with the org being the implicit app instance.

**2. Dual-write for status migration.** Retain tasks.status alongside new tasks.custom_status_id for the entire feature-build period. All new code writes both; all new read paths use custom_status_id. Drop the old column only in a deferred cleanup phase after KPI queries are verified.

**3. is_terminal replaces hardcoded done check.** The update_task endpoint currently sets completed_at when status == TaskStatus.done. After the enum migration, this logic must use custom_status.is_terminal == true. Cache terminal slugs at startup to avoid a per-update DB lookup.

**4. Sprint reminders via existing EventNotification table.** Do not add APScheduler run_date jobs — they are lost on process restart. Insert EventNotification rows when a sprint is activated; the existing 60s poll job delivers them. Add a (event_type, event_ref_id, user_id) unique constraint to prevent duplicates.

**5. Migration sequence as a pre-work artifact.** The migration chain has FK ordering constraints. The full sequence must be documented before any migration file is written. Also: ALTER TYPE ADD VALUE must run outside a Postgres transaction — set transaction_per_migration = False in Alembic env for that migration.

**6. KPI queries: single GROUP BY, no N+1.** All KPI aggregations must be written as single GROUP BY queries. The existing N+1 in timeline.py (unassigned_stmt inside a project loop) should be fixed in the hierarchy phase.

### New API Routers

| File | Prefix | Auth |
|------|--------|------|
| routers/sub_teams.py | /api/sub-teams | CRUD: supervisor/admin; reads: any authenticated |
| routers/sprints.py | /api/sprints | CRUD: supervisor/admin; reads: any authenticated |
| routers/task_statuses.py | /api/task-statuses | CRUD: supervisor/admin; reads: any authenticated |
| routers/kpi.py | /api/kpi | All endpoints: supervisor/admin only |

### New Frontend Routes and Stores

| Path | Purpose |
|------|---------|
| /sprints | Sprint management (create, list, close, view tasks) |
| /kpi | KPI analytics dashboard with tab bar per metric |
| stores/statuses.ts | Shared writable store; consumed by KanbanBoard, AgileView, filter dropdowns |

### Modified Components (Non-Trivial Changes)

- KanbanBoard.svelte: columns array currently hardcoded to 5 values; must accept a statuses prop and derive columns from it
- AgileView.svelte: statusCycle and progressFor() both hardcoded; must use statuses prop with is_terminal flag
- performance.py: all is-done joins must switch from TaskStatus.done enum comparison to KanbanStatus.is_terminal join; seven query files must be audited when team hierarchy lands

---

## Watch Out For

Priority order — address each pitfall in the phase where it is introduced.

1. **Unscoped queries after hierarchy is added.** After adding sub_team_id to users and team_id to projects, every existing select(Task) and select(Project) call must gain team-scoping predicates. Seven files to audit: tasks.py, projects.py, milestones.py, timeline.py, performance.py, dashboard.py, ai.py. Prevention: integration test (Supervisor-A queries Team-B project, assert 403/404) as a completion gate for the hierarchy phase.

2. **Postgres enum drop sequence.** DROP TYPE taskstatus fails if the tasks.status column still references it. The migration must be a multi-step sequence written as explicit op.execute() calls: add VARCHAR column, backfill, drop old column, drop type — in that order. Do not rely on alembic autogenerate for this step.

3. **Alembic migration ordering.** The full migration sequence has FK ordering constraints. Draft the complete sequence before writing any migration file. ALTER TYPE ADD VALUE must run outside a Postgres transaction.

4. **completed_at not set for custom terminal statuses.** The update_task endpoint checks if new_status == TaskStatus.done to set completed_at. After the enum migration, this must use is_terminal from the status row. If missed, all tasks completed via custom terminal statuses have completed_at = NULL, corrupting every KPI metric. Prevention: test that transitions a task to a custom terminal status and asserts completed_at is set.

5. **Sprint reminders lost on process restart.** APScheduler run_date jobs are in-memory and lost on every Azure deploy or recycle. Store sprint-end reminders as EventNotification rows; the existing 60s poll job delivers them. Add a (event_type, event_ref_id, user_id) unique constraint to prevent duplicates.

---

## Recommended Build Order

Dependencies flow downward — each phase requires the phases above it to be merged.

### Phase 1: Alembic Baseline + Migration Sequence Plan
**Rationale:** Every subsequent phase produces a migration. Without Alembic initialized and the full migration sequence documented, later phases risk out-of-order FK violations.
**Delivers:** Alembic initialized with baseline revision; full Milestone 2 migration sequence documented as a numbered list; alembic upgrade head passing in CI.
**Pitfall addressed:** Alembic migration chain ordering.

### Phase 2: Multi-Team Hierarchy
**Rationale:** Team scoping gates everything downstream — sprint visibility, KPI filtering, and sprint reminder fanout all require sub_team_id on User and team_id on Project.
**Delivers:** SubTeam model and migration; sub_team_id on User; team_id on Project; /api/sub-teams router; /team page sub-team panel; all seven query files audited and team-scoped; timeline visibility enforcement (members see assigned projects only; supervisors see team-wide) added in this phase, not deferred.
**Pitfall addressed:** Unscoped data leakage; timeline visibility enforcement.

### Phase 3: Task Types
**Rationale:** Fully isolated — a single column addition with no breaking changes. Shipping it early means KPI queries can be designed correctly from the start. Can run in parallel with Phase 2.
**Delivers:** task_type VARCHAR NOT NULL DEFAULT task on Task; migration with backfill; type badge on task cards; task_type filter on GET /api/tasks/; AI prompt updated to output task_type.
**Pitfall addressed:** Backfill strategy — existing tasks default to task; KPI dashboard documents the historical gap.

### Phase 4: Sprint Model
**Rationale:** Requires team hierarchy (Phase 2) for scoping. Sprint rows must exist before tasks.sprint_id FK can be added. Sprint close logic must be in this phase to prevent retroactive task reassignment that would corrupt burndown.
**Delivers:** Sprint model and migration; sprint_id (nullable) + story_points (nullable) on Task; Sprint.committed_points snapshot field; /api/sprints router; /sprints page; SprintCard and SprintSelector components; sprint close endpoint that prevents adding tasks to completed sprints.
**Pitfall addressed:** Orphaned tasks on sprint end; APScheduler job loss — reminders stored as EventNotification rows.

### Phase 5: Custom Kanban Statuses
**Rationale:** The riskiest migration of the milestone. Placed after Sprint so the burndown query can be written correctly against is_terminal from day one. The dual-write approach retains the old tasks.status column — it is not dropped here.
**Delivers:** CustomTaskStatus model and migration (Phase A — add custom_status_id, seed 5 defaults, backfill); /api/task-statuses router; statuses store; KanbanBoard.svelte and AgileView.svelte updated to dynamic statuses prop; is_terminal logic replacing hardcoded done check in update_task; buildStatusMaps() utility.
**Pitfall addressed:** Enum migration multi-step; completed_at not set for custom terminal statuses.

### Phase 6: Advanced KPIs
**Rationale:** Can only be completed once phases 2-5 are done. All six metrics require sprint_id, task_type, and is_terminal to be meaningful.
**Delivers:** /api/kpi router with six endpoints (velocity, burndown, cycle time, throughput, defect rate, MTTR); /kpi page with tab bar; BurndownChart.svelte and VelocityBar.svelte; all KPI queries as single GROUP BY queries; existing N+1 in timeline.py fixed; performance.py updated to join on is_terminal; layerchart version verified at phase kickoff.
**Pitfall addressed:** N+1 queries on analytics endpoints.

### Phase 7: Sprint Reminders
**Rationale:** Dependencies are only on Phases 2 and 4. Can be developed in parallel with Phase 6. Placed last to avoid splitting attention during the most complex phase.
**Delivers:** ALTER TYPE notificationeventtype ADD VALUE sprint migration; auto-creation of EventNotification rows on sprint activation; deduplication via unique constraint on (event_type, event_ref_id, user_id); stale reminder handling when sprint end_date changes; milestone release reminders using same pattern.
**Pitfall addressed:** APScheduler job loss on restart resolved via EventNotification row approach.

### Phase 8: Enum Drop Cleanup (Phase B Migration)
**Rationale:** The tasks.status Postgres enum column is retained through phases 2-7. Once KPI queries are verified against custom_status_id and is_terminal, the old column is safe to drop.
**Delivers:** Alembic migration: ALTER TABLE tasks DROP COLUMN status + DROP TYPE taskstatus; removal of all dual-write logic from tasks.py.

### Phase Ordering Rationale

- Alembic baseline is a prerequisite for every other phase
- Team hierarchy gates all scoping and must land before sprint or KPI work
- Task types are isolated and could run in parallel with Phase 2; placed at Phase 3 to keep the sequence linear
- Sprints before custom statuses so burndown is written once against the correct is_terminal semantics
- Custom statuses before KPIs so all is-done logic is correct from day one of KPI development
- Reminders can close in parallel with KPIs; placed after to avoid splitting attention
- Enum drop is deferred cleanup after full QA

---

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | Verified against actual package.json and requirements.txt; no new packages required |
| Features | HIGH | Grounded in existing codebase + established patterns for 5-15 person dev teams |
| Architecture | HIGH | All model, router, and component recommendations derived from reading the actual source files |
| Pitfalls | HIGH | All risks identified from reading existing code paths that will be affected |
| layerchart v2 Svelte 5 compatibility | MEDIUM | Installed as next tag; code comments suggest it was tried and bypassed; verify at Phase 6 kickoff |

**Overall confidence: HIGH**

### Gaps to Address

- **story_points vs estimated_hours for burndown Y-axis.** Research recommends a separate nullable story_points integer column. The burndown implementation must decide on fallback behavior when story_points is null (fall back to task count) and the UI must label which unit is in use. Decide at Phase 4 kickoff.
- **Per-project Kanban status override.** Research recommends deferring (team-wide default covers 90%). Confirm with actual users before Phase 5 scope is locked.
- **Burndown on-the-fly vs snapshot.** On-the-fly computation is sufficient for v2 if the sprint close flow enforces no retroactive task reassignment. Flag for review after the first real sprint closes.

---

## Sources

### Primary (HIGH confidence — direct codebase inspection)

- backend/app/models.py — existing schema, enum types, relationships
- backend/app/routers/tasks.py — existing task CRUD, status transition logic, AI parse prompt
- backend/app/routers/performance.py — existing KPI queries, N+1 patterns
- backend/app/routers/timeline.py — existing unscoped project queries
- backend/app/scheduler_jobs.py — existing APScheduler setup, EventNotification poll loop
- frontend/src/lib/components/tasks/KanbanBoard.svelte — hardcoded columns and DnD logic
- frontend/src/lib/components/tasks/AgileView.svelte — hardcoded statusCycle, progressFor()
- frontend/src/lib/utils.ts — hardcoded statusLabels, statusColors
- frontend/package.json — confirmed layerchart, svelte-dnd-action, d3-shape present
- backend/requirements.txt — confirmed apscheduler, sqlalchemy, alembic present
- .planning/PROJECT.md — feature requirements and constraints
- .planning/codebase/ARCHITECTURE.md — existing architecture patterns

### Secondary (MEDIUM confidence — established ecosystem patterns)

- Jira/Linear/Trello feature conventions for 5-15 person dev teams
- PostgreSQL enum migration patterns (ALTER TYPE constraints, DROP TYPE dependency ordering)
- APScheduler in-memory vs persistent job store behavior on managed hosting

---
*Research completed: 2026-04-24*
*Ready for roadmap: yes*
