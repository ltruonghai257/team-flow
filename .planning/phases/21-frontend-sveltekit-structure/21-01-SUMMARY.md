---
phase: "21-frontend-sveltekit-structure"
plan: 1
subsystem: frontend
tags: [types, api, refactor]
provides:
  - "21-IMPORT-MAP.md: complete $lib/api importer inventory"
  - "frontend/src/lib/types/status.ts: shared status types"
  - "frontend/src/lib/types/notification.ts: shared reminder types"
  - "frontend/src/lib/types/index.ts: type barrel"
affects:
  - "frontend/src/lib/api.ts"
tech-stack:
  added: []
  patterns: ["type-barrel", "re-export-shim"]
key-files:
  created:
    - ".planning/phases/21-frontend-sveltekit-structure/21-IMPORT-MAP.md"
    - "frontend/src/lib/types/status.ts"
    - "frontend/src/lib/types/notification.ts"
    - "frontend/src/lib/types/index.ts"
  modified:
    - "frontend/src/lib/api.ts"
key-decisions:
  - "D-06/D-07: moved StatusSetScope, CustomStatus, StatusSet, StatusTransition, StatusTransitionPair to status.ts; ReminderSettings, ReminderSettingsProposal to notification.ts"
  - "api.ts re-exports all moved types for backward compat"
requirements-completed: ["FRONT-01", "FRONT-03", "FRONT-04", "FRONT-05"]
duration: "~15 min"
completed: "2026-04-27"
---

# Phase 21 Plan 01: Import Inventory and Shared Types Summary

Extracted the 33-file `$lib/api` importer inventory into `21-IMPORT-MAP.md`. Created `frontend/src/lib/types/status.ts` (5 status types), `frontend/src/lib/types/notification.ts` (2 reminder types), and `frontend/src/lib/types/index.ts` barrel. Removed inline type definitions from `api.ts` and replaced with re-exports from the new type modules; `$lib/api` callsites remain unmodified and still compile through the re-export shim.

Duration: ~15 min | Tasks: 4 | Files created: 4, modified: 1

## Deviations from Plan

None - plan executed exactly as written.

## Self-Check: PASSED

- `21-IMPORT-MAP.md` exists with `## Importer Inventory`, all key files listed ✅
- `status.ts` exports all 5 status types ✅
- `notification.ts` exports `ReminderSettings`, `ReminderSettingsProposal` with `'pending' | 'approved' | 'rejected'` union ✅
- `index.ts` re-exports both modules ✅
- `api.ts` imports from `$lib/types/status`, re-exports both type modules, no inline `CustomStatus`/`ReminderSettings` ✅

Next: Ready for Plan 02 (shared request wrapper extraction).
