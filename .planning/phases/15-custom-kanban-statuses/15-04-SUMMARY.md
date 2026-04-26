---
phase: 15-custom-kanban-statuses
plan: 15-04
subsystem: frontend
tags: [svelte, kanban, status-sets, integration, projects, tasks]

requires:
  - statusSets API client (15-03)
  - Reusable status components (15-03)
provides:
  - KanbanBoard driven by DB-backed statuses with color dot, Done pill, custom_status_id dispatch
  - Tasks page loads effective status set, Manage Statuses panel, is_done completion
  - Projects page with Statuses toggle, ProjectStatusPanel, lazy-loaded per-project status sets
  - KanbanCard overdue check uses custom_status?.is_done with fallback to task.status === 'done'
affects: [frontend-tasks, frontend-projects, frontend-kanban]

key-files:
  modified:
    - frontend/src/lib/components/tasks/KanbanBoard.svelte
    - frontend/src/lib/components/tasks/KanbanCard.svelte
    - frontend/src/routes/tasks/+page.svelte
    - frontend/src/routes/projects/+page.svelte

key-decisions:
  - "KanbanBoard falls back to legacy 5-column layout when statuses prop is empty."
  - "tasks/+page.svelte wraps changeStatus into a 2-arg adapter for AgileView compatibility."
  - "Projects page loads status sets lazily on panel open to avoid N+1 on mount."

requirements-completed: [STATUS-01, STATUS-02, STATUS-04]

duration: 20 min
completed: 2026-04-26
---

# Phase 15 Plan 15-04: Integrate DB Statuses into Tasks, Kanban, and Projects UI

## Accomplishments

- **KanbanBoard.svelte**: removed hardcoded 5-column array; columns now built from `statuses` prop (active, sorted by position). Each column shows color dot, status name, count, Done pill. `taskStatusKey()` resolves `custom_status_id` first, falls back to `task.status`. Drag finalize dispatches `custom_status_id` when DB status present, `status` slug otherwise. Empty column copy: `No tasks in this status`. Preserves `touch-action: pan-x pan-y`.
- **KanbanCard.svelte**: overdue check uses `task.custom_status?.is_done ?? task.status === 'done'`.
- **tasks/+page.svelte**: imports `statusSets` + `StatusSetManager`; loads effective status set in `loadAll()`; status filter dropdown uses active DB statuses (legacy fallback); form status selects bind to `custom_status_id`; `Manage Statuses` toggle button shows `StatusSetManager`; `isTaskDone` reactive helper; `toggleStatus` uses `is_done` logic; `changeStatus` accepts `(taskId, legacyStatus, customStatusId)`; `handleTaskMove` dispatches `custom_status_id`; mixed project view guard.
- **projects/+page.svelte**: imports `statusSets` + `ProjectStatusPanel`; `toggleStatusPanel()` lazy-loads per-project status set; `Statuses` link on each project card; `ProjectStatusPanel` rendered in slide expansion.

## Verification

- PASS: `KanbanBoard.svelte` contains `export let statuses`, `custom_status_id`, `is_done`, `No tasks in this status`, `touch-action: pan-x pan-y`.
- PASS: `KanbanBoard.svelte` does not contain `const columns = ['todo', 'in_progress', 'review', 'done', 'blocked']`.
- PASS: `tasks/+page.svelte` contains `statusSets`, `StatusSetManager`, `Manage Statuses`, `custom_status_id`, `Project-specific statuses are available after filtering to one project.`.
- PASS: `tasks/+page.svelte` no longer has hardcoded 5-option status select as only source.
- PASS: `tasks/+page.svelte` contains `custom_status?.is_done`.
- PASS: `KanbanCard.svelte` contains `custom_status?.is_done`.
- PASS: `projects/+page.svelte` contains `ProjectStatusPanel`, `Statuses`, `statusSets.getEffective`, renders component with `Create project override` and `Revert to defaults` via prop.
- BLOCKED: `bun run check` exits 1 on 4 pre-existing errors (login, milestones, register, schedule). Zero new errors from 15-04 files.

## Task Commits

1. `27de030` — KanbanBoard + KanbanCard DB-status integration
2. `0b26e36` — tasks and projects page integration

---
*Phase: 15-custom-kanban-statuses*
*Completed: 2026-04-26*
