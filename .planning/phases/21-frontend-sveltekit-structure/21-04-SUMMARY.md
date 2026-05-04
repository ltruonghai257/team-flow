---
phase: "21-frontend-sveltekit-structure"
plan: 4
subsystem: frontend
tags: [migration, callsites, verification]
provides:
  - "All callsites migrated from $lib/api to $lib/apis (values) and $lib/types (types)"
  - "Shim api.ts deleted"
  - "bun run check: 0 errors"
  - "bun run build: exit 0"
affects:
  - 13 route files
  - 2 store files
  - 8 component files
tech-stack:
  added: []
  patterns: ["direct-module-imports"]
key-files:
  deleted:
    - "frontend/src/lib/api.ts"
  modified:
    - "frontend/src/routes/+layout.svelte"
    - "frontend/src/routes/+page.svelte"
    - "frontend/src/routes/ai/+page.svelte"
    - "frontend/src/routes/invite/accept/+page.svelte"
    - "frontend/src/routes/milestones/+page.svelte"
    - "frontend/src/routes/performance/+page.svelte"
    - "frontend/src/routes/performance/[id]/+page.svelte"
    - "frontend/src/routes/projects/+page.svelte"
    - "frontend/src/routes/register/+page.svelte"
    - "frontend/src/routes/schedule/+page.svelte"
    - "frontend/src/routes/tasks/+page.svelte"
    - "frontend/src/routes/team/+page.svelte"
    - "frontend/src/routes/timeline/+page.svelte"
    - "frontend/src/lib/stores/auth.ts"
    - "frontend/src/lib/stores/notifications.ts"
    - "frontend/src/lib/components/sprints/SprintForm.svelte"
    - "frontend/src/lib/components/sprints/SprintCloseModal.svelte"
    - "frontend/src/lib/components/performance/KpiWarnButton.svelte"
    - "frontend/src/lib/components/tasks/AiTaskInput.svelte"
    - "frontend/src/lib/components/tasks/KanbanBoard.svelte"
    - "frontend/src/lib/components/timeline/TimelineGantt.svelte"
    - "frontend/src/lib/components/statuses/ProjectStatusPanel.svelte"
    - "frontend/src/lib/components/statuses/StatusDeleteDialog.svelte"
    - "frontend/src/lib/components/statuses/StatusEditorRow.svelte"
    - "frontend/src/lib/components/statuses/StatusReorderList.svelte"
    - "frontend/src/lib/components/statuses/StatusSetManager.svelte"
    - "frontend/src/lib/components/statuses/StatusTransitionEditor.svelte"
    - "frontend/src/lib/components/statuses/StatusTransitionPreview.svelte"
requirements-completed: ["FRONT-01", "FRONT-02", "FRONT-03", "FRONT-04", "FRONT-05", "FRONT-06"]
duration: "~30 min"
completed: "2026-04-27"
---

# Phase 21 Plan 04: Callsite Migration, Shim Removal, and Final Verification Summary

Migrated all 33 callsites: 13 routes, 2 stores, 8 components updated from `$lib/api` to `$lib/apis` (values) and `$lib/types` (types). Deleted `frontend/src/lib/api.ts`. Final verification passed: `bun run check` reports 0 errors (9 pre-existing warnings, none introduced by Phase 21), `bun run build` exits 0 in 9.67s.

Duration: ~30 min | Tasks: 4 | Files deleted: 1, modified: 28

## Deviations from Plan

None - plan executed exactly as written.

## Self-Check: PASSED

- No bare `from '$lib/api'` imports remaining in `frontend/src` ✅
- `frontend/src/lib/api.ts` deleted ✅
- `bun run check` → 0 errors ✅
- `bun run build` → exit 0, ✓ built in 9.67s ✅
- Route URLs unchanged, API behavior unchanged ✅

Phase 21 complete.
