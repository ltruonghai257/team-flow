# Phase 25: Team Weekly Board & AI Summary - Research

**Researched:** 2026-04-28
**Domain:** FastAPI + SQLAlchemy async, APScheduler weekly jobs, LiteLLM-backed summaries, SvelteKit 5 weekly digest UI
**Confidence:** HIGH for data model, AI integration, and scheduler fit; HIGH for frontend route and markdown rendering patterns

---

<user_constraints>
## User Constraints from CONTEXT.md

### Locked Decisions

- **D-01:** Each member has one primary weekly post per ISO week, plus optional follow-up append entries.
- **D-02:** Follow-up entries belong to the author's weekly post model; they are not comments on other members' posts.
- **D-03:** Management users participate by posting their own updates; comments on another member's post are deferred.
- **D-04:** `/board` is summary-first: selected week heading and AI summary at the top, then member posts below.
- **D-05:** The board should feel like a weekly digest, not a reverse-chronological chat feed.
- **D-07:** Week navigation includes previous/current/next plus a compact week picker.
- **D-08:** Current ISO week is the default landing state.
- **D-09:** A persistent AI summary panel appears at the top of the selected week.
- **D-10:** If no summary exists, show a quiet empty state with a summarize action.
- **D-11:** Stored summaries are visible immediately for current and past weeks.
- **D-12:** On-demand regeneration has a locked 30-minute cooldown with visible feedback.
- **D-13:** Regeneration overwrites the stored summary for that ISO week.
- **D-14:** Create/edit uses a markdown textarea with a sanitized preview toggle.
- **D-15:** All rendered markdown must use `DOMPurify.sanitize(marked.parse(raw))` before `{@html}`.
- **D-16:** Preview is toggle-based, not live split-pane.

### Claude's Discretion

- Exact SQLAlchemy naming for board post and append-entry tables.
- Exact ordering for member digest cards within a week.
- Exact week-picker control implementation, provided it stays compact.
- Exact wording for summary cooldown and empty states, within the UI-SPEC contract.

### Deferred Ideas

- Comments/threading on another member's weekly post remain out of scope.
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| BOARD-01 | Any member can post a weekly markdown update | Dedicated `WeeklyPost` model, `/api/board` create/update/delete endpoints, `/board` composer |
| BOARD-02 | Board groups posts by ISO week; users can navigate past weeks | Store ISO year/week in persistence, route payload keyed by week, compact week navigator |
| BOARD-03 | Markdown is rendered safely | Frontend render helper must always use `marked` + `DOMPurify` before `{@html}` |
| BOARD-04 | Any member can trigger on-demand AI summary for current week | Summary service callable from a board router action using `app.utils.ai_client.acompletion` |
| BOARD-05 | Automatic Sunday 23:00 weekly summary via APScheduler CronTrigger | New scheduler job in `backend/app/internal/scheduler_jobs.py` |
| BOARD-06 | Summary is stored/cached; on-demand re-click within 30 minutes returns cached result | `WeeklyBoardSummary` model with `generated_at` and cooldown logic |
| BOARD-07 | Member can edit their own weekly post | Ownership-checked PATCH for primary posts and append entries |
| BOARD-08 | Member can delete their own weekly post | Ownership-checked DELETE for primary posts and append entries |
</phase_requirements>

---

## Summary

Phase 25 should introduce a dedicated board domain rather than stretching the standup or chat features. The closest existing pattern is `/updates`: same-page compose, author-only edit/delete, and compact feed cards. The two major differences are week-based grouping and the persisted AI summary layer.

The clean backend split is:

1. Persistence and schemas for `WeeklyPost`, append entries, and `WeeklyBoardSummary`
2. Board router/service for week payloads, author CRUD, and summary cooldown behavior
3. Shared summary-generation helper used by both the on-demand endpoint and the scheduled Sunday job
4. `/board` frontend route with week navigation, summary-first layout, sanitized markdown preview, and append-entry UI

The current app already has the pieces this phase needs:

- AI generation via `backend/app/routers/ai.py` and `app.utils.ai_client.acompletion`
- APScheduler startup in `backend/app/internal/scheduler_jobs.py`
- Auth/sub-team scoping and author ownership patterns in `backend/app/routers/updates.py`
- Installed `marked` and `dompurify` for safe markdown rendering on the frontend

