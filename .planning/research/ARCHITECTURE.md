# Architecture Patterns

**Project:** TeamFlow v2.2 — Team Updates, Knowledge Sharing & Weekly Board
**Researched:** 2026-04-28

---

## Feature Integration Map

### Feature 1: Member Standup Updates

**What it is:** A member posts a daily/weekly standup (what I did, pending, blockers) that captures a point-in-time snapshot of their assigned task statuses. Visible to all team members and the supervisor.

**Integration points:**

- **New domain, new router** (`/api/updates`). No existing router handles this concept; the `tasks` router owns task mutation, not standup reporting. A dedicated router keeps concerns separate and is consistent with the existing pattern (one router per domain).
- **Reads from `tasks` table** at submission time to snapshot the member's current assigned task statuses. The snapshot is stored denormalized (JSON string in a Text column) so the historical record is stable even after tasks change.
- **No writes to tasks** — the standup post is read-only with respect to tasks. It does not mutate task status; it captures a moment in time.
- **RBAC:** any authenticated user can create their own standup. Read: all authenticated users (team visibility). No supervisor-only gate beyond what already exists.
- **No scheduler dependency** — posting is user-initiated. A reminder APScheduler job is a v2.3 concern.

**Existing components untouched:** tasks router, Kanban, performance dashboard.

---

### Feature 2: Knowledge Sharing Scheduler

**What it is:** Manager/supervisor creates knowledge-sharing sessions with rich metadata (topic, description, references, presenter/assignee, session type, duration, tags). Sessions appear inside the existing `/schedule` calendar page as a new tab or filter.

**Integration points:**

- **New DB table** (`knowledge_sessions`) rather than extending `Schedule`. `Schedule` is a personal calendar event owned by one user (`user_id` FK, per-user query in `schedules.py`). Knowledge sessions are team-wide objects with a different shape (presenter, type enum, references, tags, duration). Shoehorning them into `Schedule` would require nullable sentinel columns and break the single-owner query assumption.
- **New router** (`/api/knowledge-sessions`). Added to `api/main.py` alongside the existing `schedules` router.
- **Calendar page is modified (new tab)**, not replaced. The `/schedule` +page.svelte already aggregates multiple event sources (`allEvents = [...scheduleList, ...taskEvents]`). Adding a third source (knowledge sessions) for calendar dots is a minimal change. The richer list view (upcoming sessions, detail modal) lives in a new "Sessions" tab panel within the same page.
- **RBAC:** create/edit/delete: supervisor or admin only. Read: all authenticated users.
- **Notification hook:** when a session is created, optionally enqueue an `EventNotification` using the existing `NotificationEventType` enum. A new enum value `knowledge_session` is added; the existing `process_due_notifications` scheduler job picks it up automatically — no scheduler code changes required.
- **Frontend API module** `lib/apis/knowledge-sessions.ts` is new.

---

### Feature 3: Team Weekly Board

**What it is:** Any team member posts a weekly markdown update. The AI generates a team-wide summary automatically at end of week and on demand. Posts are visible to everyone.

**Integration points:**

- **New domain, new router** (`/api/weekly-board`). Two sub-resources: posts (`/api/weekly-board/posts`) and summaries (`/api/weekly-board/summaries`).
- **AI summary reuses `ai_client.py` (`acompletion`)** exactly as `ai.py` does for project summaries. The pattern in `_fetch_project_summary_data` / `_build_summary_context_block` / `acompletion` call is a clean template. Weekly summary endpoint follows the same shape: fetch all posts for the current ISO week, build context block, call `acompletion`, persist result.
- **Auto-generation via APScheduler:** add a weekly cron job in `internal/scheduler_jobs.py` (Friday EOD or Monday morning) using the existing `AsyncIOScheduler`. The new job follows the `process_due_notifications` / `reconcile_generated_reminders_job` pattern: opens its own `AsyncSessionLocal` context, runs the summary logic, persists a `WeeklySummary` row.
- **On-demand generation:** POST `/api/weekly-board/summaries/generate` (supervisor/admin only) calls the same logic path as the cron job. This is consistent with the `/api/ai/project-summary` on-demand endpoint.
- **New frontend route** `/weekly-board` (+page.svelte). Add nav item in `+layout.svelte` `navItems` array. No existing route is extended.
- **Markdown rendering:** a lightweight markdown renderer (e.g., `marked` or `svelte-markdown`) renders post bodies and the AI summary. Check `package.json` first; if `marked` is already present, no new dependency is needed.

---

## New DB Models (table name + key columns)

### `standup_updates`

| Column | Type | Notes |
|---|---|---|
| `id` | Integer PK | |
| `author_id` | Integer FK → users.id | indexed |
| `cadence` | Enum (`daily`, `weekly`) | |
| `week_start` | Date | ISO week start Monday; for weekly listing/dedup |
| `what_i_did` | Text | freeform |
| `pending` | Text | freeform |
| `blockers` | Text | nullable |
| `task_snapshot` | Text | JSON-serialized `[{id, title, status}]` at post time |
| `created_at` | DateTime | |

