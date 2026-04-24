# Phase 12: Task Types - Context

**Gathered:** 2026-04-24
**Status:** Ready for planning

<domain>
## Phase Boundary

Phase 12 adds a task type field to every task with the values `feature`, `bug`, `task`, and `improvement`. Users can set the type when creating or editing tasks, existing tasks are backfilled to `task`, task cards show the type, and the task board can be filtered by type.

This phase does not introduce custom task types, sprint behavior, custom Kanban statuses, or new KPI views. Those belong to later Milestone 2 phases.

</domain>

<decisions>
## Implementation Decisions

### Type Picker in Create/Edit Flow
- **D-01:** Task type should live next to `status` and `priority` as a third small selector in the create/edit task form.
- **D-02:** The default type is `task` when the user does not choose a type.
- **D-03:** The picker should use the fixed roadmap values: `feature`, `bug`, `task`, and `improvement`.

### Card Display Style
- **D-04:** Task cards should show task type as an icon plus short label badge, such as `Bug` or `Feature`.
- **D-05:** The badge should stay compact enough for Kanban cards and mobile layouts.

### Filter Behavior
- **D-06:** Type filtering should support multi-select so users can show several task types at once.
- **D-07:** Type filtering should apply consistently to the task list, Kanban view, and Agile view rather than only one display mode.
- **D-08:** The type filter should sit alongside the existing task filters and preserve the current task screen's compact control style.

### AI and Autofill Behavior
- **D-09:** AI-created or AI-parsed tasks should suggest a task type, but the user must confirm or edit it before creation.
- **D-10:** If AI cannot infer a sensible type, the suggested/default value should remain `task`.

### the agent's Discretion
- Exact icons and colors for each type badge are left to the planner/implementer, as long as they are readable and consistent with the existing UI.
- Exact multi-select UI control is left to the planner/implementer, as long as it fits the existing task filter bar and works on mobile.
- Migration implementation details are left to the planner/implementer, with the hard requirement that existing tasks end up with non-null `task` type.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Roadmap and Requirements
- `.planning/ROADMAP.md` — Phase 12 goal, success criteria, sequencing, and UI hint.
- `.planning/REQUIREMENTS.md` — `TYPE-01`, `TYPE-02`, and `TYPE-03` requirement definitions.
- `.planning/PROJECT.md` — Milestone 2 product framing and active requirements.

### Existing Task Implementation
- `backend/app/models.py` — Existing `Task` model, task status, priority, timestamps, and relationships.
- `backend/app/schemas.py` — Existing task create/update/output schemas and AI parse response shape.
- `backend/app/routers/tasks.py` — Task list/create/update endpoints and AI parsing/breakdown behavior.
- `frontend/src/routes/tasks/+page.svelte` — Task create/edit modal, filters, list view, and view mode routing.
- `frontend/src/lib/components/tasks/KanbanBoard.svelte` — Kanban grouping and drag/drop task status updates.
- `frontend/src/lib/components/tasks/KanbanCard.svelte` — Existing task card badge area where type badge should fit.
- `frontend/src/lib/components/tasks/AgileView.svelte` — Agile task display and status controls.
- `frontend/src/lib/components/tasks/AiTaskInput.svelte` — AI parse and AI breakdown task creation flow.
- `frontend/src/lib/api.ts` — Existing task API client methods.
- `frontend/src/lib/utils.ts` — Existing status and priority color/label helpers.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `frontend/src/routes/tasks/+page.svelte`: already has a compact filter bar, a create/edit modal, view-mode toggle, and form state for task fields.
- `frontend/src/lib/components/tasks/KanbanCard.svelte`: already has a compact badge row for priority, due date, and tags where the type badge can be added.
- `frontend/src/lib/utils.ts`: already centralizes status and priority labels/colors; task type labels, colors, and icon metadata can follow the same pattern.

### Established Patterns
- Task status and priority are backend enums exposed through Pydantic schemas; task type should follow the same fixed-value pattern unless research/planning finds a strong reason not to.
- Task filtering currently happens through `tasksApi.list(params)` from the task page; type filtering should extend this pattern while supporting multiple selected types.
- Frontend task UI uses compact badges and dark utility classes; avoid introducing a new visual language for type labels.

### Integration Points
- Add type persistence to the `Task` model, Alembic migration, task schemas, task router filters, and task API responses.
- Add type selection to create/edit forms and include it in submit payloads.
- Add type display to list, Kanban, and Agile task presentations.
- Extend AI parse/breakdown response handling so suggested task type can populate the form while staying user-confirmable.

</code_context>

<specifics>
## Specific Ideas

- Type selector belongs beside `status` and `priority`, not hidden in advanced settings.
- Type badge should be icon plus label for readability.
- Type filter should be multi-select because users may want to see, for example, both `bug` and `feature` work together.
- AI may suggest a type, but the user stays in control before the task is created.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within Phase 12 scope.

</deferred>

---

*Phase: 12-task-types*
*Context gathered: 2026-04-24*