The main architectural risk is mixing concerns: if summary generation, week grouping, and append-entry behavior are all shoved into a single giant route/page, Phase 25 becomes hard to execute safely. Splitting the work into model/schema, board behavior, summary automation, and frontend digest UI keeps the plans testable.

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|--------------|----------------|-----------|
| Week grouping and scope | Backend | Frontend navigator labels | Week selection is a query concern; visibility remains server authoritative |
| Author ownership for edit/delete | Backend | Frontend conditional buttons | UI hides controls, backend enforces them |
| Markdown sanitization | Frontend | Backend stores raw text only | Rendering risk is at display time |
| Summary cooldown and caching | Backend | Frontend displays remaining time | Cooldown must not depend on client clocks |
| AI summary generation | Backend service | Scheduler and router callers | One shared generation path prevents drift |
| Sunday auto-summary | Scheduler | Shared summary service | Existing APScheduler bootstrap is the right integration point |
| Append-entry interaction | Frontend | Backend storage | UI owns collapsed/inline interaction; backend owns author rules |

---

## Recommended Project Structure

```text
backend/app/
├── models/
│   ├── board.py
│   └── __init__.py
├── schemas/
│   ├── board.py
│   └── __init__.py
├── routers/
│   ├── board.py
│   └── updates.py               # unchanged reference pattern only
├── services/
│   └── weekly_board.py
└── internal/
    └── scheduler_jobs.py

frontend/src/
├── lib/apis/
│   ├── board.ts
│   └── index.ts
├── lib/stores/
│   └── board.ts
├── lib/components/board/
│   ├── WeeklySummaryPanel.svelte
│   ├── WeeklyPostComposer.svelte
│   ├── WeeklyPostCard.svelte
│   ├── AppendEntryComposer.svelte
│   └── WeekNavigator.svelte
├── routes/
│   ├── +layout.svelte
│   └── board/+page.svelte
```

---

## Implementation Patterns

### Pattern 1: Separate primary posts, append entries, and summaries

Use three persistence units:

- `WeeklyPost` for the member's primary post for a week
- `WeeklyPostAppend` for follow-up notes under that primary post
- `WeeklyBoardSummary` for the generated summary per team/week

This keeps:

- one-primary-post-per-member-per-week enforceable with a unique constraint
- append entries lightweight and chronologically nested
- summary lifecycle independent from post editing

### Pattern 2: ISO week persistence

Store normalized week identity directly on rows instead of recomputing it only at query time. Recommended fields:

- `iso_year`
- `iso_week`
- `week_start_date`

This makes:

- filtering deterministic
- scheduler targeting straightforward
- historical navigation cheap

### Pattern 3: summary generation as a shared backend service

Do not put all summary logic directly in the router or scheduler job. A shared service should:

- load all primary posts and append entries for the requested week/scope
- short-circuit to `"No updates this week"` when empty
- build a constrained prompt from the stored content only
- call `acompletion(...)`
- upsert `WeeklyBoardSummary`
- enforce cooldown checks for on-demand requests

This same service can be used by:

- `POST /api/board/weeks/{year}/{week}/summary`
- the Sunday 23:00 scheduler job

### Pattern 4: board payload shaped around a week digest

The frontend should not have to fan out multiple calls for a single week view. The main week payload should include:

- selected week metadata
- available historical week options
- current user's primary post for that week if present
- all visible member posts with nested append entries
- stored summary and cooldown metadata

That keeps the route page simple and aligned with the summary-first UI.

### Pattern 5: follow-up entries are not comments

Append entries should:

- be creatable only by the owner of the parent weekly post
- render nested below that user's primary post
- reuse the same markdown sanitization path
- be disallowed for past weeks

This preserves the digest model from CONTEXT.md and avoids drifting into threaded discussion behavior.

---

## Build Order

1. **Backend data contract**
   - Add board models, schemas, exports, and Alembic migration.
   - Lock the unique constraints and summary table shape early.

2. **Board CRUD and week payload**
   - Add router/service for loading a week, creating/updating/deleting posts, and append entries.
   - Add author-ownership tests.

3. **Summary generation and automation**
   - Add reusable summary service, on-demand summary endpoint, cooldown logic, Sunday CronTrigger job, and scheduler-focused tests.

4. **Frontend digest experience**
   - Add board API/store, nav link, `/board` route, summary panel, composer, cards, append UI, and build/manual verification.

---

## Common Pitfalls

### Pitfall 1: Reusing standup templates or standup models

Weekly board posts are markdown digest content, not structured template-field posts. Reusing `StandupPost` would fight both requirements and UI-SPEC.

### Pitfall 2: Relying on client-side cooldown

The 30-minute summary cooldown must be computed server-side from persisted summary timestamps. A disabled button alone is not enough.

### Pitfall 3: Calling the AI when there are no posts

State and success criteria explicitly require the `"No updates this week"` short-circuit. Empty weeks should never hit the AI client.

### Pitfall 4: Unscoped summary generation

