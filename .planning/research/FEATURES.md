# Feature Landscape: TeamFlow v2.0

**Domain:** Multi-team task management with sprint-driven project management and analytics
**Researched:** 2026-04-24
**Confidence:** HIGH — analysis grounded in existing codebase (models.py, performance.py, scheduler_jobs.py, AgileView.svelte) plus well-established patterns from Jira/Linear/Trello/Asana ecosystems

---

## 1. Multi-Team Hierarchy

### Table Stakes

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Organization → sub-teams model | Users expect a clear container for their team; admin needs cross-team visibility | Medium | Requires new `Team` model and FK on `User` |
| 1 supervisor per sub-team | Standard management model — one accountable person per team | Low | `Team.supervisor_id` FK to `users` |
| Admin sees all teams/projects | Admin is already defined; cross-team read access is expected for that role | Low | Filter queries by `team_id` only for members/supervisors |
| Members see only their team's projects | Privacy / focus — Jira/Linear both scope project visibility to team membership | Medium | All project queries must join through team membership |
| Supervisor sees only their own team | Scoped management; supervisors should not see sibling teams' data | Low | Filter by `team.supervisor_id = current_user.id` |

### Differentiators

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| Supervisor can see their team's performance vs org-level aggregate | Comparative context — "Am I above or below org average?" | Medium | Requires org-level rollup query in performance endpoint |

### Anti-Features

| Anti-Feature | Why Avoid | What to Do Instead |
|--------------|-----------|-------------------|
| Members can belong to multiple teams | Out of scope for 5–15 person private deployment; adds RBAC complexity massively | Single team membership per user; reassign via admin |
| Team-level chat channels auto-created per team | Unpredictable behavior; teams manage their own channels | Let supervisors create channels manually |
| Nested sub-team hierarchy (teams of teams) | Overkill for a 5–15 person tool; creates recursive query complexity | Two levels only: Org → Team |

### Edge Cases

- **Removing a user from a team:** Tasks assigned to that user in team projects remain assigned. Do not cascade-delete or re-assign automatically. Surface orphaned assignments on the admin dashboard.
- **Supervisor reassignment:** When a team's supervisor changes, the old supervisor loses access to the team's `/performance` view. Existing performance history should remain readable by the new supervisor and admin.
- **Project ownership across teams:** The current `Project` model has no `team_id`. Adding one means existing projects are "teamless" — migration must assign them to a default team or handle null gracefully.
- **Admin creates project for a team:** Admin must specify which team the project belongs to. A project scoped to Team A should not appear in Team B's board.

### Dependencies

- Requires `Team` model (new): `id`, `name`, `supervisor_id`, `created_at`
- Requires `team_id` FK on `Project` (existing model, migration needed)
- Requires `team_id` FK on `User` (existing model, migration needed)
- All query filters for tasks/projects/milestones must be team-scoped downstream
- RBAC enforcement (Phase 2, already built) must be extended: supervisor role check must now also verify `team.supervisor_id = current_user.id`

---

## 2. Sprint Model

### Table Stakes

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Sprint has start date, end date, name | Core sprint identity; calendar-gating depends on dates | Low | New `Sprint` model |
| Sprints belong to a milestone | Milestones already exist and have due dates; sprints are iterations toward a milestone | Low | `Sprint.milestone_id` FK |
| Tasks can be assigned to a sprint | The primary purpose of a sprint is to scope work for a time-box | Low | `task.sprint_id` FK (nullable — unassigned tasks exist) |
| Sprint has a status: planned / active / completed | Needed for filtering active sprint board, closing out sprints | Low | Enum on `Sprint` |
| Only one sprint active per milestone at a time | Standard scrum rule — prevents confusion about which board to use | Medium | Enforce at API layer: reject `status=active` if another sprint in milestone is already active |
| Backlog concept: tasks with no sprint assigned | Tasks without `sprint_id` are implicitly "backlog"; must be visually distinct | Low | Filter `sprint_id IS NULL` for backlog view |
| Move tasks between sprints | Sprints are re-planned; tasks get reassigned during sprint planning | Low | PATCH `task.sprint_id` |

### Differentiators

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| Sprint closure: auto-move incomplete tasks to next sprint or backlog | Saves manual re-assignment at sprint end | Medium | Needs a "close sprint" action endpoint, not automatic — let supervisor decide |
| Sprint planning view: drag tasks from backlog into sprint | Reduces friction at sprint kickoff | Medium | Kanban-style drag between backlog column and sprint column |

