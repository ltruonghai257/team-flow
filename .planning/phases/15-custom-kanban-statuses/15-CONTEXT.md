# Phase 15: Custom Kanban Statuses - Context

**Gathered:** 2026-04-26
**Status:** Ready for planning

<domain>
## Phase Boundary

Kanban columns are driven by database-stored statuses instead of hardcoded enum values. Supervisors/admins can create, reorder, archive/delete, and manage sub-team default statuses and per-project overrides. Task completion is determined by `is_done`, while the existing `tasks.status` enum remains during the dual-write transition.

</domain>

<decisions>
## Implementation Decisions

### Status Set Ownership
- **D-01:** Team-wide default status sets are scoped per sub-team, not globally across the whole organization.
- **D-02:** Supervisors/admins manage the default status set for their active or implicit sub-team, following the Phase 13 sub-team scoping model.
- **D-03:** Admin access should respect the global sub-team context switcher when editing defaults; supervisors operate only within their assigned sub-team.

### Per-Project Override Behavior
- **D-04:** Projects may define their own status set; projects without custom statuses inherit the sub-team default set.
- **D-05:** Statuses need a stable canonical key/slug so project-specific statuses can be mapped back to default statuses safely.
- **D-06:** When switching a project from custom statuses back to the sub-team default set, the system should auto-map matching slugs and require an explicit fallback only for unmatched statuses.

### Completion Rules
- **D-07:** Multiple statuses in a set may have `is_done = true`.
- **D-08:** Moving a task into any `is_done` status sets `completed_at`; moving it from any done status back to a non-done status clears `completed_at`.
- **D-09:** Phase 16 KPI and burndown work must use `custom_status.is_done`, not `TaskStatus.done` or status slug comparisons.

### Status Management UI
- **D-10:** Status management should be available from both `/projects` and `/tasks`.
- **D-11:** `/projects` should provide the full project-context settings surface for project overrides and access to sub-team defaults.
- **D-12:** `/tasks` should provide direct Kanban column management where supervisors/admins can see the impact of status changes on the board.
- **D-13:** Board-context editing must handle mixed project views carefully; project-specific settings should only apply when the board has a clear project context.

### Deletion, Archiving, and Reordering
- **D-14:** Deleting a status with assigned tasks should offer two safe paths: move affected tasks to a replacement status and delete, or archive the status.
- **D-15:** Archived statuses remain attached to existing tasks but are hidden from new task creation/status selection.
- **D-16:** Status reordering is immediate and shared: drag-and-drop reorder saves instantly and all users see the updated order.

### AI and Legacy Status Compatibility
- **D-17:** AI task parsing and quick task creation stay on the legacy enum values during the dual-write period.
- **D-18:** The backend maps legacy AI/status input (`todo`, `in_progress`, `review`, `done`, `blocked`) to the appropriate DB-backed status for the task's project/sub-team context.

### Agent's Discretion
- Exact schema names for status set/status tables and relationships.
- Exact API route names for status set management, as long as they follow existing router/API client patterns.
- Exact UI layout for status management controls on `/projects` and `/tasks`.
- Exact color picker implementation, provided it supports the roadmap's name/color/order requirements.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Roadmap and Requirements
- `.planning/ROADMAP.md` — Phase 15 goal, dependencies, and success criteria.
- `.planning/REQUIREMENTS.md` — STATUS-01 through STATUS-04 acceptance criteria.
- `.planning/STATE.md` — Locked dual-write strategy and Phase 16 `is_done` dependency notes.

### Prior Phase Context
- `.planning/phases/13-multi-team-hierarchy-timeline-visibility/13-CONTEXT.md` — Sub-team scoping and admin global switcher decisions.
- `.planning/phases/14-sprint-model/14-CONTEXT.md` — Sprint board backlog column and sprint/Kanban context decisions.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `frontend/src/lib/components/tasks/KanbanBoard.svelte`: Existing drag-and-drop column implementation using `svelte-dnd-action`; should be adapted to DB-provided status columns instead of the hardcoded `columns` array.
- `frontend/src/lib/components/tasks/KanbanCard.svelte`: Existing task card display can continue rendering task metadata while status data moves to DB-backed fields.
- `frontend/src/lib/api.ts`: Existing domain API client pattern should gain a status/status-set client section.
- `backend/app/routers/tasks.py`: Existing task list/update routes are the integration point for `custom_status_id`, dual-write mapping, and `completed_at` behavior.

### Established Patterns
- Backend models live in `backend/app/models.py`; schemas live in `backend/app/schemas.py`; routers use FastAPI `APIRouter` modules under `backend/app/routers/`.
- Existing writes use `await db.flush()` and rely on `get_db()` for transaction commit/rollback.
- Frontend uses Svelte 5, Tailwind utilities, `lucide-svelte`, and existing dark board/card styling.
- Admin sub-team scoping is passed through `X-SubTeam-ID` in `frontend/src/lib/api.ts`; status-set APIs should follow that established context model.

### Integration Points
- `backend/app/models.py`: Add DB-backed status/status-set models and `Task.custom_status_id` while retaining `Task.status`.
- `backend/app/schemas.py`: Add status/status-set create/update/out schemas and expose custom status fields on task responses as needed.
- `backend/app/routers/tasks.py`: Replace hardcoded completion checks with DB status `is_done` logic once custom status is present.
- `backend/app/routers/dashboard.py`, `backend/app/routers/performance.py`, `backend/app/routers/ai.py`, and timeline/task UI code currently check `TaskStatus.done`; Phase 15 should update direct completion behavior required now and flag remaining KPI-style aggregation changes for Phase 16 where appropriate.
- `frontend/src/routes/tasks/+page.svelte` and `frontend/src/lib/components/tasks/KanbanBoard.svelte`: Replace hardcoded status filters/options with fetched status sets.
- `frontend/src/routes/projects/+page.svelte`: Add project-context status settings/override management.

</code_context>

<specifics>
## Specific Ideas

- Use stable slugs/canonical keys for status mapping, especially when reverting project overrides back to sub-team defaults.
- Management should be reachable both from project settings and directly from the Kanban board.
- Deletion should not be a single destructive action: users can either move tasks and delete, or archive the status.

</specifics>

<deferred>
## Deferred Ideas

None - discussion stayed within phase scope.

</deferred>

---

*Phase: 15-Custom Kanban Statuses*
*Context gathered: 2026-04-26*
