# Phase 28: Milestone Planning & Decisions - Context

**Gathered:** 2026-04-29
**Status:** Ready for planning

<domain>
## Phase Boundary

Improve `/milestones` into a clearer command view for milestone planning state, decision visibility, and related work. This phase should make planned, committed, active, completed, risky, and decision-heavy milestones easier to scan while keeping the existing `/milestones` route and reusing current milestone/task data wherever possible. New persistence is justified only for structured milestone decisions, because current milestone/task fields cannot represent those cleanly.

</domain>

<decisions>
## Implementation Decisions

### Planning State Signal
- **D-01:** Milestone planning state should be derived from existing data, not stored as a new manual planning-state field.
- **D-02:** A milestone counts as `committed` when it has schedule dates plus at least one linked task.
- **D-03:** A milestone counts as `active` when the existing milestone status is `in_progress`.
- **D-04:** Risk should be an overlay on top of the main planning state, not a separate top-level lane. For example, an active milestone can also show `at risk` or `delayed`.
- **D-05:** Users should not be able to manually override the derived planning state in Phase 28. They should edit the underlying milestone or task data instead.

### Milestone Detail With Linked Tasks
- **D-06:** Linked tasks should appear inside expandable milestone cards on `/milestones`.
- **D-07:** Collapsed milestone cards should still show task counts by state plus a progress summary, such as total tasks, done count, blocked count, and completion percentage.
- **D-08:** Expanded task lists should group tasks by status first, then by due date.
- **D-09:** Task rows in milestone details should open or link into the existing task detail/edit flow. Phase 28 should not duplicate inline task editing inside milestone cards.
- **D-10:** Milestone detail should show only tasks already linked to that milestone. Suggested linking of unassigned or date-matching project tasks is out of scope.

### Decision Visibility
- **D-11:** Milestone decisions should use structured decision entries, not milestone description text or task tags.
- **D-12:** Decision entries should support `proposed`, `approved`, `rejected`, and `superseded` statuses.
- **D-13:** These statuses are visible decision states only. Phase 28 should not build sign-off routing, approval assignment, or a full decision workflow.
- **D-14:** Each milestone decision should include a title, status, note, created date, and optional linked task.
- **D-15:** Collapsed milestone cards should show decision counts by status. Expanded milestone cards should show full decision entries.
- **D-16:** Users should be able to create, edit, and delete milestone decisions inside milestone details.

### Command-View Layout
- **D-17:** `/milestones` should organize milestones into planning-state lanes: `Planned`, `Committed`, `Active`, and `Completed`.
- **D-18:** Milestones within each lane should order by risk first, then nearest due date.
- **D-19:** Active and risky milestones should be expanded by default.
- **D-20:** The page should include a compact summary metrics row above the lanes, such as active milestones, risky milestones, proposed decisions, and blocked tasks.
- **D-21:** On mobile, planning-state lanes should stack as collapsible sections rather than switching to a different information model.

### the agent's Discretion
- Exact badge copy, risk thresholds, icon choices, responsive spacing, empty states, and the visual treatment of decision/status counts are left to the planner and implementer, as long as the decisions above and existing TeamFlow visual conventions are preserved.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase Scope And Requirements
- `.planning/ROADMAP.md` — Phase 28 goal, dependencies, success criteria, and relation to Phases 27 and 29.
- `.planning/REQUIREMENTS.md` — ML-01 through ML-04 requirements and v2.3 out-of-scope constraints.
- `.planning/PROJECT.md` — Product context and v2.3 decision that timeline and milestones are planning surfaces while route URLs stay stable.
- `.planning/STATE.md` — Current milestone status, watch-outs, and deferred todo context.
- `.planning/phases/27-timeline-gantt-clarity/27-CONTEXT.md` — Carry-forward decision that Phase 27 may show lightweight decision hints only, while explicit milestone decision persistence belongs to Phase 28.