### Anti-Features

| Anti-Feature | Why Avoid | What to Do Instead |
|--------------|-----------|-------------------|
| Automatic sprint creation on a schedule | Unpredictable; teams plan at different cadences | Let supervisor create sprints manually |
| Locking tasks once a sprint is active (no changes allowed) | Too rigid for a small team; adds UX friction | Allow edits; rely on burndown to surface scope creep |
| Sub-tasks / task hierarchy | Not in scope for this milestone; multiplies complexity | Use task descriptions or checklist fields instead |

### Edge Cases

- **Sprint with no tasks:** Valid — a sprint can be created and then planned. Do not hide it.
- **Task due date vs sprint end date conflict:** A task's `due_date` may fall after the sprint ends. Surface as a warning, not a block.
- **Milestone with no sprints:** Must still work — tasks can belong to a milestone without a sprint. The existing `AgileView` groups by milestone and must remain functional.
- **Completing a sprint while tasks are in-progress:** Allow it. Record `sprint.completed_at`. Incomplete tasks remain with their sprint (for historical burndown accuracy) until explicitly moved.
- **Reopening a completed sprint:** Disallow. Force creation of a new sprint instead.

### Dependencies

- Requires new `Sprint` model: `id`, `name`, `milestone_id`, `start_date`, `end_date`, `status`, `completed_at`, `created_at`
- Requires `sprint_id` FK (nullable) on `Task` (migration needed)
- KPIs (Feature 5) depend entirely on this model: velocity, burndown, and throughput are all sprint-scoped
- Story points (Feature 5 dependency) — `Task.estimated_hours` exists but burndown typically uses `story_points`. Decision required: **reuse `estimated_hours` as the point unit, or add a separate `story_points` integer column.** Recommendation: add `story_points` (nullable integer). Keep `estimated_hours` as-is since it already drives the AI breakdown feature.

---

## 3. Custom Kanban Statuses

### Table Stakes

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Supervisor/admin can define a team-wide default status set | Trello-style boards are table stakes; fixed enums feel rigid to power users | Medium | New `KanbanStatus` model per team |
| Per-project override of status set | Some projects need different workflows (e.g., QA-heavy vs quick-turnaround) | Medium | `ProjectKanbanStatus` override table, falls back to team default if empty |
| Column order is configurable | Drag-and-drop column order is expected in any Kanban tool | Medium | `position` integer on status; drag updates order |
| Status has a name and color | Visual differentiation between columns | Low | `name: String`, `color: String` on status model |
| Existing default statuses remain as the initial team defaults | Migration path — current `todo/in_progress/review/done/blocked` should seed the team's default set | Low | Seed migration or first-run logic |

### Differentiators

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| "Done" flag on a status (marks task as completed) | Needed for KPI computation — completed_at must be set when task enters a "done-type" status | Medium | Boolean `is_done` on status; triggers `completed_at` update |
| "Blocked" flag on a status | Allows MTTR / defect metrics to distinguish blocked from in-progress | Low | Boolean `is_blocked` on status |

### Anti-Features

| Anti-Feature | Why Avoid | What to Do Instead |
|--------------|-----------|-------------------|
| Per-member status sets | Individual status sets destroy team-wide visibility and reporting | Team or project scope only |
| Unlimited status count | More than 8–10 columns becomes unusable on any screen | Soft cap at 10 with a UI warning |
| Deleting a status that has tasks in it | Creates orphaned tasks with invalid status | Block delete; require reassign first, or move tasks to another status before deletion |

### Edge Cases

- **Hardcoded `TaskStatus` enum:** The existing `TaskStatus` SQLAlchemy enum (`todo/in_progress/review/done/blocked`) is a Postgres ENUM type. Custom statuses cannot use the same column without a schema change. The cleanest approach is: keep the enum for the system defaults; for custom statuses, store `status` as a `String` FK to a `kanban_statuses` table. This is a significant migration concern.
  - **Alternative (simpler):** Store `task.custom_status_id` (nullable FK to `kanban_statuses`) alongside the existing `task.status` enum. When `custom_status_id` is set, the board uses it; otherwise falls back to the enum. This avoids altering the Postgres enum but adds nullable logic.
  - **Recommendation:** Replace `task.status` with a `String` column (not enum), validated at the application layer against allowed statuses. Drop the Postgres enum. One migration, cleaner long-term.
