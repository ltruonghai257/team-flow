# Feature Landscape: TeamFlow v2.0 + v2.2

**Domain:** Multi-team task management with sprint-driven project management, analytics, standup flows, knowledge sharing, and team communication boards
**Researched:** 2026-04-28 (v2.2 sections added)
**Confidence:** HIGH for standup and weekly board patterns (well-established in Geekbot, Standuply, Range, Notion, Confluence); MEDIUM for knowledge sharing scheduler patterns (less standardized across tools)

---

<!-- ====================================================================== -->
<!-- v2.0 FEATURES (existing — do not re-implement)                         -->
<!-- ====================================================================== -->

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

<!-- ====================================================================== -->
<!-- v2.2 FEATURES (new — Milestone 2.2)                                    -->
<!-- ====================================================================== -->

## 7. Member Standup / Daily Updates

**Context:** Tools like Geekbot, Standuply, Range, and Status Hero have standardized this space. The model below reflects what teams expect from a standup feature embedded in a task management app rather than a standalone bot.

**Confidence:** HIGH — based on well-established standup tool patterns documented through training cutoff.

### Table Stakes

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Three-field freeform post: "What I did", "What I'm working on", "Blockers" | This is the canonical standup format (Scrum daily standup). Teams arriving from any other tool know this structure immediately. | Low | Three text fields, all optional in practice but prompted |
| Automatic task status snapshot attached to each post | The reason to embed standups in a task tool is this link — post should show the member's tasks and their current statuses at post time, no manual copy/paste | Medium | Snapshot = array of `{task_id, title, status}` captured at submit time; stored as JSON or a related table |
| Visible to all team members | Standups are a team-visibility mechanism by definition; hiding them from teammates defeats the purpose | Low | Query filters by `team_id`; all team members and supervisor can read |
| Visible to supervisor | Supervisor uses the feed for asynchronous stand-up review | Low | Already covered by team visibility; supervisor RBAC reads all |
| Post timestamp and author shown | Without author + time, the feed is unreadable | Low | `created_at`, `author_id` FK to users |
| Team feed: most recent post per member, reverse-chronological | Range and Geekbot both default to "latest update per person" — teams scan who has posted today | Low | Query: latest post per `author_id` within a date window |
| Historical posts accessible | Teams review yesterday's blockers, supervisors audit | Low | Paginated list endpoint with date-range filter |
| Post frequency is freeform (daily or weekly) | Forcing a daily cadence creates compliance anxiety; let members decide | Low | No scheduling enforcement; `post_type` field: `daily` or `weekly` for display label |

### Differentiators

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| Post includes only the member's own tasks (filtered snapshot) | In a 5–15 person team spanning multiple projects, members want their slice, not every project's tasks | Low | Snapshot queries `tasks WHERE assignee_id = current_user.id` at post time |
| Blocked tasks highlighted in the post UI | Blockers field is text, but the snapshot can flag tasks currently in `blocked` status visually without the member needing to retype | Low | In frontend render: highlight snapshot entries where `status == blocked` |
| Supervisor sees the full team feed grouped by member | Geekbot's "digest" view — not one long stream, but one card per member with their latest update | Medium | Group-by-member layout in frontend; one API call, client-side grouping |
| In-app notification to supervisor when a post contains a blocker | Passive visibility fails when blockers get buried; a notification surfaces them | Medium | On post submit: if `blockers` field is non-empty or snapshot has blocked tasks, create a notification for the supervisor |

### Anti-Features

| Anti-Feature | Why Avoid | What to Do Instead |
|--------------|-----------|-------------------|
| Scheduled bot reminder ("It's standup time!") | Adds scheduler complexity, notification fatigue, and is the primary reason teams disable Geekbot bots; in-app tools don't need this | Members post when they're ready; no scheduled prompts |
| Mandatory post before accessing the app | Hard gate is hostile UX; kills adoption in the first week | Post is opt-in; the feed simply shows who has posted |
| Editing a submitted post | Range allows edits; this adds versioning complexity and undermines the "snapshot in time" integrity of the task status snapshot | Posts are immutable once submitted; correct by posting a new one |
| Per-question commenting / reactions | Turns standup into a chat thread; the existing WebSocket chat already handles discussion | Link from a standup post to the relevant chat channel for follow-up |
| Video/audio standup | Out of scope for a browser-based internal tool | Text only |
| Multiple posts per day shown equally | Two posts on the same day from the same person creates confusion in the feed | Display latest post per member per day as "today's update"; older same-day posts collapsed |

### Complexity Notes