### Milestone Implementation
- `frontend/src/routes/milestones/+page.svelte` — Current milestone page state, route highlighting, CRUD modal, due-date ordering, status badge, and time-elapsed progress bar.
- `frontend/src/lib/apis/milestones.ts` — Current frontend milestone API wrapper.
- `backend/app/routers/milestones.py` — Current milestone list/get/create/update/delete endpoints and reminder rebuild behavior.
- `backend/app/models/work.py` — Project, Milestone, Task, CustomStatus, and relationship fields used for planning-state derivation, linked task rollups, and new decision persistence.
- `backend/app/schemas/work.py` — Existing milestone, task, and timeline response schema patterns to extend for Phase 28.
- `frontend/src/lib/utils.ts` — Existing milestone status colors, task status labels, priority colors, date formatting, and overdue helpers.

### Related Task And Timeline Patterns
- `backend/app/routers/tasks.py` — Existing task filters, milestone_id support, task detail/update endpoints, custom status resolution, and transition enforcement.
- `frontend/src/routes/tasks/+page.svelte` — Existing task detail/edit flow that milestone task rows should open or link into.
- `backend/app/routers/timeline.py` — Existing example of returning milestone-task rollups from backend data.
- `frontend/src/lib/components/timeline/TimelineGantt.svelte` — Existing milestone/task visual grouping and task click behavior for planning surfaces.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `frontend/src/routes/milestones/+page.svelte` already supports loading milestones/projects, route-based highlighting from `milestone_id`, create/edit/delete modal behavior, status badges, due dates, and a progress bar.
- `backend/app/routers/milestones.py` already owns milestone CRUD and reminder rebuilds when due dates change.
- `Task.milestone_id` already links tasks to milestones, and `tasksApi.get` / existing route query behavior can support opening linked task details rather than duplicating task editing.
- `TimelineMilestoneOut` and `backend/app/routers/timeline.py` already demonstrate milestone payloads with nested tasks.

### Established Patterns
- Frontend work should stay in SvelteKit with Tailwind utility classes and `lucide-svelte` icons.
- Backend API additions should use explicit FastAPI `response_model` schemas and existing Pydantic model patterns.
- Schema changes must go through Alembic migrations.
- Existing route URLs should remain stable; improve `/milestones` in place.

### Integration Points
- Planning-state derivation connects to milestone status/dates plus linked task counts.
- Decision persistence likely connects to a new milestone-owned model/table because existing milestone description, task tags, and task types cannot cleanly represent structured decisions.
- The milestone list endpoint likely needs an enriched response contract for linked task rollups, decision counts, risk overlay inputs, and summary metrics.
- Task rows should link to or reuse the existing task detail/edit route behavior rather than implementing full inline task editing on `/milestones`.

</code_context>

<specifics>
## Specific Ideas

- The command view should make `Planned`, `Committed`, `Active`, and `Completed` visible as first-class lanes.
- Risk remains an overlay so delayed or blocked work is visible without creating a fifth primary planning category.
- Collapsed cards should still carry enough signal for scanning: task counts, task progress, risk, and decision counts.
- Expanded cards should be the place for detailed linked tasks and decision CRUD.
- Mobile keeps the same planning-state mental model through stacked collapsible lane sections.

</specifics>

<deferred>
## Deferred Ideas

- Manual planning-state override is deferred unless future use proves the derived model too rigid.
- Suggested task linking from unassigned or date-matching project tasks is out of scope for Phase 28.
- Inline task status changes or full task editing inside milestone cards is out of scope for Phase 28.
- Approval routing, sign-off ownership, and formal decision workflow automation are out of scope for Phase 28.

### Reviewed Todos (not folded)
- `2026-04-26-status-transition-graph-workflow.md` — Reviewed because it matched milestone/task/status keywords, but deferred. The broader status-transition graph and YouTrack-style workflow management work belongs outside Phase 28; this phase only needs current task state/risk signals as inputs to milestone planning display.

</deferred>

---

*Phase: 28-milestone-planning-decisions*
*Context gathered: 2026-04-29*