Snapshot stored as JSON string in `Text` column — consistent with how `Task.tags` stores comma-separated values; the app does not use SQLAlchemy `JSON` type elsewhere.

---

### `knowledge_sessions`

| Column | Type | Notes |
|---|---|---|
| `id` | Integer PK | |
| `topic` | String | not null |
| `description` | Text | nullable |
| `references` | Text | nullable; plain text or newline-separated URLs |
| `presenter_id` | Integer FK → users.id | nullable (session with no single presenter) |
| `session_type` | Enum (`presentation`, `demo`, `workshop`, `qa`) | new `KnowledgeSessionType` enum in `models/enums.py` |
| `start_time` | DateTime | not null |
| `duration_minutes` | Integer | not null |
| `tags` | String | comma-separated; matches `Task.tags` pattern |
| `created_by_id` | Integer FK → users.id | supervisor/admin who created |
| `created_at` | DateTime | |
| `updated_at` | DateTime | |

New enum `KnowledgeSessionType` added to `models/enums.py`.

---

### `weekly_board_posts`

| Column | Type | Notes |
|---|---|---|
| `id` | Integer PK | |
| `author_id` | Integer FK → users.id | indexed |
| `week_start` | Date | ISO Monday; indexed for week-based queries |
| `content` | Text | Markdown body |
| `created_at` | DateTime | |
| `updated_at` | DateTime | |

---

### `weekly_board_summaries`

| Column | Type | Notes |
|---|---|---|
| `id` | Integer PK | |
| `week_start` | Date | unique constraint; one summary per week |
| `content` | Text | AI-generated markdown |
| `generated_by` | Enum (`auto`, `manual`) | cron vs on-demand |
| `generated_at` | DateTime | |
| `model` | String | nullable; AI model name (mirrors `AIMessage.model`) |

`week_start` unique constraint lets the cron job upsert cleanly.

---

## Routes & Components (new vs modified)

### Backend — New Routers

| Router file | Prefix | Notes |
|---|---|---|
| `routers/updates.py` | `/api/updates` | |
| `routers/knowledge_sessions.py` | `/api/knowledge-sessions` | |
| `routers/weekly_board.py` | `/api/weekly-board` | posts + summaries sub-resources |

**Key endpoints — `routers/updates.py`:**
- `GET /api/updates/` — list all recent standup posts (`?author_id=`, `?week=`)
- `POST /api/updates/` — create standup; auto-snapshots caller's assigned tasks
- `GET /api/updates/{id}` — get single post
- `DELETE /api/updates/{id}` — delete own post or supervisor

**Key endpoints — `routers/knowledge_sessions.py`:**
- `GET /api/knowledge-sessions/` — list all (all users)
- `POST /api/knowledge-sessions/` — create (supervisor/admin only)
- `GET /api/knowledge-sessions/{id}` — get single
- `PATCH /api/knowledge-sessions/{id}` — update (supervisor/admin only)
- `DELETE /api/knowledge-sessions/{id}` — delete (supervisor/admin only)

**Key endpoints — `routers/weekly_board.py`:**
- `GET /api/weekly-board/posts` — list posts (`?week=ISO-date`)
- `POST /api/weekly-board/posts` — create post (any authenticated user)
- `PATCH /api/weekly-board/posts/{id}` — edit own post
- `DELETE /api/weekly-board/posts/{id}` — delete own post or supervisor
- `GET /api/weekly-board/summaries/current` — get this week's summary (404 if none)
- `POST /api/weekly-board/summaries/generate` — on-demand AI generation (supervisor/admin)

### Backend — Modified Files

| File | Change |
|---|---|
| `models/enums.py` | Add `KnowledgeSessionType` enum; add `knowledge_session` to `NotificationEventType` |
| `models/__init__.py` | Re-export 4 new model classes |
| `internal/scheduler_jobs.py` | Add weekly summary cron job (cron trigger, Friday 17:00 local) |
| `api/main.py` | 3 new `include_router` calls |

New model files follow the existing split-by-domain pattern:
- `models/updates.py` — `StandupUpdate`
- `models/knowledge.py` — `KnowledgeSession`
- `models/board.py` — `WeeklyBoardPost`, `WeeklyBoardSummary`

### Frontend — New Files

| File | Purpose |
|---|---|
| `src/routes/updates/+page.svelte` | Standup feed; post composer at top, chronological list below |
| `src/routes/weekly-board/+page.svelte` | Weekly board; post composer, post list, AI summary panel |
| `src/lib/apis/updates.ts` | API client for `/api/updates` |
| `src/lib/apis/knowledge-sessions.ts` | API client for `/api/knowledge-sessions` |
| `src/lib/apis/weekly-board.ts` | API client for `/api/weekly-board` |
| `src/lib/components/updates/StandupForm.svelte` | Post modal with task snapshot preview table |
| `src/lib/components/updates/StandupCard.svelte` | Single standup post display |
| `src/lib/components/board/WeeklyPostEditor.svelte` | Markdown textarea + preview toggle |
| `src/lib/components/board/AiSummaryPanel.svelte` | AI summary display + "Regenerate" button (supervisor only) |
| `src/lib/components/knowledge/SessionForm.svelte` | Create/edit modal for sessions (supervisor only) |
| `src/lib/components/knowledge/SessionCard.svelte` | Session list item for calendar sidebar |

