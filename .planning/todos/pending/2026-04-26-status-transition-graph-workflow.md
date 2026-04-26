---
created: 2026-04-26T08:41:00.000Z
title: Status transition graph / workflow rules (YouTrack-style)
area: ui
files:
  - backend/app/models.py
  - backend/app/routers/statuses.py
  - frontend/src/lib/components/statuses/StatusSetManager.svelte
  - frontend/src/lib/components/tasks/KanbanBoard.svelte
---

## Problem

Currently statuses are a flat ordered list — any task can move to any status freely.
The user wants a directed graph of allowed transitions, like YouTrack workflow rules.

Example rule: A task in "In Progress" may only transition to "Testing" or "Deploy",
not directly to "Done". This prevents teams from accidentally skipping mandatory steps.

## Solution

### Backend

- Add a `StatusTransition` model (or JSON field on `StatusSet`) capturing
  `(from_status_id, to_status_id)` allowed pairs.
- Expose CRUD endpoints: `GET/POST/DELETE /status-sets/{id}/transitions`.
- On task update: if transitions are defined, validate that the requested
  `custom_status_id` is a permitted target from the current status; reject with 422 if not.
- If no transitions are defined for a status set, allow free movement (backward-compatible).

### Frontend — Management UI

- In `StatusSetManager`, add a "Transition rules" section (supervisor/admin only).
- Visual graph editor: each status is a node; drag an arrow from one node to another
  to allow that transition.
- Alternatively: simple matrix/table UI — rows = from, columns = to, checkbox cells.
- Show transition arrows on the Kanban column header as small hint icons.

### Frontend — Enforcement

- In `KanbanBoard`, when drag-drop finalises, check allowed transitions before
  dispatching `taskMove`. Show an inline error/toast if the move is blocked.
- In task edit form status dropdown, filter options to only allowed next statuses
  (based on current `custom_status_id`).

### Scope Notes

- Graph should be per `StatusSet` (both sub-team defaults and project overrides).
- Empty transition list = free movement (default, fully backward-compatible).
- Cycle detection: UI should warn if the graph becomes disconnected or has no
  path to a terminal (is_done) status.

## References

- YouTrack workflow graph: https://www.jetbrains.com/help/youtrack/server/workflow-graph.html
- Phase 15 custom status models: `.planning/phases/15-custom-kanban-statuses/`
