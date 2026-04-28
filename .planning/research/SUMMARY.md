# Project Research Summary

**Project:** TeamFlow v2.2 — Team Updates, Knowledge Sharing & Weekly Board
**Domain:** Async communication layer on top of an existing team task management app
**Researched:** 2026-04-28
**Confidence:** HIGH

---

## Executive Summary

v2.2 adds three async-communication features: standup posts, a knowledge sharing scheduler, and a team weekly board with AI summaries. All three build entirely on existing infrastructure — LiteLLM, APScheduler, the notification system, and the calendar view are reused without modification. The only new packages are two frontend libraries (`marked` + `dompurify`) to render and sanitize user markdown. Zero new backend packages are required.

**Build order:** Phase A (standup) → Phase B (KS scheduler) → Phase C (weekly board + AI)
Ordered by risk profile: lowest first to validate migration patterns, `ALTER TYPE` isolated in B, AI + cron combined last in C.

---

## Stack Additions

| Package | Side | Version | Purpose |
|---------|------|---------|---------|
| `marked` | frontend | ^14.x | Parse markdown to HTML |
| `dompurify` | frontend | ^3.x | Sanitize HTML before `{@html}` |
| `@types/dompurify` | frontend (dev) | ^3.x | TypeScript types |

**Zero new backend packages.** `apscheduler`, `litellm`, `sqlalchemy`, `alembic`, `pydantic` already installed.

**Do not add:** Tiptap, ProseMirror, remark/rehype, Redis, Celery, SSE.

---

## Feature Table Stakes

### Member Standup Posts
- Three-field freeform post: "What I did", "What I'm working on", "Blockers"
- Task status snapshot captured **server-side at submit time** (JSONB, frozen — not a live query)
- Team feed; author-only edit/delete; `cadence` field (`daily` | `weekly`)

### Knowledge Sharing Scheduler
- Session fields: topic, description, references, presenter (user FK), session type (presentation/demo/workshop/qa), duration, date/time, tags
- Supervisor/admin-only create/edit/delete; all team members read
- "Knowledge Sessions" **tab inside existing `/schedule`** — not a new route
- In-app reminder notification before session; creation fan-out notification on new session

### Team Weekly Board + AI Summary
- Any member posts markdown scoped to current ISO week (`week_start` Date column)
- On-demand AI summary ("Summarize this week") — stored, not regenerated on every load
- Automatic end-of-week summary via APScheduler `CronTrigger` (Sunday 23:00)
- Summary stored in `WeeklyBoardSummary`; regeneration overwrites existing row for that week

---

## Architecture Overview

### New Models
| Model | File | Notes |
|-------|------|-------|
| `StandupPost` | `models/updates.py` | `task_snapshot JSONB`, `cadence` enum |
| `KnowledgeSession` | `models/knowledge.py` | Team-scoped; `session_type` enum; `references` text |
| `WeeklyPost` | `models/board.py` | Scoped to `week_start` ISO date |
| `WeeklyBoardSummary` | `models/board.py` | One row per week; `trigger` enum; overwritten on regen |

### New Enum Values / Types
- `StandupCadence`: `daily | weekly`
- `KnowledgeSessionType`: `presentation | demo | workshop | qa`
- `NotificationEventType` (**existing** PostgreSQL enum): add `knowledge_session` via `ALTER TYPE` migration **outside a transaction block**

### New Routes / Pages
| Route | Type | Notes |
|-------|------|-------|
| `/updates` | New route | Standup post form + team feed |
| `/board` | New route | Weekly board with AI summary panel |
| KS sessions | New tab in `/schedule` | Not a separate route |

### Pattern Reuse
- AI generation: follows `routers/ai.py` project summary pattern via `utils/ai_client.py`
- Scheduler job: one `CronTrigger(day_of_week='sun', hour=23)` added to `internal/scheduler_jobs.py`
- Notifications: reuses `EventNotification` model and existing delivery poll

---

## Watch Out For

1. **XSS via `{@html}` without DOMPurify** — Always wrap: `DOMPurify.sanitize(marked.parse(raw))`. Install `dompurify` in the same commit as the first `{@html}` usage. Stored XSS risk: malicious markdown executes for every viewer.

2. **`ALTER TYPE` PostgreSQL enum extension inside a transaction** — `ALTER TYPE notificationeventtype ADD VALUE` fails in PostgreSQL inside a transaction block. Write as a dedicated Alembic migration with `execute_as_transaction=False`. Test against PostgreSQL container — SQLite silently passes.

3. **Task snapshot as live query** — Using a live task query at render time makes historical standups meaningless. Store `task_snapshot` as `JSONB` at POST time, server-generated. Irreversible without a data migration.

4. **AI summary cost / hallucination on empty input** — Cache result; skip regeneration if summary created within 30 minutes; apply token budget (~50k char max); short-circuit with "no updates this week" if no posts exist (model will hallucinate otherwise).

5. **`Schedule` model is `user_id`-scoped** — Reusing it for KS sessions (team-scoped) will silently hide sessions from team members. Use a separate `KnowledgeSession` table.

---

## Build Order Rationale

| Phase | Feature | Why here |
|-------|---------|---------|
| A | Standup posts | Lowest risk; validates new model + migration pattern; installs markdown rendering with XSS protection |
| B | KS scheduler | Isolates `ALTER TYPE` migration in one phase before AI work begins |
| C | Weekly board + AI | Combines AI prompt, first `CronTrigger` job, and most complex UI; benefits from A+B patterns |

---

*Research completed: 2026-04-28 | Ready for roadmap: yes*
