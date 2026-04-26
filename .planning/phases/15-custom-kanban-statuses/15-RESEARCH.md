---
phase: 15
slug: custom-kanban-statuses
status: complete
created: 2026-04-26
---

# Phase 15 — Research: Custom Kanban Statuses

## Research Goal

Answer: what must be true to plan Phase 15 well, given the existing TeamFlow codebase and the locked discuss-phase decisions?

Phase 15 replaces hardcoded Kanban status enum behavior with DB-backed status sets while preserving legacy `tasks.status` during a dual-write transition.

## Source Inputs

- `.planning/phases/15-custom-kanban-statuses/15-CONTEXT.md`
- `.planning/REQUIREMENTS.md` (`STATUS-01` through `STATUS-04`)
- `.planning/ROADMAP.md` Phase 15 section
- `.planning/STATE.md` dual-write and Phase 16 dependency notes
- Backend: `backend/app/models.py`, `backend/app/schemas.py`, `backend/app/routers/tasks.py`, `backend/app/routers/projects.py`, `backend/app/main.py`
- Frontend: `frontend/src/routes/tasks/+page.svelte`, `frontend/src/lib/components/tasks/KanbanBoard.svelte`, `frontend/src/routes/projects/+page.svelte`, `frontend/src/lib/api.ts`, `frontend/src/lib/utils.ts`
- Tests: `backend/tests/*`, `frontend/tests/mobile/*`

## Current Code Findings

### Backend Status Model

`backend/app/models.py` currently defines:

- `TaskStatus` enum values: `todo`, `in_progress`, `review`, `done`, `blocked`
- `Task.status = Column(Enum(TaskStatus), default=TaskStatus.todo)`
- No `CustomStatus`, `StatusSet`, or `Task.custom_status_id` model fields yet
- `Project` has `sub_team_id`, which is the correct inheritance boundary for default status sets

Phase 15 must add DB-backed status structures without dropping `Task.status`.

### Task Completion Logic

`backend/app/routers/tasks.py` currently sets and clears `completed_at` only when `Task.status` changes to or from `TaskStatus.done`.

Phase 15 must replace this direct predicate in task writes with DB status `is_done` semantics:

- Moving into any status where `is_done = true` sets `completed_at`
- Moving from an `is_done` status to a non-done status clears `completed_at`
- Moving between two done statuses preserves `completed_at`
- Moving between two non-done statuses leaves `completed_at` unchanged unless explicitly provided by an authorized endpoint

### Existing AI Compatibility

The AI task parse path still emits legacy enum strings in `_AI_PARSE_SYSTEM_PROMPT`, and `_coerce_ai_parse()` validates against `TaskStatus`.

Per `D-17` and `D-18`, Phase 15 should keep AI output legacy enum-based during dual-write and map those legacy values to DB statuses server-side at task creation/update time.

### Existing UI

`frontend/src/lib/components/tasks/KanbanBoard.svelte` hardcodes:

```text
['todo', 'in_progress', 'review', 'done', 'blocked']
```

`frontend/src/routes/tasks/+page.svelte` also hardcodes status filter and create/edit status options.

`frontend/src/routes/projects/+page.svelte` has project cards and edit/create modal only; it has no project status override UI.

`frontend/src/lib/utils.ts` stores hardcoded `statusColors` and `statusLabels`; those should become fallbacks only, not the source of truth for board columns.

### Sub-Team Scoping

Phase 13 introduced `get_sub_team()` and frontend `X-SubTeam-ID` propagation through `frontend/src/lib/api.ts`.

Status-set APIs should follow this pattern:

- Members can read applicable statuses for their sub-team/project context.
- Supervisors can manage only their implicit sub-team default statuses and project overrides in that sub-team.
- Admins can manage the active `X-SubTeam-ID` context; if no sub-team context is selected, write endpoints should reject with a clear 400/403 instead of mutating global data.

## Recommended Data Model

Use two explicit tables.

### `StatusSet`

Purpose: owns an ordered set of statuses for either a sub-team default or a project override.

Recommended fields:

- `id`
- `sub_team_id` nullable FK to `sub_teams.id`
- `project_id` nullable FK to `projects.id`
- `scope`: string or enum with values `sub_team_default` and `project`
- `created_at`, `updated_at`

Constraints:

- Exactly one of `project_id` or `sub_team_id` identifies the effective owner for a set.
- One default set per sub-team.
- One project override set per project.
- Project override set must belong to a project whose `sub_team_id` matches the set `sub_team_id`.

### `CustomStatus`

Purpose: one Kanban column/status record inside a status set.

Recommended fields:

