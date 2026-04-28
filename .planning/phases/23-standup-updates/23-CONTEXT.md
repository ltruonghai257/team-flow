# Phase 23: Standup Updates - Context

**Gathered:** 2026-04-28
**Status:** Ready for planning

<domain>
## Phase Boundary

Members can post structured daily/weekly standups using a configurable template, a frozen task snapshot is stored at submit time, and the whole team can browse and filter a reverse-chronological feed at `/updates`.

</domain>

<decisions>
## Implementation Decisions

### Template Storage (UPD-02, UPD-03)
- **D-01:** The global default template (fields: Pending Tasks, Future Tasks, Blockers, Need Help From, Critical Timeline, Release Date) is stored as a row in a DB settings table — **not** hardcoded. This allows runtime changes to the default without a deploy.
- **D-02:** Per-team overrides are stored in a separate `StandupTemplate` table (one row per sub-team). Teams that have never customized have no row; they inherit the global default.
- **D-03:** Existing posts are immutable — template changes (add/remove/rename fields) only affect future posts. The JSONB snapshot in each post preserves the original field labels and values at submit time.

### Feed Layout & Display (UPD-05, UPD-06)
- **D-04:** Posts displayed as **cards, reverse-chronological** (newest first). No date-grouping or author-grouping.
- **D-05:** Task snapshot is **collapsed by default** on each card. A toggle/expand reveals the frozen task list. Template field text responses are visible without expanding.
- **D-06:** **Cursor-based pagination** with a "Load more" button (default page size: 20 posts).
- **D-07:** The standup submission form lives **on the same `/updates` page**, above the feed (or in a collapsible panel). No separate `/updates/new` route needed.

### Task Snapshot Scope (UPD-04)
- **D-08:** Snapshot captures **all tasks assigned to the submitting member** regardless of status (todo, in-progress, done, blocked).
- **D-09:** Fields stored per task in the JSONB snapshot: `id`, `title`, `status`, `priority`, `due_date` — no sprint name or project name (keep snapshot compact).

### Post Edit/Delete UX (UPD-07, UPD-08)
- **D-10:** Edit surfaces **inline** — clicking "Edit" on a post card replaces it with an editable form in-place. No modal, no separate route.
- **D-11:** Editing updates **only the template field text responses**. The task snapshot is not re-frozen on edit — it stays as the original submit-time snapshot.
- **D-12:** Delete confirmation is **inline**: clicking "Delete" shows Yes/No buttons directly on the card (no modal, no browser confirm dialog).

### Claude's Discretion
- Exact table/column name for the global settings store (e.g., `standup_settings` vs `app_settings`)
- Exact page size for pagination (20 is a suggested default)
- Collapsible-by-default vs always-open form on the /updates page — Claude can decide based on SvelteKit patterns

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Requirements
- `.planning/REQUIREMENTS.md` — UPD-01 through UPD-08 (standup requirements for this phase)

### Architecture Decisions
- `.planning/STATE.md` §Architecture Decisions (Milestone v2.2) — locked model names, JSONB snapshot rationale, Alembic migration constraints, DOMPurify/marked install timing, zero new packages rule

### Backend Patterns
- `backend/app/models/notifications.py` — EventNotification model and pattern for the existing notification/reminder system
- `backend/app/routers/schedules.py` — Existing router pattern (async FastAPI, SQLAlchemy async, Pydantic schemas)
- `backend/app/models/work.py` — Task model (fields: id, title, status, priority, due_date, assignee_id, etc.)
- `backend/app/models/enums.py` — NotificationEventType enum (ALTER TYPE must run outside transaction per STATE.md watch-out #5)
- `backend/app/scheduler_jobs.py` — Existing APScheduler jobs pattern

### Frontend Patterns
- `frontend/src/routes/schedule/+page.svelte` — Existing route page pattern for SvelteKit
- `frontend/src/lib/` — Existing stores, types, components structure

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `EventNotification` table + 60s poll in `routers/notifications.py` — in-app notification delivery (no new infrastructure needed)
- `get_current_user` auth dependency — reuse for all /updates endpoints
- `get_db` async session dependency — standard async SQLAlchemy pattern

### Established Patterns
- Router: async FastAPI with `Depends(get_current_user)` and `Depends(get_db)`, Pydantic response models
- Model: SQLAlchemy declarative base in `app/db/database.py`
- Schema changes: Alembic only (`alembic revision --autogenerate`)
- Frontend: SvelteKit `+page.svelte` per route, `frontend/src/lib/stores/` for reactive state, `frontend/src/lib/apis/` for API calls

### Integration Points
- New route `/updates` added to SvelteKit routes at `frontend/src/routes/updates/`
- New router `routers/updates.py` registered in `backend/app/main.py`
- New models in `backend/app/models/updates.py` (StandupPost, StandupTemplate)
- New schemas in `backend/app/schemas/` (or extend existing updates schema file)
- `marked` + `DOMPurify` frontend packages to be installed in this phase (first `{@html}` usage in the app — always wrap: `DOMPurify.sanitize(marked.parse(raw))`)

</code_context>

<specifics>
## Specific Ideas

- The form should feel lightweight — it's a daily standup, not a project report. The template fields should render as labeled textareas.
- The frozen task snapshot expanding inline (not navigating away) keeps the standup card self-contained.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 23-standup-updates*
*Context gathered: 2026-04-28*