- **Project inherits team statuses, then team statuses change:** Projects with no override see the updated team set immediately. This is the expected behavior (inheritance).
- **Drag reorder during active use:** Column reorder by one user while another is looking at the board — position changes should be reflected on next board load (no real-time sync required).
- **KPI calculations rely on "done" semantics:** Once status is a string, cycle time and throughput queries must join `kanban_statuses` to find `is_done = true` statuses rather than comparing to the `TaskStatus.done` enum value. All existing performance queries in `performance.py` must be updated.

### Dependencies

- New `KanbanStatus` model: `id`, `team_id`, `project_id` (nullable — null means team default), `name`, `color`, `position`, `is_done`, `is_blocked`, `created_by`
- `Task.status` must change from `Enum(TaskStatus)` to `String` (Alembic migration required — dropping a Postgres enum type is non-trivial: requires `ALTER COLUMN`, then `DROP TYPE`)
- Requires schema migration seeding existing task statuses into the new `kanban_statuses` table
- All performance queries in `performance.py` must join on `KanbanStatus.is_done` instead of `TaskStatus.done`
- `AgileView.svelte` hardcodes `statusCycle` dict and `statusColors/statusLabels` — these must be driven by API data

---

## 4. Task Types

### Table Stakes

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| `task_type` field with values: feature / bug / task / improvement | Standard triage field in any project management tool | Low | Add `task_type` enum/string column to `Task` |
| Visible on task cards (Kanban, AgileView, list) | Engineers scan cards and need type at a glance | Low | Icon or colored badge per type |
| Filterable on board and list views | "Show me only bugs" is a daily workflow | Low | Query param on `GET /api/tasks` |
| Required on task creation (or defaulting to "task") | Without a default, data quality degrades immediately | Low | Default to `"task"`; allow update |

### Differentiators

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| AI task input pre-classifies type | NLP already identifies task intent; extending it to classify type reduces manual overhead | Low | Add type to AI prompt output; existing `estimated_hours` already comes from AI |

### Anti-Features

| Anti-Feature | Why Avoid | What to Do Instead |
|--------------|-----------|-------------------|
| User-defined task types | Types are the axis for KPI breakdowns — custom types break metric comparability across sprints | Fixed four values only |
| Mandatory type change on status transition | Adds friction with no benefit for a small team | Keep type independent of status |

### Edge Cases

- **Existing tasks have no type:** Migration must set a default. Set all existing tasks to `"task"` (the most generic type).
- **AI-classified type is wrong:** Users must be able to change type freely with no side effects other than KPI recalculation going forward.
- **Bug type and defect metrics:** If a task typed "bug" is closed, it contributes to defect metrics. If its type is later changed to "task", it should no longer count as a resolved bug. Metrics are computed at query time from current `task_type`, not cached — this is the expected behavior.

### Dependencies

- Requires `task_type` column on `Task` (new, non-nullable with default `"task"`)
- KPI feature (Feature 5) depends on this: cycle time breakdown by type, throughput breakdown by type, and defect/MTTR metrics all require `task_type`
- AI task input (already built) needs prompt update to output `task_type`
- Filtering in `GET /api/tasks` needs `task_type` as an optional query param

---

## 5. Advanced KPIs on Performance Dashboard

### Table Stakes

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Velocity per sprint (task count or story points) | Core scrum metric; teams use it for planning future sprints | Medium | Sum of `story_points` (or task count) for tasks with `is_done` status in a closed sprint |
| Sprint burndown chart | Expected whenever sprints exist; shows scope control and progress | High | Requires daily snapshot OR computed from `completed_at` timestamps within sprint date range |
| Cycle time broken down by task type | Extension of existing cycle time metric (already computed in `performance.py`) | Medium | Group `avg(completed_at - created_at)` by `task_type` |
| Throughput per member per period | Extension of existing `completed_30d` metric; add `task_type` breakdown | Medium | `COUNT tasks WHERE is_done AND assignee=X GROUP BY task_type, period` |
| Defect metrics: bugs reported vs resolved | Required for any team that tracks quality | Medium | `COUNT WHERE task_type='bug'` split by open vs closed |
| MTTR (mean time to repair) | Expected for bug-tracking; measures responsiveness | Medium | `AVG(completed_at - created_at) WHERE task_type='bug' AND is_done` |

