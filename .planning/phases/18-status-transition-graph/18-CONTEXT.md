# Phase 18: Status Transition Graph - Context

**Gathered:** 2026-04-26
**Status:** Ready for planning

<domain>
## Phase Boundary

Add workflow rules to DB-backed status sets by storing directed allowed transitions between custom statuses. When a status set has transition rules, task moves not represented by the graph are rejected. When a status set has no transition rules, existing free movement stays fully backward-compatible.

This phase includes the `StatusTransition` data model and migration, status-set transition APIs, backend task-update enforcement, Kanban drag/drop enforcement and feedback, task edit dropdown filtering, and transition management inside the existing status-set management surface.

Note: `.planning/PROJECT.md`, `.planning/REQUIREMENTS.md`, and `.planning/STATE.md` currently contain v2.1 structural-refactor language that starts after Phase 18. `.planning/ROADMAP.md` and `gsd-sdk query init.phase-op 18` identify Phase 18 as Status Transition Graph; downstream agents should treat the roadmap Phase 18 entry as the source of truth for this context.

</domain>

<decisions>
## Implementation Decisions

### Transition Editing UI
- **D-01:** Use a hybrid transition editor: a matrix/table is the primary editing surface, with a read-only graph preview.
- **D-02:** The graph preview should show statuses as nodes and allowed transitions as edges; it must not become the primary editor.
- **D-03:** Validation level is left to the agent's discretion, with a bias toward non-blocking warnings over hard save failures.
- **D-04:** Transition rules should live wherever they fit cleanly in `StatusSetManager`; tabs are preferred if the component starts feeling crowded.
- **D-05:** Provide an explicit "Generate linear flow" quick-start action that creates ordered forward transitions from each active status to the next active status.
- **D-06:** Empty transition list still means free movement until rules are actually created.
- **D-07:** Self-transitions should be hidden or disabled in the editor.
- **D-08:** Transition editing uses active statuses only. Archived statuses stay out of the transition rule editor.

### Enforcement Rules
- **D-09:** Tasks without `custom_status_id` should be resolved through the existing legacy-status mapping first, then transition enforcement applies.
- **D-10:** Enforce workflow rules on status changes and project changes. Ordinary task edits should not be blocked by transition rules.
- **D-11:** Transition rules are a strict allowlist: if a status set has any transition rules, non-listed status moves are blocked.
- **D-12:** `is_done` statuses get no runtime exception. Moving into done requires an explicit allowed transition when rules exist.
- **D-13:** Backend blocked transitions return HTTP 422 with structured detail, including a stable error code plus current/target status context for UI feedback.

### User Feedback
- **D-14:** Kanban should use a hybrid feedback model: mark or prevent obvious invalid targets client-side where practical, but still handle backend 422 by reverting and showing a toast.
- **D-15:** Blocked-move toast wording is left to the agent's discretion, with a bias toward direct and status-specific messages from the structured backend response.
- **D-16:** The task edit dropdown should show allowed target statuses plus the current status so the selected value never disappears.
- **D-17:** Kanban column headers should use small hint icons/tooltips for transition restrictions, not always-visible labels.
- **D-18:** If the backend returns a blocked-transition 422, the frontend should refresh status set/transition data so future hints reflect current rules.

### Project Override Behavior
- **D-19:** Project-specific status overrides should copy matching transition rules from the effective default status set when the override is created.
- **D-20:** Reverting a project override should discard the project-specific transition rules along with the project status set.
- **D-21:** Deleting a status removes transitions involving it; archiving keeps those transitions dormant/hidden so they can be restored if the status is unarchived later.
- **D-22:** The transition API should return active-status transitions by default, with an `include_archived=true` option for management/recovery.
- **D-23:** Project overrides are independent snapshots. Default transition-rule changes do not automatically sync into existing project overrides.

### Agent's Discretion
- Exact validation implementation for graph-shape issues such as dead ends, disconnected statuses, and no path to a done status, with a preference for warnings rather than blocking saves unless planning finds a strong reason to block.
- Exact placement of transition rules inside `StatusSetManager`, with tabs preferred if the manager becomes crowded.
- Exact blocked-move toast copy, provided it uses the structured 422 response and is direct/status-specific.
- Exact read-only graph rendering approach, provided the matrix remains the primary editor and the preview does not add heavy interaction scope.

