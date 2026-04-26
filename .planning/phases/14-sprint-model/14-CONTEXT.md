# Phase 14: Sprint Model - Context

**Gathered:** 2026-04-26
**Status:** Ready for planning

<domain>
## Phase Boundary

Sprints as time-boxed iterations within milestones; tasks assigned to sprints; sprint board filters by sprint; sprint close flow.

</domain>

<decisions>
## Implementation Decisions

### Sprint Board Layout
- **D-01:** The "Backlog" (unassigned tasks) should be displayed as a fixed column on the far-left of the Kanban board, allowing tasks to be easily dragged out of it.

### Sprint Close Flow
- **D-02:** When closing a sprint, a modal should list incomplete tasks, allowing the user to select the destination (e.g., Backlog or next sprint) on a per-task basis before finalizing the close.

### Date Enforcement
- **D-03:** Sprint dates are enforced loosely: the UI should warn the user if sprint dates overlap or exceed the milestone dates, but it allows creation anyway.

### Hierarchy & Association
- **D-04:** Sprint and Milestone assignments on a task are independent fields. They can mismatch if the user chooses to do so.

### Claude's Discretion
- Exact UI design of the sprint close modal (e.g., layout of the task list and destination dropdowns).
- Visual styling of the overlap/exceed warnings for sprint dates during creation/editing.
- How to ensure the Backlog column integrates smoothly without breaking horizontal scrolling or layout on smaller screens.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Roadmap and Requirements
- `.planning/ROADMAP.md` — Phase 14 goal, success criteria, sequencing, and dependencies.
- `.planning/REQUIREMENTS.md` — `SPRINT-01` through `SPRINT-04` acceptance criteria.
- `.planning/PROJECT.md` — Milestone 2 product framing and active requirements.

### Existing Task and Milestone Implementation
- `backend/app/models.py` — Existing Task and Milestone models to be updated with Sprint relationships.
- `backend/app/schemas.py` — Existing schemas to be updated.
- `backend/app/routers/milestones.py` — Milestone endpoints, to be updated or used as reference for Sprint endpoints.
- `backend/app/routers/tasks.py` — Task endpoints, needing updates to accept and filter by `sprint_id`.

### Frontend Components
- `frontend/src/routes/tasks/+page.svelte` — Main task page, needs Sprint selector and Backlog integration.
- `frontend/src/lib/components/tasks/KanbanBoard.svelte` — Kanban board component, needs a fixed Backlog column added.
- `frontend/src/lib/components/tasks/AiTaskInput.svelte` — AI task input may need updating to understand "sprint" context.
- `frontend/src/lib/api.ts` — API client to add Sprint endpoints.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `frontend/src/lib/components/tasks/KanbanBoard.svelte`: Existing drag-and-drop logic can be extended to support the new fixed Backlog column.
- FastAPI dependency injection and existing router patterns (`backend/app/routers/milestones.py`) can be used to quickly scaffold `sprints.py`.

### Established Patterns
- SQLAlchemy async sessions and Pydantic schemas for data validation.
- Sub-team scoping (from Phase 13) must be applied to Sprints (Sprints belong to Milestones, which belong to Projects, which belong to SubTeams).

### Integration Points
- Add `Sprint` model to `backend/app/models.py` with FK to `Milestone`.
- Add `sprint_id` FK to `Task` model.
- Add `backend/app/routers/sprints.py` for Sprint CRUD operations.
- Update Kanban view to query and filter by `sprint_id`, showing unassigned tasks in the Backlog column.
- Integrate sprint validation warnings (non-blocking) in the frontend forms when date overlaps with other sprints or exceeds milestone dates.

</code_context>

<specifics>
## Specific Ideas

- The Backlog column should be permanently visible on the left side of the Kanban board to make dragging tasks into the active sprint frictionless.
- The Sprint Close modal should clearly list the tasks and provide an easy way to map each to either "Backlog" or another active sprint.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within Phase 14 scope.

</deferred>