### Differentiators

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| Velocity trend across sprints | Planning improves when teams can see whether velocity is increasing or unstable | Low | Sprint velocity is already computable once burndown exists; trend is just multiple sprints' velocity |
| Defect escape rate (bugs found in done sprints) | Measures QA quality; surfaces post-release bugs | High | Requires knowing when a bug was created vs when its associated sprint closed — complex |

### Anti-Features

| Anti-Feature | Why Avoid | What to Do Instead |
|--------------|-----------|-------------------|
| Individual member burndown | Creates surveillance anxiety for small teams; cycle time and throughput per member are sufficient | Keep burndown at sprint level only |
| Predictive sprint completion (ML-based) | Requires historical data depth this tool won't have initially; false precision | Show trend line from actual data |
| Real-time dashboard refresh (WebSocket) | Performance queries are expensive aggregates; polling every 5 min or on-demand is sufficient | Manual refresh button + 5-min poll |

### Edge Cases

**Burndown specifics:**

- Burndown requires knowing the sprint's total committed scope at the start. If story_points are added mid-sprint ("scope creep"), the burndown starting point becomes ambiguous.
  - **Recommendation:** Record `sprint.committed_points` at sprint start (snapshot when status changes from `planned` to `active`). Use this as the Y-axis start. Show scope creep as a separate indicator.
- Burndown is computed from `completed_at` timestamps within the sprint date range — no separate daily-snapshot table needed. Query: for each day D in `[sprint.start_date, sprint.end_date]`, sum `story_points` of tasks where `completed_at <= D AND sprint_id = X AND is_done`.
- If `story_points` is null on a task, fall back to counting tasks (count = 1 per task). Both modes should be supported; the burndown chart should label which unit is in use.

**Velocity specifics:**

- Velocity is only meaningful for **completed** sprints. Active and planned sprints show no velocity (or "in progress" label).
- If a sprint is closed with incomplete tasks left in it (not moved to backlog), count only the `is_done` tasks toward velocity.

**MTTR specifics:**

- MTTR = `avg(completed_at - created_at)` for bug-type tasks in the time window. This is directly computable from existing fields once `task_type` exists.
- Bugs that are still open contribute to "unresolved" count but not MTTR (do not include in average).

**Cycle time by type specifics:**

- The existing `performance.py` computes a global avg cycle time. Extending it to break down by `task_type` is a `GROUP BY task_type` addition — low risk.
- Requires joining `KanbanStatus.is_done` (see Feature 3) instead of hardcoded `TaskStatus.done`.

### Dependencies

- Sprint model (Feature 2): velocity and burndown require sprint dates and `sprint_id` on tasks
- Task types (Feature 4): cycle time by type, throughput by type, defect metrics, MTTR all require `task_type`
- Custom statuses (Feature 3): all "is this task done?" logic must use `KanbanStatus.is_done` join
- `story_points` integer column on `Task` (nullable): needed for point-based velocity and burndown. `estimated_hours` is insufficient because hours are not story points semantically.
- `Sprint.committed_points` integer (nullable): snapshot at sprint activation for burndown Y-axis
- Existing `performance.py` must be extended (not replaced) — existing metrics (cycle time, on-time rate, active tasks) remain; new metrics are additive

---

## 6. Sprint and Release Reminders

### Table Stakes

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| In-app notification when a sprint end date is approaching | Teams forget sprint endings; a reminder 24–48h before prevents surprises | Low | Extend existing `EventNotification` / scheduler pattern |
| In-app notification when a milestone release date is approaching | Milestones already have `due_date`; reminder is the same pattern as task reminders | Low | Add `sprint` and `milestone` values to `NotificationEventType` enum |
| Supervisor and admin receive sprint-end reminders | They are responsible for sprint closure and retrospective | Low | Create notification for supervisor of the team |
| Members receive sprint-end reminder | Awareness of deadline drives last-mile task completion | Low | Fanout: create one notification per team member |
| Reminders are dismissible | Users expect bell-icon notifications they can clear | Already built | `dismiss` endpoint already exists |

