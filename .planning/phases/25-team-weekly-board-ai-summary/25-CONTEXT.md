# Phase 25: Team Weekly Board & AI Summary - Context

**Gathered:** 2026-04-28
**Status:** Ready for planning

<domain>
## Phase Boundary

Any team member can post markdown updates to a shared `/board` page organized by ISO week. The board shows stored weekly posts, supports safe markdown rendering, allows authors to edit/delete their own content, and provides an AI-generated weekly summary both on demand and automatically at Sunday 23:00.

</domain>

<decisions>
## Implementation Decisions

### Posting Model
- **D-01:** Each member has one primary weekly post per ISO week, plus optional short follow-up append entries for that same week.
- **D-02:** Follow-up append entries are part of the weekly board post model, not comments on other members' posts.
- **D-03:** Management users participate in this phase by writing their own weekly post and follow-up append entries; direct comments on another member's post are deferred.

### Board Layout
- **D-04:** `/board` uses a summary-first week view: selected week header and AI summary at the top, then each member's primary post with its follow-up append entries below.
- **D-05:** The board should read like a weekly team digest rather than a reverse-chronological chat feed.
- **D-06:** Mobile layout stacks the same sections vertically; desktop can use a constrained single-column digest or light two-zone layout only if it stays consistent with existing TeamFlow pages.

### Week Navigation
- **D-07:** Week navigation includes previous/current/next controls plus a compact week picker for jumping to older ISO weeks.
- **D-08:** The current week should remain the default landing state.

### AI Summary Experience
- **D-09:** A persistent AI summary panel appears at the top of the selected week.
- **D-10:** If no stored summary exists, the summary panel shows a quiet empty state with a `Summarize this week` action.
- **D-11:** If a stored summary exists, it is visible immediately for current and past weeks.
- **D-12:** On-demand regeneration respects the locked 30-minute cooldown; while blocked, the UI shows the stored summary and disables regeneration with clear cooldown feedback.
- **D-13:** Regeneration overwrites the stored weekly summary for that ISO week.

### Markdown Authoring
- **D-14:** Create/edit uses a markdown textarea with a sanitized preview toggle.
- **D-15:** Rendered markdown must always go through `DOMPurify.sanitize(marked.parse(raw))` before any `{@html}` usage.
- **D-16:** Live split preview is not required for this phase; the toggle is enough to verify formatting without adding mobile layout weight.

### Codex's Discretion
- Exact naming for append-entry tables/schemas/endpoints.
- Exact wording for empty summary and cooldown text.
- Exact compact week-picker UI, as long as it supports ISO week navigation and stays lightweight.
- Exact ordering of members/posts within the selected week, with a preference for readable digest order over noisy event-stream ordering.

</decisions>

<specifics>
## Specific Ideas

- The board should feel like a team weekly digest, not another chat surface.
- Management-team comments were raised during discussion, but for Phase 25 that intent should be served through management users' own weekly posts and follow-up entries.
- Markdown authoring should stay useful without becoming a full editor.

</specifics>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Roadmap and Requirements
- `.planning/ROADMAP.md` - Phase 25 goal, dependency on Phase 24, and success criteria for weekly board, ISO week navigation, AI summary, and author edit/delete behavior.
- `.planning/PROJECT.md` - Milestone v2.2 framing for Team Weekly Board as a shared markdown space with AI-generated summaries.
- `.planning/REQUIREMENTS.md` - BOARD-01 through BOARD-08, including markdown safety, on-demand summary, scheduled summary, cached summary, cooldown, and author-only edit/delete.
- `.planning/STATE.md` - Locked v2.2 architecture decisions for `WeeklyPost`, `WeeklyBoardSummary`, `/board`, `marked` + `DOMPurify`, 30-minute cooldown, Sunday 23:00 APScheduler job, and AI client reuse.

### Prior Phase Context
- `.planning/phases/23-standup-updates/23-CONTEXT.md` - Same-page compose/feed pattern, author edit/delete expectations, and v2.2 feature-domain structure.
- `.planning/phases/24-knowledge-sharing-scheduler/24-CONTEXT.md` - Recent scheduler/notification decisions and phase dependency context.

### Backend Integration Points
- `backend/app/routers/ai.py` - Existing AI summary endpoint and prompt pattern using `app.utils.ai_client.acompletion`.
- `backend/app/utils/ai_client.py` - Canonical AI client helper.
- `backend/app/internal/scheduler_jobs.py` - APScheduler setup where the Sunday 23:00 weekly summary job should integrate.
- `backend/app/api/main.py` - Router registration pattern.
- `backend/app/models/updates.py` - Recent v2.2 model style for team-scoped user-authored posts.
- `backend/app/routers/updates.py` - Recent v2.2 route style for list/create/update/delete with author ownership.
- `backend/app/schemas/updates.py` - Recent schema style for user-authored update payloads and responses.

### Frontend Integration Points
- `frontend/src/routes/updates/+page.svelte` - Existing same-page compose and card feed pattern to adapt carefully for `/board`.
- `frontend/src/lib/components/updates/StandupCard.svelte` - Existing author-only edit/delete and inline confirmation behavior.
- `frontend/src/lib/apis/updates.ts` - API module shape for a new board API module.
- `frontend/src/lib/stores/updates.ts` - Store pattern for v2.2 feed data.
- `frontend/src/routes/+layout.svelte` - Sidebar navigation location for adding `/board`.
- `frontend/package.json` - Confirms `marked` and `dompurify` are already installed.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `/updates` provides a close frontend pattern for authenticated team posts, same-page creation, author-only edit/delete, and load states.
- `backend/app/routers/updates.py` provides backend patterns for user-authored posts, sub-team context, cursor-style listing, and author ownership checks.
- `backend/app/routers/ai.py` provides a concrete AI summary pattern with low-temperature generation and strict "do not invent information" style prompting.
- `backend/app/internal/scheduler_jobs.py` already owns APScheduler startup and recurring jobs.
- `marked` and `DOMPurify` are already present in frontend dependencies.

### Established Patterns
- New feature domains use dedicated routers, schemas, API modules, and route pages.
- Backend mutations enforce ownership in the router.
- Frontend uses SvelteKit route pages, `$lib/apis/*` wrappers, writable stores when state needs reuse, `svelte-sonner` toasts, and Tailwind utility classes.
- The app favors quiet, dense operational layouts over decorative pages.

### Integration Points
- New backend domain likely introduces `backend/app/models/board.py`, `backend/app/schemas/board.py`, `backend/app/routers/board.py`, and service helpers for AI summary generation.
- New frontend domain likely introduces `frontend/src/routes/board/+page.svelte`, `frontend/src/lib/apis/board.ts`, and board-specific components if the page gets too large.
- Scheduler integration should add a Sunday 23:00 CronTrigger job without disrupting existing notification jobs.
- Navigation should add a `/board` sidebar item near `/updates` because both are team update surfaces.

</code_context>

<deferred>
## Deferred Ideas

- Management comments on another member's board post - future phase. This would add a comment/threading capability explicitly deferred from v2.2 because it overlaps with chat.

</deferred>

---

*Phase: 25-team-weekly-board-ai-summary*
*Context gathered: 2026-04-28*
