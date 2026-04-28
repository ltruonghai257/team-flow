# Technology Stack — Milestone v2.2 Additions

**Project:** TeamFlow v2.2 (Team Updates, Knowledge Sharing, Weekly Board)
**Researched:** 2026-04-28
**Scope:** NEW dependencies only — what the existing FastAPI + SvelteKit 5 + PostgreSQL 16 + TailwindCSS stack needs for the three new feature areas in v2.2.

---

## Summary

All three v2.2 features (standup posts, knowledge-sharing scheduler, weekly board with AI summary) are achievable with **one new frontend library** (`marked` + `dompurify` as a pair) and **zero new backend packages**. The AI summary pattern, scheduler trigger, and database layer all reuse what is already present.

---

## New Dependencies

### Frontend

| Library | Version | Purpose | Why |
|---------|---------|---------|-----|
| `marked` | `^14.x` (verify with `yarn info marked version`) | Parse markdown to HTML in the browser | Lightweight (< 25 kB gzip), no DOM dependency, runs in SvelteKit SSR and CSR modes. Used by Open WebUI (the reference architecture for this project) for the same purpose — chat message and post rendering. Pure-JS, no build-time config needed. |
| `dompurify` | `^3.x` (verify with `yarn info dompurify version`) | Sanitize HTML produced by `marked` before injecting into the DOM | Required whenever `{@html ...}` is used with user-supplied text. Prevents XSS from crafted markdown. `marked` alone does NOT sanitize. `dompurify` is the standard browser-side sanitizer; it has no runtime dependencies and is < 7 kB gzip. |
| `@types/dompurify` | matching `dompurify` major | TypeScript types for DOMPurify | DOMPurify ships no bundled types; this package provides them. Dev-only. |

**Net new frontend packages: 3** (`marked`, `dompurify`, `@types/dompurify`).

**Install:**
```bash
yarn add marked dompurify
yarn add -D @types/dompurify
```

**Usage pattern in SvelteKit components:**
```typescript
import { marked } from 'marked';
import DOMPurify from 'dompurify';

function renderMarkdown(raw: string): string {
  return DOMPurify.sanitize(marked.parse(raw) as string);
}
```
Then in template: `{@html renderMarkdown(post.content)}`

**Why not a heavier editor?** The three features need:
1. Rendering stored markdown (read-only display) — `marked` + `dompurify` is sufficient.
2. Authoring (standup post, weekly board post) — a plain `<textarea>` with live preview is the right complexity level for a team-internal tool. A full rich-text editor (Tiptap, Milkdown, ProseMirror) adds 200–500 kB and a plugin system for no user benefit over a split-pane textarea + preview.

**Why not `@tailwindcss/typography`?** It is already a natural fit for styling rendered markdown but is a dev/CSS-only addition, not a JS package. It can be added as a Tailwind plugin at implementation time (`yarn add -D @tailwindcss/typography`, one line in `tailwind.config.js`). It is not strictly required — prose styling can be done with existing Tailwind utilities — so it is listed here as an optional convenience, not a required dependency.

### Backend

| Library | Version | Purpose | Why |
|---------|---------|---------|-----|
| No new packages required | — | All v2.2 features | `apscheduler`, `litellm`, `sqlalchemy`, `alembic`, and `pydantic` already cover everything. |

**Net new backend packages: zero.**

---

## Integration Points

### 1. LiteLLM — AI Weekly Summary (Confirmed Pattern)

The existing `acompletion` wrapper in `backend/app/utils/ai_client.py` is the correct call point. The pattern used in `routers/ai.py` for project summaries applies directly:

```python
from app.utils.ai_client import acompletion
from app.core.config import settings

response = await acompletion(
    model=settings.AI_MODEL,
    messages=[
        {"role": "system", "content": SUMMARY_SYSTEM_PROMPT},
        {"role": "user", "content": aggregated_posts_text},
    ],
    temperature=0.3,
)
summary_text = response.choices[0].message.content
```

The weekly summary endpoint:
- Collects all `WeeklyPost` rows for the current ISO week.
- Concatenates their content into a single prompt block (same pattern as `_build_summary_context_block`).
- Calls `acompletion` via the existing wrapper.
- Stores the result back on a `WeeklyBoardSummary` model row (or a `summary` field on a per-week aggregate record).
- Returns it from the endpoint and also triggers it from the scheduler job.

No new LiteLLM configuration, no new env vars, no streaming required for this use case.

### 2. APScheduler — Weekly Summary Trigger

The existing `AsyncIOScheduler` in `backend/app/internal/scheduler_jobs.py` is already running. Add one new job:

```python
sched.add_job(
    generate_weekly_summary_job,
    trigger="cron",
    day_of_week="sun",
    hour=23,
    minute=0,
    id="generate_weekly_summary",
    replace_existing=True,
)
```

The job calls the same LiteLLM wrapper used by the on-demand endpoint. No new scheduler library, no Redis, no Celery.

Confidence: HIGH — the scheduler already uses `AsyncIOScheduler` with `interval` triggers. Adding a `cron` trigger is a supported APScheduler feature on the same scheduler instance (`apscheduler>=3.10.4` is already installed).