- `id`
- `status_set_id` FK to `status_sets.id`
- `name`
- `slug`
- `color`
- `position`
- `is_done`
- `is_archived`
- `legacy_status` nullable enum/string mapping to existing `TaskStatus`
- `created_at`, `updated_at`

Constraints:

- Unique `(status_set_id, slug)`
- Unique `(status_set_id, position)` or position maintained by normalized updates
- Slug should be lowercase stable canonical key, generated from name but not silently changed after creation
- Multiple `is_done = true` statuses are allowed

### `Task.custom_status_id`

Add nullable FK to `custom_statuses.id`.

Keep `Task.status` during the dual-write transition. Do not remove or rename enum values in this phase.

## Migration Strategy

The Alembic migration must be explicit and reversible enough for local development.

Recommended migration sequence:

1. Create `status_sets`.
2. Create `custom_statuses`.
3. Add nullable `tasks.custom_status_id`.
4. For every existing sub-team, create one default status set.
5. For unscoped projects/tasks, create a fallback default status set with `sub_team_id = NULL`.
6. Seed default custom statuses for each status set:
   - `todo` / `To Do` / gray / position 0 / `is_done = false`
   - `in_progress` / `In Progress` / blue / position 1 / `is_done = false`
   - `review` / `Review` / amber / position 2 / `is_done = false`
   - `done` / `Done` / green / position 3 / `is_done = true`
   - `blocked` / `Blocked` / red / position 4 / `is_done = false`
7. Backfill every task's `custom_status_id` by matching its legacy `Task.status` to the status set for its project sub-team, falling back to the unscoped default set.
8. Preserve existing `completed_at` values for existing tasks.
9. Add indexes for task lookup and status ordering.

The migration must include row-count verification as an execution acceptance criterion:

- `select count(*) from tasks` before and after the migration must match
- `select count(*) from tasks where custom_status_id is null` must be zero after backfill, unless orphan/unscoped edge cases are explicitly documented and handled

## API Design Recommendation

Add a focused router, for example `backend/app/routers/statuses.py`, mounted in `backend/app/main.py`.

Recommended endpoints:

- `GET /api/status-sets/default`
  - Returns the current sub-team default set.
- `GET /api/status-sets/effective?project_id={id}`
  - Returns the project override set if present, else the sub-team default.
- `POST /api/status-sets/default/statuses`
  - Create a default-set status for the current sub-team.
- `PATCH /api/status-sets/statuses/{status_id}`
  - Update name, color, `is_done`, archive state.
- `POST /api/status-sets/{status_set_id}/reorder`
  - Save ordered status IDs.
- `POST /api/projects/{project_id}/status-set`
  - Create a project override set by copying the effective/default set.
- `DELETE /api/projects/{project_id}/status-set`
  - Revert to default after auto-mapping matching slugs and requiring fallback status for unmatched slugs.
- `POST /api/status-sets/statuses/{status_id}/delete`
  - Either move assigned tasks to `replacement_status_id` and delete, or archive.

Keep route names flexible if they better match existing project style, but preserve these capabilities.

## Backend Integration Requirements

### Task Create

Task creation should accept either:

- `custom_status_id`
- legacy `status`

If only `status` is provided, map it to the effective status set using `legacy_status` or matching `slug`.

If neither is provided, use the effective status whose slug is `todo`; if missing, use the first non-archived status by position.

Dual-write behavior:

- Set `Task.custom_status_id`
- Set `Task.status` to the mapped legacy value where available
- If the selected custom status has no `legacy_status`, keep `Task.status` as the closest safe fallback, preferably `done` for `is_done = true` and `todo` otherwise

### Task Update

Task update should accept either:

- `custom_status_id`
- legacy `status`

The endpoint must resolve the final `CustomStatus`, update both fields, and apply completion timestamp transitions based on old/new `is_done`.

### Task List and Response

`TaskOut` should include:

- `custom_status_id`
- `custom_status` object or fields sufficient for UI display: `id`, `name`, `slug`, `color`, `position`, `is_done`, `is_archived`

Task filtering should support:

- Existing `status` legacy filter during transition
- New `custom_status_id` filter for DB-backed UI

### Project Override Rules

Project override creation should copy current effective statuses into a new project-scoped set. Slugs remain stable.

Reverting to defaults should:

- Auto-map tasks by matching status slug
- For unmatched slugs, require a fallback default status ID
- Refuse silent fallback to `todo`

### Delete and Archive Rules

Requirement `STATUS-01` says a status cannot be deleted if tasks are assigned. Discuss decision `D-14` refines this:

- Deleting an assigned status must not be a single destructive action.
- The API should support move-and-delete with explicit `replacement_status_id`.
- The API should support archive without moving existing tasks.
- Archived statuses remain valid for existing tasks but are hidden from new selection.

## Frontend Integration Requirements

### API Client

Add a `statusSets` client section to `frontend/src/lib/api.ts` following existing `request()` and `X-SubTeam-ID` behavior.

Expected methods:

- `defaultSet()`
- `effective(projectId?: number)`
- `createStatus(scope, data)`
- `updateStatus(statusId, data)`
- `reorder(statusSetId, statusIds)`
- `createProjectOverride(projectId)`
- `revertProjectOverride(projectId, fallbackMappings)`
- `deleteOrArchiveStatus(statusId, data)`

### Task Page

`frontend/src/routes/tasks/+page.svelte` should load statuses alongside tasks/users/projects/milestones.

Replace hardcoded status filter and form options with active statuses from the effective/default set.

Board-context editing requirements:

- Provide status management controls on `/tasks`.
- If the board has a clear project context, show project override controls.
- If the board is a mixed-project view, show sub-team default management only and avoid applying project-specific changes.

### Kanban Board

`frontend/src/lib/components/tasks/KanbanBoard.svelte` should accept a `statuses` prop and group by `task.custom_status_id`.

During transition, fallback grouping by legacy `task.status` is acceptable only when `custom_status_id` is absent.

The board should render status names/colors from DB records, not from `statusLabels`/`statusColors`.

### Project Page

`frontend/src/routes/projects/+page.svelte` should provide full project-context status settings:

- Show whether a project inherits default statuses or has an override.
- Create project override by copying defaults.
- Reorder, create, update, archive/delete statuses for that project.
- Revert project override with slug auto-map and explicit fallback prompt for unmatched statuses.

## Testing Strategy

### Backend Tests

Add or extend tests in `backend/tests/` for:

- Migration/default seed behavior where feasible in test setup.
- Supervisor/admin can manage status sets within scoped sub-team.
- Member cannot mutate status sets.
- Project override inherits default until override exists.
- Revert project override maps by slug and requires fallback for unmatched slug.
- Deleting assigned status without replacement returns a validation error.
- Move-and-delete migrates tasks to replacement and removes the status.
- Archive hides status from selection but existing tasks retain it.
- Task create maps legacy status to `custom_status_id`.
- Task update sets/clears/preserves `completed_at` based on old/new `is_done`.

### Frontend Checks

Use `bun run check` for Svelte type/component validation.

Add or extend Playwright mobile tests only if the implementation touches mobile-specific behavior; otherwise, manual UAT can cover status management flows.

## Validation Architecture

Phase 15 needs a validation strategy because it changes data model, migration behavior, permissions, task completion semantics, and UI control surfaces.

Critical validation dimensions:

1. **Data migration safety:** no task rows lost; every task gains a DB status; existing `completed_at` values preserved.
2. **Dual-write correctness:** create/update keeps `Task.status` and `Task.custom_status_id` coherent.
3. **Completion semantics:** `completed_at` follows `CustomStatus.is_done`, not legacy `TaskStatus.done`.
4. **Sub-team authorization:** supervisors/admins mutate only the correct sub-team context.
5. **Project override inheritance:** projects inherit defaults until an override exists.
6. **Deletion/archive safety:** assigned statuses cannot disappear without explicit move or archive behavior.
7. **UI source of truth:** Kanban columns and form options come from API status records.
8. **Phase 16 readiness:** code exposes `custom_status_id` and `is_done` data that KPI queries can join against.

## Planning Recommendations

Split execution into five plans:

1. Backend schema, migration, seed/backfill, and models.
2. Backend schemas/router/helper logic for status sets and task dual-write.
3. Frontend API and reusable status management components.
4. Integrate statuses into `/tasks`, Kanban board, and `/projects`.
5. Validation, tests, and cross-feature cleanup for completion semantics.

Use Wave 1 for schema/migration first. Do not start UI implementation until backend API shapes are stable.

## Open Risks

- Existing uncommitted `backend/app/schemas.py` changes appear related to Phase 14 sprint schemas. Phase 15 execution should inspect and preserve those changes, not overwrite them.
- `Task.status` must remain during the transition because AI parsing and existing UI still rely on it.
- Multiple done statuses make simple `status === 'done'` UI checks incorrect; plans must identify and replace the highest-risk checks in task-facing UI now, while KPI aggregate rewrites remain Phase 16.
- A missing UI design contract should block plan generation because this phase changes `/tasks` and `/projects` management surfaces.

## RESEARCH COMPLETE
