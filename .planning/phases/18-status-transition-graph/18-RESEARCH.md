---
phase: 18
slug: status-transition-graph
status: complete
created: 2026-04-26
---

# Phase 18: Status Transition Graph - Research

## Research Complete

Phase 18 should extend the Phase 15 DB-backed status-set work with a directed transition allowlist per status set. The implementation should stay close to existing status-set APIs and task update flow: add a normalized transition table, expose transition CRUD under `/api/status-sets`, enforce moves in `update_task`, and then pass transition data to the status management and task board UI.

## Scope Inputs

- `.planning/ROADMAP.md`: Phase 18 goal is a YouTrack-style directed graph where an empty graph preserves free movement.
- `.planning/phases/18-status-transition-graph/18-CONTEXT.md`: Captures locked decisions D-01 through D-23, including matrix-first editing, backend 422 structured errors, project override snapshots, and archived-status behavior.
- `.planning/todos/pending/2026-04-26-status-transition-graph-workflow.md`: Captures the original workflow-rule idea and UI/enforcement notes.
- `.planning/phases/15-custom-kanban-statuses/15-CONTEXT.md`: Defines the existing DB-backed status-set boundary this phase builds on.

## Existing Backend Shape

`backend/app/models.py` already has:

- `StatusSet` with `statuses` relationship and `StatusSetScope`.
- `CustomStatus` with `status_set_id`, `position`, `is_done`, `is_archived`, and `legacy_status`.
- `Task.custom_status_id` plus legacy `Task.status` for dual-write compatibility.

`backend/app/routers/statuses.py` already centralizes status-set reads/writes:

- `_get_effective_set` resolves project override first, then sub-team default, then global default.
- `_copy_statuses` copies default statuses into project overrides.
- `_require_status_write_scope` restricts writes to supervisor/admin.
- Delete/archive and project override revert logic already update affected task `custom_status_id` values.

`backend/app/routers/tasks.py` is the enforcement point:

- `_resolve_custom_status` maps explicit `custom_status_id` or legacy status to a concrete DB status.
- `update_task` updates status, completion state, and `completed_at`.
- Enforcement should run only when the resolved custom status changes or the project change changes the effective status set; ordinary task edits should not be blocked.

## Recommended Data Model

Add `StatusTransition` as a normalized table rather than JSON on `StatusSet`.

Required fields:

- `id`
- `status_set_id` FK to `status_sets.id`, indexed
- `from_status_id` FK to `custom_statuses.id`, indexed
- `to_status_id` FK to `custom_statuses.id`, indexed
- `created_at`

Required constraints:

- Unique constraint on `(status_set_id, from_status_id, to_status_id)`.
- Check constraint preventing `from_status_id = to_status_id`.
- Foreign keys should cascade or be explicitly cleaned up when a status is deleted.

Relationship notes:

- Add `StatusSet.transitions` with `cascade="all, delete-orphan"`.
- Add `CustomStatus.outgoing_transitions` and `incoming_transitions` only if they simplify implementation; otherwise direct queries are enough.
- Ensure transition endpoints validate both statuses belong to the same status set and are not archived for create/update paths.

## Migration Notes

Create one Alembic migration for `status_transitions`. It should be independent of the Phase 15 migration and should not rewrite existing status data.

Migration checks:

- Table creation works on empty and populated databases.
- Unique constraint name is stable enough for downgrade.
- Indexes support transition lookup by status set and current status.
- Downgrade drops table only; it must not mutate tasks or statuses.

## API Plan

Extend `backend/app/schemas.py` with:

- `StatusTransitionOut`: `id`, `status_set_id`, `from_status_id`, `to_status_id`, `created_at`.
- `StatusTransitionCreate`: `from_status_id`, `to_status_id`.
- `StatusTransitionsReplace`: list of transition pairs for matrix save.
- `BlockedStatusTransitionDetail`: stable error payload with `code`, `message`, `current_status_id`, `current_status_name`, `target_status_id`, `target_status_name`, `status_set_id`, and `allowed_status_ids`.

Extend `backend/app/routers/statuses.py` with:

- `GET /api/status-sets/{status_set_id}/transitions?include_archived=false`
- `POST /api/status-sets/{status_set_id}/transitions` for replacing the transition set from matrix state
- `DELETE /api/status-sets/{status_set_id}/transitions/{transition_id}` if the UI needs granular deletes

The matrix UI is easiest if `POST` replaces the full set atomically. Keep a granular `DELETE` only if it matches existing API style better during implementation.

Default GET behavior should return active-status transitions only. `include_archived=true` should expose archived-linked transitions for management/recovery, matching D-22.