### 3. Knowledge Sessions — Existing Calendar Model

The existing `Schedule` model in `models/work.py` has `title`, `description`, `start_time`, `end_time`, `location`, and `user_id`. Knowledge sessions need additional fields: `topic`, `session_type` (enum: presentation/demo/workshop/Q&A), `presenter_id` (FK to users), `references` (text), `tags` (array or text), and `duration_minutes`.

**Two options:**

**Option A (recommended): New `KnowledgeSession` model.** A separate table avoids polluting `Schedule` with knowledge-specific nullable columns. The calendar frontend filters by event type to show sessions in their own tab. The `KnowledgeSession` rows appear as calendar items by also creating a corresponding `Schedule` row (or by having the calendar query both tables and union them client-side).

**Option B: Extend `Schedule`.** Add an `event_type` discriminator column and knowledge-specific columns to `schedules`. Simpler migration, but the `Schedule` model grows wide with NULLable columns that only apply to one event type.

Recommendation: Option A. The calendar's existing query filters by `user_id`; the new tab queries `/api/knowledge-sessions` independently. No JOIN required.

### 4. Standup Posts — New Model

`StandupPost` table: `id`, `user_id FK`, `post_type` (daily/weekly enum), `content TEXT` (markdown), `task_snapshot JSONB` (snapshot of user's tasks at post time), `created_at`, `week_number INT`, `year INT` (for grouping). No existing model to extend.

`task_snapshot` stores a lightweight JSON array of `{task_id, title, status}` at the moment of posting. PostgreSQL's `JSONB` type is already used in the project; SQLAlchemy supports it natively with `JSON` column type.

### 5. Weekly Board Posts — New Model

`WeeklyPost` table: `id`, `user_id FK`, `content TEXT` (markdown), `week_number INT`, `year INT`, `created_at`, `updated_at`. Posts are editable by the author until the week ends (or a supervisor locks the board).

`WeeklyBoardSummary` table: `id`, `week_number INT`, `year INT`, `summary TEXT`, `generated_at`, `generated_by` (enum: `auto`/`manual`). One row per week. The `auto` variant is created by the Sunday cron job; `manual` by a supervisor-triggered endpoint.

---

## What NOT to Add

| Temptation | Why to Avoid |
|-----------|--------------|
| **Tiptap / ProseMirror / Milkdown / Quill** | Full rich-text editors are 200–500 kB with complex plugin APIs. A textarea + `marked` preview covers all three v2.2 authoring needs without the weight or the maintenance surface. |
| **`svelte-markdown` or `svelte-remarkable`** | These are thin Svelte wrappers around the same underlying parsers (marked/remarkable). They add an abstraction layer for no benefit when you can call `marked.parse()` directly in a helper function. Both have lower maintenance activity than `marked` itself. |
| **`highlight.js` or `prismjs`** | Syntax highlighting for code blocks is not needed in standup posts or weekly updates. Do not add a syntax highlighter unless a future milestone explicitly requires it in knowledge-sharing references. |
| **`remark` / `rehype` / `unified`** | The unified/remark ecosystem is excellent but is a pipeline of composable plugins — appropriate when you need custom AST transforms, MDX, or server-side rendering to static HTML. For browser-side "convert markdown to safe HTML", `marked` + `dompurify` is materially simpler. |
| **Redis / Celery / RQ** | The weekly summary cron is a single APScheduler `cron` job. No external broker is needed for one scheduled task. |
| **`pg_cron` / database-level scheduling** | APScheduler is already deployed and tested. Moving scheduling into the database adds operational complexity for zero benefit. |
| **A separate "feed" or activity-stream library** | Standup posts and weekly board posts are simple timestamped rows. A dedicated activity-stream library (e.g., Stream.io) is overkill for < 15 users. |
| **Server-Sent Events or a second WebSocket channel for live board updates** | The weekly board does not require real-time collaboration. HTTP polling (or a page reload after posting) is sufficient. Do not extend the WebSocket infrastructure for this feature. |
| **`@tailwindcss/typography` as a required install** | Markdown prose styling is achievable with existing Tailwind utilities. Add only if the team wants it as a convenience — it is a zero-JS dev dependency and can be added in one line at implementation time. |

---

## Confidence Assessment

| Area | Confidence | Basis |
|------|------------|-------|
| `marked` + `dompurify` recommendation | HIGH | Industry-standard pair, used by Open WebUI (project reference), verified against `package.json` (not yet installed — confirmed no conflict). |
| LiteLLM usage pattern | HIGH | Read actual source of `ai_client.py` and `routers/ai.py`; pattern is clear and directly transferable. |
| APScheduler cron trigger | HIGH | `apscheduler>=3.10.4` installed; `cron` trigger is a core APScheduler feature, same scheduler instance used. |
| Zero new backend packages | HIGH | All dependencies (`apscheduler`, `litellm`, `sqlalchemy`, `alembic`, `pydantic`) verified present in `requirements.txt`. |
| `marked` current version (^14.x) | MEDIUM | Based on training data (knowledge cutoff Aug 2025); verify exact version at implementation time with `yarn info marked version`. |
| `dompurify` current version (^3.x) | MEDIUM | Same caveat — verify at implementation time. |
