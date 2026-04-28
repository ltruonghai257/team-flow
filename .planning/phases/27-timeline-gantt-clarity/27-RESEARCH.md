# Phase 27: Timeline & Gantt Clarity - Research

**Date:** 2026-04-29
**Scope:** Existing TeamFlow timeline backend, Svelte timeline UI, and current test/tooling setup
**Research depth:** Level 0 - codebase pattern audit

## Summary

Phase 27 does not need external library or product research. The existing codebase already contains the right primitives: milestone and task data in the backend, a `svelte-gantt` timeline surface on the frontend, and targeted backend/Playwright test infrastructure. The main planning decision is where to draw the line between richer API payloads and frontend-derived milestone view models.

## Current Code Findings

### Timeline Page Baseline
- `frontend/src/routes/timeline/+page.svelte` currently owns the timeline page state, date-range controls, task edit modal, and reload-after-reschedule flow.
- Date range already survives project/member view toggles because it lives at the page level.
- Focus state does not exist yet, so there is nothing preserving milestone/task context across view switches.

### Gantt Rendering Capabilities
- `frontend/src/lib/components/timeline/TimelineGantt.svelte` currently renders a flat row list: project rows, milestone label rows, and task bars.
- Milestone rows are labels only; they are not distinct planning objects and do not expose progress, task counts, risk, or decision signal.
- The existing `svelte-gantt` package supports tree rows via `children`, default expansion via `expanded`, and rich row headers via `headerHtml`, so milestone-first parent rows can be implemented without replacing the library.

### Timeline Data Contract
- `backend/app/routers/timeline.py` already groups tasks by milestone and keeps unassigned tasks separate.
- The current response omits milestone description/completed state and most task metadata needed for derived risk and decision signals.
- `backend/app/schemas/work.py` already has `TaskOut` and `CustomStatusOut` patterns that can be reused for a richer timeline-specific schema without introducing new persistence.

### Existing Model Inputs For Derived Signals
- `Milestone` already stores `title`, `description`, `status`, `start_date`, `due_date`, and `completed_at`.
- `Task` already stores `status`, `priority`, `due_date`, `tags`, and `custom_status_id`.
- `CustomStatus` already stores `name`, `slug`, `color`, and `is_done`, which is enough to derive blocked/custom-status risk signal without adding workflow-rule UI in this phase.

### Test And Tooling Baseline
- `backend/tests/test_timeline.py` already exists as a stub and is the natural home for timeline API contract and visibility assertions.
- The frontend has `bun run check`, `bun run build`, and Playwright coverage via `bunx playwright test ...`.
- There is no dedicated timeline UI regression spec yet, so Phase 27 needs a targeted Playwright test instead of assuming coverage from the broad demo suites.

## Planning Implications

1. Enrich the `/api/timeline` payload just enough to expose milestone/task fields already present in the database, then derive progress, risk, expansion defaults, and lightweight decision markers on the frontend.
2. Keep the milestone-first interaction centered in `TimelineGantt.svelte` and the page-level focus/range state in `frontend/src/routes/timeline/+page.svelte` so the current task modal and reload behavior stay intact.
3. Use `svelte-gantt` tree rows and `headerHtml` for milestone parent rows instead of replacing the chart library or introducing a separate planning surface.
4. Add targeted backend API coverage plus a new Playwright timeline regression spec; there is no existing timeline-specific safety net strong enough for this phase.

## Constraints

- Keep the public `/timeline` route and existing project/member toggle labels unchanged.
- Keep task click -> edit modal behavior intact.
- Keep task drag-to-reschedule behavior intact for task bars only; milestone parent rows must remain non-draggable.
- Reuse existing milestone, task, and custom-status data before adding any new tables or stored risk/decision state.
- By Member view must remain people-first even after milestone context is added.

## Recommendation

Plan the phase in three steps:
1. Expand the timeline API contract and typed frontend data model
2. Rebuild the timeline UI around milestone-first parent rows and focus continuity
3. Add targeted regression coverage and run release verification
