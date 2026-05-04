---
phase: "21-frontend-sveltekit-structure"
plan: 3
subsystem: frontend
tags: [api, modules, refactor]
provides:
  - "frontend/src/lib/apis/index.ts: stable namespace barrel"
  - "frontend/src/lib/apis/auth.ts, users.ts, projects.ts, milestones.ts, sprints.ts, tasks.ts, schedules.ts, notifications.ts, ai.ts, chat.ts, dashboard.ts, performance.ts, timeline.ts, invites.ts, status-sets.ts, sub-teams.ts"
  - "frontend/src/lib/api.ts: temporary compatibility shim"
affects:
  - "frontend/src/lib/api.ts"
tech-stack:
  added: []
  patterns: ["namespace-extraction-pattern", "barrel-pattern", "compatibility-shim"]
key-files:
  created:
    - "frontend/src/lib/apis/auth.ts"
    - "frontend/src/lib/apis/users.ts"
    - "frontend/src/lib/apis/projects.ts"
    - "frontend/src/lib/apis/milestones.ts"
    - "frontend/src/lib/apis/sprints.ts"
    - "frontend/src/lib/apis/tasks.ts"
    - "frontend/src/lib/apis/schedules.ts"
    - "frontend/src/lib/apis/notifications.ts"
    - "frontend/src/lib/apis/ai.ts"
    - "frontend/src/lib/apis/chat.ts"
    - "frontend/src/lib/apis/dashboard.ts"
    - "frontend/src/lib/apis/performance.ts"
    - "frontend/src/lib/apis/timeline.ts"
    - "frontend/src/lib/apis/invites.ts"
    - "frontend/src/lib/apis/status-sets.ts"
    - "frontend/src/lib/apis/sub-teams.ts"
    - "frontend/src/lib/apis/index.ts"
  modified:
    - "frontend/src/lib/api.ts"
key-decisions:
  - "D-01/D-02: one module per namespace, all import from ./request"
  - "D-04: api.ts replaced with 3-line shim (export * from $lib/apis + export type * from $lib/types)"
  - "request not exported from barrel — API-internal only (D-11)"
  - "qs() helper internalized in performance.ts (not exported)"
requirements-completed: ["FRONT-01", "FRONT-02", "FRONT-03", "FRONT-04", "FRONT-05"]
duration: "~20 min"
completed: "2026-04-27"
---

# Phase 21 Plan 03: Feature API Modules and Temporary Shim Summary

Created 16 domain API modules under `frontend/src/lib/apis/` (auth, users, projects, milestones, sprints, tasks, schedules, notifications, ai, chat, dashboard, performance, timeline, invites, status-sets, sub-teams). Each module imports `request` from `./request` and exports its namespace. Created `apis/index.ts` barrel re-exporting all namespaces. Replaced `frontend/src/lib/api.ts` with a 3-line temporary compatibility shim (`export * from '$lib/apis'; export type * from '$lib/types'`). All existing `$lib/api` callsites continue to resolve through the shim.

Duration: ~20 min | Tasks: 4 | Files created: 17, modified: 1

## Deviations from Plan

None - plan executed exactly as written.

## Self-Check: PASSED

- All 16 namespace modules created under `apis/` ✅
- Each module exports its matching namespace object ✅
- `apis/index.ts` re-exports all namespaces including `statusSets`, `reminderSettings` ✅
- `request` not exported from barrel ✅
- `api.ts` is 3-line shim with comment + `$lib/apis` + `$lib/types` exports ✅

Next: Ready for Plan 04 (callsite migration, shim removal, final verification).