The app is team-scoped. Summary queries must use the same team/sub-team scope rules as the board posts; otherwise admin context and member context can drift.

### Pitfall 5: Unsafe markdown preview

Raw `marked.parse(...)` without `DOMPurify.sanitize(...)` would violate a locked decision and create stored-XSS risk.

### Pitfall 6: Past-week mutation leakage

The route should allow historical viewing but not historical editing/append creation. This should be enforced in both UI and backend.

---

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Backend framework | pytest with httpx AsyncClient |
| Backend quick command | `cd backend && rtk pytest tests/test_board.py -q` |
| Backend broader command | `cd backend && rtk pytest tests/test_board.py tests/test_notifications.py -q` |
| Frontend commands | `cd frontend && rtk bun run check` and `cd frontend && rtk bun run build` |
| Manual check | Browser walkthrough of `/board` for current and past weeks |

### Phase Requirements to Test Map

| Req ID | Behavior | Test Type | Target |
|--------|----------|-----------|--------|
| BOARD-01 | Member creates current-week markdown post and sees it in response payload | integration | `backend/tests/test_board.py` |
| BOARD-02 | Week queries return grouped historical content by ISO week | integration | `backend/tests/test_board.py` |
| BOARD-03 | Frontend preview/render path sanitizes markdown before `{@html}` | build + manual | `/board` components |
| BOARD-04 | On-demand summary generates once and returns cached content inside cooldown window | integration | `backend/tests/test_board.py` |
| BOARD-05 | Sunday scheduler job upserts summaries and skips AI on empty weeks | integration/unit | `backend/tests/test_board.py` |
| BOARD-06 | Stored summary is overwritten after cooldown or scheduled regeneration | integration | `backend/tests/test_board.py` |
| BOARD-07 | Author can edit own primary post and append entries only | integration | `backend/tests/test_board.py` |
| BOARD-08 | Non-author cannot delete another member's post or append entry | integration | `backend/tests/test_board.py` |

---

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|------------------|
| V2 Authentication | Yes | All board endpoints use `Depends(get_current_user)` |
| V4 Access Control | Yes | Author-only mutations, scoped week queries |
| V5 Input Validation | Yes | Pydantic schemas validate week identity and payload shape |
| V7 Error Handling | Yes | Hidden or unauthorized resources return 403/404 without cross-team leakage |

### STRIDE Threat Register

| Threat ID | Category | Component | Mitigation |
|-----------|----------|-----------|------------|
| T-25-01 | Information Disclosure | Week payload and stored summaries | Filter by allowed team scope before building post and summary payloads |
| T-25-02 | Tampering | Post and append-entry edit/delete | Enforce author ownership on every mutation |
| T-25-03 | Stored XSS | Markdown rendering | Always sanitize rendered markdown with DOMPurify |
| T-25-04 | Abuse / Cost | Repeated on-demand summary generation | Enforce 30-minute cooldown server-side |
| T-25-05 | Integrity | Weekly summary content | Build prompts from stored post text only and short-circuit empty weeks |

---

## Sources

### Primary

- `.planning/phases/25-team-weekly-board-ai-summary/25-CONTEXT.md`
- `.planning/phases/25-team-weekly-board-ai-summary/25-UI-SPEC.md`
- `.planning/REQUIREMENTS.md`
- `.planning/ROADMAP.md`
- `.planning/STATE.md`
- `backend/app/routers/updates.py`
- `backend/app/routers/ai.py`
- `backend/app/internal/scheduler_jobs.py`
- `backend/app/utils/ai_client.py`
- `backend/app/models/knowledge.py`
- `backend/app/models/notifications.py`
- `backend/app/services/reminder_notifications.py`
- `frontend/src/routes/updates/+page.svelte`
- `frontend/src/lib/components/updates/StandupCard.svelte`
- `frontend/src/lib/apis/updates.ts`
- `frontend/src/lib/stores/updates.ts`
- `frontend/src/routes/+layout.svelte`

### Secondary

- `.planning/phases/24-knowledge-sharing-scheduler/24-CONTEXT.md`
- `.planning/phases/24-knowledge-sharing-scheduler/24-01-PLAN.md`
- `.planning/phases/24-knowledge-sharing-scheduler/24-02-PLAN.md`
- `.planning/phases/24-knowledge-sharing-scheduler/24-03-PLAN.md`

---

## Metadata

**Confidence breakdown:**

- Data model and ownership rules: HIGH
- Summary-generation integration with existing AI client: HIGH
- Scheduler fit for Sunday CronTrigger: HIGH
- Frontend digest layout and nav integration: HIGH

**Research date:** 2026-04-28
**Valid until:** 2026-05-28

## RESEARCH COMPLETE