## Enforcement Algorithm

1. Resolve the task's current custom status. If `task.custom_status_id` is null, use existing legacy status mapping for the task's effective project/sub-team before enforcement.
2. Resolve the target custom status from `custom_status_id` or legacy `status`.
3. Determine the effective status set for the target project. If `project_id` changes in the same update, use the new project for the target set.
4. If the effective status set has no transition rows, allow the move.
5. If the current and target statuses are the same, allow as a no-op.
6. If transition rows exist, allow only when `(current_status_id, target_status_id)` exists for the effective status set.
7. If blocked, return HTTP 422 with a structured detail object and a stable code such as `status_transition_blocked`.

Project-change enforcement needs careful handling because a task may move between effective status sets. If a project change causes remapping by slug/legacy status, enforcement should compare the resolved current status in the old set to the target status in the new effective set only when a status change is requested; otherwise it should not block ordinary project reassignment unless the implementation explicitly changes `custom_status_id`.

## Project Override Behavior

When creating a project override:

- Copy statuses first.
- Build a source-to-target status ID map by slug.
- Copy transitions whose source and target statuses both have matching copied statuses.
- Existing project overrides remain independent snapshots.

When reverting a project override:

- Existing delete cascade on the project status set should remove project transitions.
- Task remapping should continue to use existing fallback mapping behavior.

When deleting or archiving statuses:

- Hard delete should remove transitions where the deleted status is either endpoint.
- Archive should keep transitions in the DB but hide them from default transition API responses and the editor.
- Unarchive should make those transitions visible again if both endpoints are active.

## Frontend Integration

`frontend/src/lib/api.ts` should add transition types and client methods in the existing `statusSets` section:

- `StatusTransition`
- `StatusTransitionPayload`
- `statusSets.getTransitions(statusSetId, includeArchived?)`
- `statusSets.replaceTransitions(statusSetId, transitions)`
- optional `statusSets.deleteTransition(statusSetId, transitionId)`

`StatusSetManager.svelte` should grow a transition-management area:

- Primary editor: matrix/table with active statuses as rows and columns.
- Self-transition cells hidden or disabled.
- Quick action: "Generate linear flow" creates forward transitions in active status order.
- Read-only preview: simple nodes and edges derived from matrix state; no drag-to-connect scope.
- Warnings: non-blocking warnings for dead ends, disconnected active statuses, or no route to a done status.

`KanbanBoard.svelte` should receive transition data or an allowed-target helper:

- Prevent obvious invalid drops where practical.
- Add small header hint icons/tooltips for restricted columns.
- Still dispatch attempted moves in ambiguous cases and rely on backend 422 as source of truth.

`frontend/src/routes/tasks/+page.svelte` should:

- Load transitions with the effective status set.
- Filter edit dropdown target statuses to allowed targets plus the current status.
- On blocked 422, revert local state, show a direct toast, and refresh status set/transition data.
- Preserve free movement when no transitions exist.

## Validation Architecture

Automated validation should cover the phase at three layers:

1. Model and migration tests: `StatusTransition` exists, constraints reject duplicates and self-transitions, and deleting a status removes linked transitions.
2. API/enforcement tests: transition CRUD permission rules, empty graph free movement, strict allowlist blocking with HTTP 422, legacy-status resolution before enforcement, done status requiring an explicit edge, and project override copy/revert behavior.
3. Frontend checks: TypeScript/Svelte check for new transition types and components; focused component logic tests are optional if the repo lacks frontend test infrastructure.

Recommended quick commands:

- Backend targeted: `rtk pytest backend/tests/test_status_sets.py backend/tests/test_tasks.py`
- Frontend check: `cd frontend && rtk bun run check`
- Full backend: `rtk pytest backend/tests`

## Threat Model Inputs

Plans should include a threat model covering:

- Authorization bypass: transition writes must use `_require_status_write_scope`.
- Cross-status-set mutation: API must reject transitions where endpoints do not belong to the target status set.
- Client-side trust: Kanban/dropdown filtering is advisory; backend 422 enforcement remains authoritative.
- Data integrity: duplicates, self-transitions, archived endpoints, and hard deletes must not leave invalid active workflow rules.
- Information quality: structured 422 responses should reveal status names/IDs already visible to the current user, not unrelated project/team data.

## Planning Recommendations

Split execution into four waves:

1. Backend persistence and API foundation.
2. Backend enforcement and project override/status lifecycle integration.
3. Frontend transition-management UI.
4. Frontend task-flow enforcement plus regression verification.

Do not combine all backend and frontend work into one plan. The migration/API foundation should land before task enforcement, and both should land before the UI consumes transition data.