- Backend: new `StandupPost` table + task snapshot (JSON column or related table). `POST /api/standups`, `GET /api/standups` with filters. Medium complexity.
- Frontend: post form (3 fields + task list preview) + team feed page. Medium complexity.
- Key integration: task snapshot requires reading current user's tasks at submit time — this is a read-only query against the existing task system, no schema changes to tasks.

### Dependencies on Existing Features

- Task model (existing): snapshot queries `tasks WHERE assignee_id = current_user.id`
- User/RBAC (existing): post visibility scoped by team, supervisor role can read all
- Notification system (existing): optional blocker alert reuses the existing notification pattern

---

## 8. Knowledge Sharing Scheduler

**Context:** Knowledge sharing session scheduling is less standardized than standups. The closest reference tools are calendar-embedded event types (Google Calendar, Outlook), learning management integrations (Confluence's "Learning" space), and engineering team practices (team tech talks). This feature is a lightweight specialized event type layered on top of the existing calendar.

**Confidence:** MEDIUM — knowledge sharing schedulers are domain-specific; patterns inferred from calendar tool conventions and LMS-lite features.

### Table Stakes

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Session fields: topic, description, presenter, session type, duration, tags | These are the minimum fields to describe a knowledge session meaningfully. Topic and presenter are required; others optional. | Low | New `KnowledgeSession` model; session types: `presentation`, `demo`, `workshop`, `Q&A` |
| References/resources field | Knowledge sessions link to external docs, code, articles — storing the reference alongside the session is the point | Low | Text or structured array; `references: JSONB` (array of `{label, url}`) or plain text |
| Appears as a dedicated tab within the existing Calendar view | Calendar integration is explicitly required; teams expect "all scheduling in one place" | Medium | New tab/section in `CalendarView`; sessions appear as events using existing calendar rendering but with a distinct visual type |
| All team members can view upcoming sessions | Knowledge sharing is team-wide; visibility is universal | Low | No permission restriction on reads; all team members see all sessions |
| Only manager/supervisor can create/edit/cancel sessions | Scheduling is a management function to prevent calendar noise | Low | RBAC check: `supervisor` or `admin` role required on write endpoints |
| Session date and time (inherits calendar event semantics) | It's a scheduled event; needs start datetime | Low | Reuse existing `ScheduledEvent` pattern or FK into it |
| Tags for categorization | Teams want to browse "all Python sessions" or "all architecture sessions" | Low | Array of string tags; stored as JSONB or a tags relation |

### Differentiators

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| Presenter is a team member (assignee FK) | Ties session to the person responsible; shows on their calendar; creates accountability | Low | `presenter_id` FK to `users`; presenter sees it in their own calendar events |
| Session type badge in the calendar view | At a glance, "workshop" vs "Q&A" requires different prep; visual type label on the calendar event improves scanability | Low | Color-coded or icon-coded badge per session type on the calendar card |
| In-app notification to all team members when a session is scheduled | Without notification, members miss new sessions; scheduling a session should announce it | Medium | On session create, fan out a notification to all team members (reuse existing notification pattern) |
| Reminder notification before the session | Members forget; a 30-min or 1-hour reminder is high value | Medium | Reuse existing `EventNotification` scheduler pattern; auto-create on session save |
| References shown on session detail view | Resource links should be clickable and prominently displayed on the session page, not buried in a description textarea | Low | Render `references` array as a list of anchor links |

### Anti-Features

| Anti-Feature | Why Avoid | What to Do Instead |
|--------------|-----------|-------------------|
| Members can propose sessions (with approval flow) | Approval workflows add state machine complexity; this is an internal tool where the supervisor directs knowledge sharing | Members propose sessions informally via chat; supervisor creates the formal session |
| Video conferencing embed or meeting link auto-generation | Zoom/Teams integration is significant scope; sessions are in-person or handled externally | Provide a plain text "location/link" field the supervisor fills manually |
| Attendance tracking (RSVP/present/absent) | Surveillance feature that creates anxiety; knowledge sharing should be low-pressure | No attendance tracking; focus on the content, not the headcount |
| Recurring session series (weekly tech talk that repeats) | Recurrence rules add significant scheduler complexity | Create sessions individually; copy-paste is acceptable for a small team |
| Rating or feedback form after sessions | Turns a lightweight calendar entry into a mini-LMS; out of scope | Use chat for follow-up discussion |
| Full LMS features (quizzes, certificates, progress tracking) | Massive scope creep; this is a calendar event type, not a course platform | Keep it as a specialized event with references |

### Complexity Notes

- Backend: new `KnowledgeSession` model (or specialized `ScheduledEvent` subtype). Decide: extend existing `ScheduledEvent` with a `session_type` discriminator column, or create a separate table. Recommendation: separate `knowledge_sessions` table to avoid polluting the existing scheduler schema with optional fields. Relationships: `presenter_id` → users, calendar events cross-linked. Medium complexity.
- Frontend: new tab component inside the existing Calendar view. Session list + session detail card. Session create/edit form (supervisor only). Low-medium complexity — the calendar rendering infrastructure already exists.
- Key risk: how sessions appear on the existing calendar. If the calendar currently renders only `ScheduledEvent` rows, either sessions must also create a `ScheduledEvent` row (for notification/reminder purposes) or the calendar query must be extended to union-join `knowledge_sessions`. The simpler path: create a `ScheduledEvent` row as a "backing event" when a session is created, so the notification/reminder scheduler works without changes.

### Dependencies on Existing Features

- Existing calendar/scheduler (existing): sessions either extend or create backing `ScheduledEvent` rows for reminder triggers
- Existing `EventNotification` + scheduler (existing): reuse for session reminders and creation announcements
- User/RBAC (existing): read open to all team members; write restricted to supervisor/admin
- WebSocket chat (existing): link from session to a chat channel for follow-up discussion (optional differentiator)

---

## 9. Team Weekly Board with AI Summary

**Context:** Tools like Notion's team updates page, Confluence's team space, and GitLab's "Weekly updates" pattern are the reference points. The AI summary layer is the differentiator — it requires the existing LiteLLM integration. Range.io also has a "goals + weekly updates" board.

**Confidence:** HIGH for the board feature pattern; HIGH for the AI summary integration given LiteLLM is already in the stack.

### Table Stakes

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Any team member can post a weekly markdown update | The feature is explicitly a team-wide markdown board; universal posting rights are the stated requirement | Low | `POST /api/weekly-board/posts`; no role restriction on create |
| Posts are visible to all team members and supervisor | Team boards are shared by definition | Low | Read access: all team members; no supervisor-only filtering |
| Markdown rendering on post display | If the input is markdown, the display must render it — plain text display of markdown is unacceptable UX | Low | Use existing markdown rendering (likely already present for task descriptions); `marked` or `svelte-markdown` |
| Post includes author and timestamp | Context for readers — "who said this, when" | Low | `author_id` FK to users, `created_at`, `week_label` (ISO week string e.g. "2026-W17") |
| Posts grouped or filterable by week | The board is a "weekly" board; users read it week by week | Low | Query param `?week=2026-W17`; default to current week |
| On-demand AI summary of all posts for a given week | Explicitly required; member or supervisor clicks "Summarize this week" | Medium | POST to LiteLLM with all posts for the week as context; response stored or streamed |
| End-of-week automatic AI summary generation | Explicitly required; runs on a schedule (Friday evening or start of Monday) | Medium | Scheduler job (extend existing `scheduler_jobs.py`); stores summary in `weekly_summaries` table |
| AI summary visible alongside posts | The summary should appear at the top or bottom of the week view, not on a separate page | Low | Render `WeeklySummary` row if it exists for the current week |

### Differentiators

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| AI summary regeneration (re-run after new posts are added) | If posts come in after the auto-summary ran, the summary is stale; a "regenerate" button keeps it current | Low | Same endpoint as on-demand; overwrites the existing summary for the week |
| Summary scoped to a team (not cross-team) | In a multi-team deployment, each team's board should summarize only their own posts | Low | `team_id` scoping on posts and summaries; already a pattern from other features |
| Post edit within the same week | Authors should be able to fix typos before the summary runs | Low | `PATCH /api/weekly-board/posts/{id}`; restrict to `author_id = current_user.id` and `week_label = current_week` |
| Pinning a post or marking it as a highlight | Supervisor can surface key updates in the week view | Medium | Boolean `is_pinned` on post; pinned posts appear first in the week view |

### Anti-Features

| Anti-Feature | Why Avoid | What to Do Instead |
|--------------|-----------|-------------------|
| Post comments / threaded discussion | This turns the board into a second chat; the existing WebSocket chat already covers discussion | Link from a post to the relevant chat channel |
| Per-post AI analysis ("Summarize just this post") | A single-post summary adds no value over reading the post; the value is cross-post synthesis | AI summary is week-scoped only |
| Forcing a structured template for posts | Range uses goal-linked templates; Notion uses free pages; for a small team, freeform markdown is lower friction and more expressive | Provide a placeholder hint in the textarea, not a mandatory structure |
| Versioned post history | Edit history for weekly updates is over-engineering for a 5–15 person tool | Allow one edit per post per week; no version trail |
| Cross-week AI summary ("summarize the last 4 weeks") | Interesting but not requested; LLM context window and cost grow with scope | Defer; per-week summary covers 90% of the use case |
| Email digest of weekly board | Out of scope in PROJECT.md (no email notifications) | In-app only |
| Voting or reactions on posts | Slack-style reactions create gamification dynamics unsuited to a serious work update board | No reactions; the board is informational |

### Complexity Notes

- Backend: new `WeeklyPost` table + `WeeklySummary` table. Three endpoints: post CRUD, summary on-demand, summary auto-trigger. LiteLLM call is a single prompt with all week posts concatenated. Medium complexity.
- Frontend: one new route/page (`/board` or `/updates`). Week selector, post list (markdown-rendered), post form, summary panel. Low-medium complexity.
- AI integration: prompt design is the main risk — collecting all posts for a week, formatting them clearly for the model, and generating a meaningful narrative summary. The existing AI pattern (LiteLLM with `LITELLM_MODEL` env var) applies directly; no new infrastructure needed.
- Scheduler: auto-summary job runs at end of week. Extend `scheduler_jobs.py` with a weekly cron. Trigger time: Friday at 18:00 local (or configurable). Creates a `WeeklySummary` row only if posts exist for that week.

### Dependencies on Existing Features

- LiteLLM integration (existing): AI summary uses the same `litellm.completion()` call pattern already established
- Scheduler / `scheduler_jobs.py` (existing): end-of-week auto-summary extends the existing scheduler
- User/RBAC (existing): all team members can post and read; supervisor has no special write access beyond the team
- Markdown rendering (likely existing for task descriptions): reuse the same renderer for posts

---

## v2.2 Feature Dependency Map

```
Member Standup Posts (7)
    └── reads: Task model (existing) — snapshot at post time
    └── uses: Notification system (existing) — blocker alert to supervisor
    └── no new dependencies on v2.2 features

Knowledge Sharing Scheduler (8)
    └── extends: Calendar/ScheduledEvent (existing) — backing event or tab
    └── uses: EventNotification + scheduler (existing) — reminders
    └── no dependency on Feature 7 or 9

Team Weekly Board + AI Summary (9)
    └── uses: LiteLLM (existing) — AI summary call
    └── extends: scheduler_jobs.py (existing) — weekly cron
    └── no dependency on Feature 7 or 8
```

**All three v2.2 features are independent of each other. Each can be phased without blocking the others.**

**Recommended build order within v2.2:**
1. Member Standup Posts — lowest risk, no scheduler changes, direct read of existing task data
2. Knowledge Sharing Scheduler — medium risk (calendar integration), no AI involved
3. Team Weekly Board + AI Summary — medium risk, AI prompt design requires iteration

---

## v2.0 Feature Dependency Map

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

**Recommended build order for v2.0:**
1. Task types — isolated, zero breaking changes, unblocks KPI enrichment immediately
2. Multi-team hierarchy — foundational; gates visibility and sprint reminders
3. Sprint model — requires team hierarchy for scoping; story_points field added here
4. Custom Kanban statuses — the riskiest migration (enum → string); do after sprint model so burndown queries can be written correctly from the start
5. Advanced KPIs — can only be completed once 1–4 are done
6. Sprint reminders — can be completed once 1 and 2 are done (does not require custom statuses or KPIs)

---

## MVP Recommendation for v2.2

**Build all three features.** They are independent, the scope is bounded, and all build on existing infrastructure.

**Priority order:**
1. Member Standup Posts — highest daily-use value for a supervisor who needs async team visibility
2. Team Weekly Board + AI Summary — the AI differentiator gives the product a capability none of the raw task tools have
3. Knowledge Sharing Scheduler — lower daily frequency but high team development value

**Do not defer any of them** — they are small enough individually that deferral buys little while leaving the milestone incomplete.

**Be conservative on these specifically:**
- Standup task snapshot: store as a JSON column at submit time, not a live query on render — preserves historical accuracy when tasks change after the post
- Weekly board AI summary: design the prompt with a token budget in mind; 15 posts of ~200 words each = ~3,000 tokens; well within standard model context limits
- Calendar integration for Knowledge Sessions: validate the existing calendar data model before deciding whether to create backing `ScheduledEvent` rows or extend the calendar query — wrong choice here causes a rewrite
