---
plan: "19-03"
phase: "19-refactor-map-safety-baseline"
status: complete
completed: "2026-04-27"
---

# Plan 19-03 Summary: Frontend Target Map

## What Was Built

Created `19-FRONTEND-MAP.md` — the SvelteKit target structure, API/type split map, route boundary rules, and Phase 21 migration slices.

## Tasks Completed

- **19-03-01:** Documented frontend target structure keeping `frontend/src` as root with `lib/apis/`, `lib/types/`, and existing `lib/components/`, `lib/stores/`, `lib/websocket.ts`
- **19-03-02:** Mapped all current frontend files to target locations including the full `api.ts` split (17 API modules + centralized `request.ts`), inline type extraction, stores, components, routes, and config files
- **19-03-03:** Defined 8 frontend migration slices (F0–F7) with dependencies and per-slice verification

## Key Outputs

- Frontend target structure covering all required groups: `lib/apis`, `lib/components`, `lib/stores`, `lib/types`, `lib/utils`, WebSocket client placement, route-local component boundaries
- Centralized request behavior explicitly documented: base URL, credentials, X-SubTeam-ID header, error handling — all must remain in `apis/request.ts`
- Full `api.ts` split map: 17 feature API modules across `lib/apis/`
- Type extraction map: `StatusSetScope`, `CustomStatus`, `StatusSet`, `StatusTransition`, `StatusTransitionPair` → `lib/types/status.ts`; `ReminderSettings`, `ReminderSettingsProposal` → `lib/types/notification.ts`
- All 14 Svelte route URLs listed as PROTECTED
- F0–F7 migration slices with explicit dependencies and protected behavior per slice

## Deviations

None. No frontend code was moved or modified.