### Frontend — Modified Files

| File | Change |
|---|---|
| `src/routes/+layout.svelte` | Add "Updates" (`/updates`) and "Weekly Board" (`/weekly-board`) to `navItems` array |
| `src/routes/schedule/+page.svelte` | Add "Sessions" tab; load knowledge sessions in `loadAll()`; add `source: 'knowledge_session'` to `allEvents`; render `SessionCard` in upcoming panel when tab is active |
| `src/lib/apis/index.ts` | Re-export 3 new API modules |

---

## Build Order with Rationale

### Phase A: Member Standup Updates

**Build first because:** Completely self-contained. Reads the `tasks` table but writes nothing to it. No dependency on Features 2 or 3. Delivers immediate team value and establishes the "team-visible post" pattern that Feature 3 reuses.

Deliverables in order:
1. Alembic migration: `standup_updates` table
2. `models/updates.py` — `StandupUpdate` + export from `models/__init__.py`
3. New schemas (inline in router or `schemas/updates.py`)
4. `routers/updates.py` — CRUD + task snapshot query at POST time
5. Register in `api/main.py`
6. `src/lib/apis/updates.ts`
7. `StandupForm.svelte` — task list auto-populated via existing `tasksApi.list()`
8. `StandupCard.svelte`
9. `src/routes/updates/+page.svelte`
10. Nav item in `+layout.svelte`

---

### Phase B: Knowledge Sharing Scheduler

**Build second because:** Independent of Features 1 and 3. Calendar page change is a contained extension. The `NotificationEventType` enum addition is a backward-compatible migration. Building after Phase A validates the "new domain = new router + new model + new migration" rhythm before adding AI complexity.

Deliverables in order:
1. Alembic migration: add `knowledge_session` to `NotificationEventType` enum + `knowledge_sessions` table + `KnowledgeSessionType` enum
2. `models/enums.py` additions
3. `models/knowledge.py` — `KnowledgeSession` + export
4. New schemas
5. `routers/knowledge_sessions.py` — CRUD, optional `EventNotification` insert on POST
6. Register in `api/main.py`
7. `src/lib/apis/knowledge-sessions.ts`
8. `SessionForm.svelte` + `SessionCard.svelte`
9. Modify `src/routes/schedule/+page.svelte`: add Sessions tab, load API, render in calendar grid

---

### Phase C: Team Weekly Board + AI Summary

**Build last because:** Highest complexity. Introduces AI generation, APScheduler extension, markdown rendering, and a new nav-level route. Depends on nothing from Phases A or B, but the patterns established in those phases (new model, new router, new migration, new API module) mean Phase C follows a well-worn path. The AI summary logic is a copy-and-specialize of `_fetch_project_summary_data` + `_build_summary_context_block` from `routers/ai.py`.

Deliverables in order:
1. Alembic migration: `weekly_board_posts` + `weekly_board_summaries` + `GeneratedBy` enum
2. `models/board.py` — `WeeklyBoardPost`, `WeeklyBoardSummary` + exports
3. New schemas
4. `routers/weekly_board.py` — posts CRUD + `summaries/generate` + `summaries/current`
5. AI helper function for weekly context block (in router file or `services/weekly_summary.py`)
6. Weekly cron job in `internal/scheduler_jobs.py` (cron trigger)
7. Register router in `api/main.py`
8. `src/lib/apis/weekly-board.ts`
9. `WeeklyPostEditor.svelte` + `AiSummaryPanel.svelte`
10. `src/routes/weekly-board/+page.svelte`
11. Nav item in `+layout.svelte`

---

## Cross-Cutting Notes

**RBAC pattern:** All new routers use the existing `get_current_user` dependency. Supervisor-only gates follow the pattern in `performance.py` and `dashboard.py`: check `current_user.role in (UserRole.supervisor, UserRole.admin)`, raise `HTTPException(403)` otherwise.

**APScheduler cron extension:** Adding a new job to `start_scheduler()` in `scheduler_jobs.py` is non-destructive. The existing two jobs keep their IDs. The new job gets its own `id="generate_weekly_summary"` with a `cron` trigger (`day_of_week='fri', hour=17`).

**No WebSocket extension needed** for any of the three features. All three are poll-based (page load or manual refresh). Real-time "someone just posted a standup" notifications are a v2.3 concern.

**One Alembic migration per Phase** keeps history granular and reversible, consistent with the existing 10-migration history.

---

## Sources

- Codebase direct inspection: `backend/app/routers/`, `backend/app/models/`, `frontend/src/routes/schedule/+page.svelte`, `frontend/src/routes/+layout.svelte`, `internal/scheduler_jobs.py`, `routers/ai.py`, `models/enums.py`, `models/notifications.py`
- Confidence: HIGH — all integration points derived from reading the actual running code.
