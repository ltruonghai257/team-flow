# Phase 28: Milestone Planning & Decisions - Research

**Date:** 2026-04-29
**Scope:** Existing TeamFlow milestone backend, milestone page UI, task links, timeline rollup patterns, and test/tooling setup
**Research depth:** Level 0 - codebase pattern audit

## Summary

Phase 28 should reuse the existing milestone, task, project, and custom-status models for planning-state and risk signals. The one justified persistence addition is structured milestone decisions, because current milestone description text, task tags, and task state cannot represent titled decision entries with visible lifecycle states and optional linked tasks.

The likely implementation should split into three waves: first backend decision persistence and enriched milestone response contracts, then the `/milestones` command-view UI, then targeted backend and Playwright coverage.

## Current Code Findings

### Milestone Page Baseline

- `frontend/src/routes/milestones/+page.svelte` already loads milestones and projects, supports create/edit/delete milestone modal behavior, highlights a `milestone_id` query param, shows due date/project/status, and renders a time-elapsed bar.
- The page currently renders one flat milestone list ordered by backend due date. It does not expose planning-state lanes, linked tasks, task rollups, decision counts, or expanded milestone detail.
- The current page uses SvelteKit, Tailwind utilities, `lucide-svelte`, `toast`, and local helper utilities from `frontend/src/lib/utils.ts`. Phase 28 should keep that pattern.

### Milestone API Baseline

- `backend/app/routers/milestones.py` currently provides list/get/create/update/delete for `Milestone` with optional `project_id` filtering and reminder rebuilds when milestone due dates change.
- The current milestone response model is `MilestoneOut`, which contains milestone fields only. It does not include linked tasks, task rollups, decision counts, derived planning state, risk overlay fields, or summary metrics.
- `Task.milestone_id` already provides the link needed for milestone detail task lists. `tasks.py` already exposes milestone filtering and task detail/update endpoints, so Phase 28 should not duplicate inline task editing inside the milestone surface.

### Existing Model Inputs For Derived Signals

- `Milestone.status`, `start_date`, `due_date`, and `completed_at` are enough to derive active/completed status and schedule presence.
- A milestone can be considered committed when it has schedule dates plus at least one linked task, per Phase 28 context D-02.
- `Task.status`, `Task.priority`, `Task.due_date`, `Task.custom_status_id`, and `CustomStatus.is_done` provide enough data to derive task counts, completion percentage, blocked counts, and risk overlay.
- `backend/app/routers/timeline.py` already demonstrates nested milestone-task response construction with `selectinload`, and can be used as the closest backend payload pattern.

### Decision Persistence Gap

- Current milestone description text is unstructured and cannot support `proposed`, `approved`, `rejected`, and `superseded` decision counts or entries.
- Task tags are task-owned and cannot cleanly represent milestone-level decisions, optional task links, notes, and lifecycle states.
- Phase 28 therefore needs a milestone-owned decision table/model with title, status, note, created date, optional linked task, and relationship back to `Milestone`.

### UI Integration Pattern

- `/tasks` already supports route-driven selection via `task_id`, and milestone task rows can link to `/tasks?task_id={id}` instead of implementing full inline task editing.
- `/timeline` Phase 27 work provides the closest product pattern for milestone rollups, status grouping, risk signal, and linked task context.
- Mobile should keep the same lane model by stacking collapsible lane sections instead of switching to a different information model.

### Test And Tooling Baseline

- There is no dedicated milestone backend test file today. Phase 28 should add `backend/tests/test_milestones.py` to cover milestone decision CRUD, enriched milestone list shape, linked task rollups, decision counts, and role/sub-team filtering behavior inherited from project/task data.
- Frontend has existing Playwright structure in `frontend/tests/timeline-gantt.spec.ts`; Phase 28 should add a targeted `frontend/tests/milestones.spec.ts` with mocked API responses for lanes, expansion, task links, and decision CRUD controls.
- Verification should use focused commands first: `rtk uv run pytest backend/tests/test_milestones.py -q` from repo root if the project runner supports that shape, or `cd backend && rtk uv run pytest tests/test_milestones.py -q`; frontend checks should use Bun per project preference.

## Planning Implications

1. Add structured milestone-decision persistence first, including enum/status constraints, schemas, API endpoints, and backend tests.
2. Enrich the milestone list/get contract to include derived planning state, risk overlay, linked task rollups, grouped task detail, decision counts, and summary metrics without adding a stored planning-state field.
3. Rebuild `/milestones` around summary metrics and planning-state lanes: Planned, Committed, Active, Completed.
4. Keep task rows as links into the existing task detail/edit flow, using `/tasks?task_id={id}`.
5. Add Playwright coverage with API mocks before relying on the new command-view interaction.

## Constraints

- Do not add a manual milestone planning-state field in Phase 28.
- Do not add suggested task linking, date-matching suggestions, or inline task editing inside milestone cards.
- Do not build approval routing, sign-off assignment, or a full decision workflow.
- All schema changes must go through Alembic.
- Keep the public `/milestones` route stable.
- Preserve existing milestone reminder rebuild behavior when due dates change.

## Validation Architecture

Phase 28 has both backend contract risk and UI regression risk, so validation should combine focused API tests with browser-level command-view checks.

- Backend quick check: `cd backend && rtk uv run pytest tests/test_milestones.py -q`
- Backend regression check: `cd backend && rtk uv run pytest tests/test_milestones.py tests/test_timeline.py tests/test_tasks.py -q`
- Frontend quick check: `cd frontend && bun run check`
- Frontend browser check: `cd frontend && bun x playwright test tests/milestones.spec.ts --workers=1`
- Full phase check: run the backend regression check plus frontend check and milestone Playwright spec.

## Recommendation

Plan the phase in four executable plans:

1. Add milestone decision persistence, schemas, API endpoints, and backend CRUD coverage.
2. Enrich milestone API responses with derived planning state, task rollups, risk overlay, decision counts, and summary metrics.
3. Rebuild `/milestones` into the command-view UI with lanes, expandable cards, linked task rows, and decision CRUD controls.
4. Add targeted frontend Playwright coverage and final regression verification.
