# Phase 27: Timeline & Gantt Clarity - Context

**Gathered:** 2026-04-29
**Status:** Ready for planning

<domain>
## Phase Boundary

Turn `/timeline` into a milestone-first planning surface with clearer Gantt signals, linked task rollups, derived milestone risk, lightweight decision hints, and preserved context when switching between project-oriented and people-oriented views. This phase clarifies timeline display and interaction. It should not become a workflow-rule editor, full decision-management system, or replacement for the separate `/milestones` command view.

</domain>

<decisions>
## Implementation Decisions

### Milestone-First Layout
- **D-01:** `/timeline` should use milestone parent rows as the dominant planning objects.
- **D-02:** Each milestone parent row should show title, status, date span, and a progress badge.
- **D-03:** Task rows should be expanded by default for active or risky milestones and collapsed by default for quiet milestones.
- **D-04:** Milestone rows should be distinct summary rows, not normal draggable task bars. Task bars remain the editable/draggable work items.

### Task Rollups Inside Milestones
- **D-05:** Collapsed milestone rows should still show a progress badge plus task counts by state.
- **D-06:** Expanded milestone tasks should be grouped by status first, then by due date.
- **D-07:** Task rows should show title, assignee, priority, due date, and status label.
- **D-08:** Clicking a task should keep the existing quick-edit modal behavior.

### Risk, Planning, and Decision Signals
- **D-09:** Milestone risk should be derived from existing data, not new risk persistence. Inputs may include delayed milestone status, overdue milestone dates, blocked tasks, critical tasks, low completion near due date, and relevant custom-status state.
- **D-10:** The milestone planning window should be represented by the milestone `start_date` to `due_date` span.
- **D-11:** Phase 27 may show lightweight placeholder decision markers only when existing milestone text or tags already provide that signal. Explicit decision persistence belongs to Phase 28.
- **D-12:** Risk and decision signals should appear as small badges/icons on milestone rows, keeping the Gantt chart itself readable.

### Project vs People View Continuity
- **D-13:** Switching between By Project and By Member should preserve the selected date range plus the highlighted milestone/task.
- **D-14:** In By Member view, rows should stay people-first; task rows should include milestone badges or links to preserve planning context.
- **D-15:** If the focused milestone is not naturally visible in the current view, show a compact focused-milestone banner.
- **D-16:** Users should create or change focus by clicking a milestone row or task row. Task focus carries its milestone context.

### Folded Todos
- **D-17:** Fold in only the timeline-relevant part of `Status transition graph / workflow rules (YouTrack-style)`: blocked/custom-status state may contribute to milestone risk. The broader graph editor, workflow-rule visualization, and transition-management UI remain outside Phase 27.

### the agent's Discretion
- Exact badge copy, icon choice, color thresholds, empty states, and responsive spacing are left to the planner/implementer, as long as the decisions above and existing TeamFlow visual conventions are preserved.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase Scope And Requirements
- `.planning/ROADMAP.md` — Phase 27 goal, dependencies, success criteria, and relation to Phases 26, 28, and 29.
- `.planning/REQUIREMENTS.md` — TL-01 through TL-05 requirements and milestone-level out-of-scope constraints.
- `.planning/PROJECT.md` — Product context and v2.3 decisions: timeline and milestones are planning surfaces, route URLs stay stable, and current data should be reused where possible.
- `.planning/STATE.md` — Current milestone status, watch-outs, and deferred todo context.

### Timeline Implementation
- `frontend/src/routes/timeline/+page.svelte` — Timeline page state, date-range handling, view toggle, task edit modal, and existing load/reschedule behavior.
- `frontend/src/lib/components/timeline/TimelineGantt.svelte` — Current SvelteGantt row/task construction, project/member view grouping, task click handling, and task visual states.
- `frontend/src/lib/components/timeline/TimelineToolbar.svelte` — Existing By Project/By Member toggle and range selector.
- `frontend/src/lib/apis/timeline.ts` — Current frontend API wrapper for timeline data.
- `backend/app/routers/timeline.py` — Timeline payload construction, project/milestone/task grouping, and current role/sub-team filtering.
- `backend/app/schemas/work.py` — Timeline response schemas plus task, milestone, custom status, and date fields available to the frontend.
- `backend/app/models/work.py` — Project, Milestone, Task, CustomStatus, and StatusTransition model fields relevant to timeline risk and rollups.

### Folded Todo Reference
- `.planning/todos/pending/2026-04-26-status-transition-graph-workflow.md` — Source todo for workflow rules; only blocked/custom-status risk signal is folded into this phase.
- `backend/app/routers/statuses.py` — Existing status-set and transition APIs that may inform custom-status risk signal, without adding workflow management UI here.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `TimelineGantt.svelte` already builds rows and Gantt tasks from `projects`, supports `project` and `member` modes, and styles unscheduled, overdue, and done task bars.
- `TimelineToolbar.svelte` already preserves date-range state at the page level while switching view modes.
- `/api/timeline/` already returns projects with milestones, milestone tasks, unassigned tasks, assignees, milestone dates/status, and task status/priority/due dates.
- The existing task edit modal in `frontend/src/routes/timeline/+page.svelte` can remain the task-click interaction.

### Established Patterns
- Frontend work should stay in SvelteKit with Tailwind utility classes and `lucide-svelte` icons.
- Existing route URLs should remain stable; improve the `/timeline` surface in place.
- Backend API changes should use explicit FastAPI response models and existing Pydantic schema patterns.
- Schema changes, if any become unavoidable, must go through Alembic, but Phase 27 decisions intentionally prefer derived display logic over new persistence.

### Integration Points
- Milestone parent rows and risk badges connect primarily to `TimelineGantt.svelte`.
- Highlight/focus state connects to `frontend/src/routes/timeline/+page.svelte` and should survive view-mode switches.
- Timeline risk calculations can be frontend-derived from the current timeline payload unless planning finds a clear reason to move the calculation server-side.
- Member view should remain organized around users while adding milestone badges/links on task rows.

</code_context>

<specifics>
## Specific Ideas

- Active or risky milestones should open automatically so supervisors see where attention is needed first.
- Quiet milestones can stay collapsed but must still expose progress and task-state counts.
- Decision markers are intentionally lightweight placeholders in this phase; full milestone decision capture and visibility belongs to Phase 28.

</specifics>

<deferred>
## Deferred Ideas

- Workflow-rule graph editor, transition-rule visualization, and YouTrack-style management UI remain deferred to the existing status-transition workflow backlog.
- Explicit milestone decision persistence and richer decision lifecycle handling belong to Phase 28.

</deferred>

---

*Phase: 27-timeline-gantt-clarity*
*Context gathered: 2026-04-29*