### Differentiators

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| Configurable reminder offset (e.g., 24h vs 48h vs 1h before sprint end) | Teams work differently; some want day-before, others hour-before | Low | `offset_minutes` already exists on `EventNotification`; reuse the pattern |
| Automatic reminder creation when a sprint is activated | Removes the need for supervisor to manually set reminders | Medium | On `PATCH /sprints/{id}` with `status=active`, auto-create `EventNotification` rows for all team members |

### Anti-Features

| Anti-Feature | Why Avoid | What to Do Instead |
|--------------|-----------|-------------------|
| Email notifications | Explicitly out of scope in PROJECT.md | In-app only |
| Push notifications (browser/mobile) | Complexity not warranted for an internal tool; adds service worker + VAPID key setup | In-app bell notification only |
| Reminder for every status transition | Notification spam kills adoption immediately | Only sprint end and milestone release dates |

### Edge Cases

- **Sprint end date changes after reminders are created:** The existing `EventNotification` stores `start_at_cache` and `remind_at` at creation time. If the sprint end date is updated, existing notifications become stale. Solution: on sprint date update, delete and recreate the notifications (same pattern as `POST /notifications/bulk`).
- **Sprint end date is in the past when sprint is activated:** Scheduler would immediately flip notification to `sent`. This is acceptable — it surfaces the issue visually. Optionally warn the supervisor at activation time.
- **Multiple reminders for the same sprint:** If supervisor activates, deactivates, and reactivates a sprint, duplicate notifications would be created. Use the bulk-replace pattern (delete existing sprint notifications before creating new ones).
- **`NotificationEventType` enum:** Currently only `schedule` and `task` values exist (Postgres enum in `event_notifications` table). Adding `sprint` and `milestone` requires an `ALTER TYPE ... ADD VALUE` Alembic migration on the Postgres enum. This is non-destructive but must be ordered before any notification creation for those types.
- **Who receives sprint reminders:** The supervisor's team members are determined by the new `Team` membership (Feature 1). This feature has a hard dependency on multi-team hierarchy being complete first.

### Dependencies

- Sprint model (Feature 2): sprint `end_date` and `id` needed for notification creation
- Multi-team hierarchy (Feature 1): team membership determines who receives sprint-end fanout notifications
- `NotificationEventType` enum must be extended (Alembic `ALTER TYPE` migration)
- Scheduler job (`scheduler_jobs.py`) already handles the `pending → sent` transition — no changes needed there
- Auto-creation of reminders on sprint activation is triggered from the sprint PATCH endpoint, not the scheduler

---

## Feature Dependency Map

```
Task Types (4)
    └── feeds KPIs: cycle time by type, throughput by type, defect metrics, MTTR (5)

Sprint Model (2)
    └── requires: story_points on Task (new field)
    └── feeds KPIs: velocity, burndown (5)
    └── feeds: sprint reminders (6)

Multi-Team Hierarchy (1)
    └── gates: sprint reminders fanout (6)
    └── gates: all project/task visibility scoping

Custom Kanban Statuses (3)
    └── requires: Task.status from enum → string (migration)
    └── feeds KPIs: all "is done?" logic (5)
    └── blocks: burndown and throughput queries until is_done semantics are in place

KPIs (5) depends on: 1 + 2 + 3 + 4 all being complete
Sprint Reminders (6) depends on: 1 + 2 being complete
```

**Recommended build order:**
1. Task types — isolated, zero breaking changes, unblocks KPI enrichment immediately
2. Multi-team hierarchy — foundational; gates visibility and sprint reminders
3. Sprint model — requires team hierarchy for scoping; story_points field added here
4. Custom Kanban statuses — the riskiest migration (enum → string); do after sprint model so burndown queries can be written correctly from the start
5. Advanced KPIs — can only be completed once 1–4 are done
6. Sprint reminders — can be completed once 1 and 2 are done (does not require custom statuses or KPIs)

---

## MVP Recommendation for a 5–15 Person Dev Team

**Build all six features** — for a dev team, sprints, task types, and burndown are daily-use features, not nice-to-haves.

**Prioritize correctness on these edge cases specifically:**
- Custom status migration (enum → string) done once, done right, with seeded defaults
- Sprint burndown fallback to task count when `story_points` is null
- Sprint reminder auto-creation on activation with deduplication

**Defer these until validated by real use:**
- Defect escape rate (complex, low daily value until the team has shipping cadence)
- Per-project Kanban status override (team-wide default covers 90% of teams; add override only if requested)
- Velocity trend visualization (simple to add after velocity per sprint works)