### Folded Todos
- `Status transition graph / workflow rules (YouTrack-style)` from `.planning/todos/pending/2026-04-26-status-transition-graph-workflow.md` is folded into this phase. It defines the same problem as Phase 18: statuses are currently a flat ordered list, and teams need directed workflow rules to prevent skipping required steps.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Roadmap and Scope
- `.planning/ROADMAP.md` — Phase 18 goal, dependencies, success criteria, and sequencing before v2.1 refactor work.
- `.planning/todos/pending/2026-04-26-status-transition-graph-workflow.md` — User-captured workflow-rule idea, YouTrack-style reference, management UI notes, and enforcement notes.

### Prior Phase Context
- `.planning/phases/15-custom-kanban-statuses/15-CONTEXT.md` — DB-backed status-set decisions, sub-team/project override behavior, archived status behavior, stable slug mapping, and `custom_status.is_done` completion semantics.

### Current Project State
- `.planning/STATE.md` — Contains active planning state and relevant watch-outs, including the current mismatch between Phase 18 roadmap scope and v2.1 structural-refactor notes.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `backend/app/models.py`: Existing `StatusSet`, `CustomStatus`, and `Task.custom_status_id` models are the natural integration point for `StatusTransition`.
- `backend/app/routers/statuses.py`: Existing `/api/status-sets` router already handles effective/default status sets, project overrides, status reorder, delete/archive, and write-scope authorization.
- `backend/app/routers/tasks.py`: Existing `update_task` resolves legacy statuses to custom statuses and manages `completed_at`; this is the backend enforcement point for transition validation.
- `frontend/src/lib/api.ts`: Existing `statusSets` API client section should grow transition methods and transition-related types.
- `frontend/src/lib/components/statuses/StatusSetManager.svelte`: Existing status management surface should host transition management.
- `frontend/src/lib/components/tasks/KanbanBoard.svelte`: Existing `svelte-dnd-action` board dispatches `taskMove`; this is the client-side drag/drop enforcement and feedback point.
- `frontend/src/routes/tasks/+page.svelte`: Existing task edit form and `handleTaskMove` flow should filter statuses and handle structured blocked-transition errors.

### Established Patterns
- Status sets can be sub-team defaults or project overrides; project overrides currently copy statuses from the effective default status set.
- Archived statuses remain attached to existing tasks but are hidden from new task creation/status selection.
- Backend writes use `await db.flush()` and rely on `get_db()` for transaction commit/rollback.
- Status-set writes are supervisor/admin only through `_require_status_write_scope`.
- Frontend status management is available from `/tasks` and `/projects`, with mixed-project safeguards already present.
- Frontend uses `svelte-sonner` toasts and small `lucide-svelte` icons; use those patterns for blocked-move feedback and column hints.

### Integration Points
- Add transition persistence and relationships around `StatusSet`/`CustomStatus` while preserving empty-transition free movement.
- Add `GET/POST/DELETE /status-sets/{id}/transitions` behavior under the existing status-set router/API pattern.
- Extend task update validation to compare current and target custom statuses against the effective status set's transition graph.
- Extend project override copy/revert/delete/archive logic to copy, discard, delete, or hide transitions according to the decisions above.
- Extend `StatusSetOut` or related schemas/API types so the frontend can render matrix state, graph preview, allowed targets, and column hints.

</code_context>

<specifics>
## Specific Ideas

- The desired workflow behavior is YouTrack-style: a directed graph controls which status moves are allowed.
- Matrix/table editing is the source of truth for editing; the graph is a read-only preview.
- "Generate linear flow" should create forward transitions in active status order as a quick-start.
- Blocked transitions should include enough structured backend detail for UI messages such as current status, target status, and a stable error code.
- Project overrides behave as independent snapshots after creation.

</specifics>

<deferred>
## Deferred Ideas

None - discussion stayed within phase scope.

</deferred>

---

*Phase: 18-Status Transition Graph*
*Context gathered: 2026-04-26*
