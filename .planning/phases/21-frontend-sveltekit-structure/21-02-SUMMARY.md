---
phase: "21-frontend-sveltekit-structure"
plan: 2
subsystem: frontend
tags: [api, request, refactor]
provides:
  - "frontend/src/lib/apis/request.ts: centralized request wrapper"
affects:
  - "frontend/src/lib/api.ts"
tech-stack:
  added: []
  patterns: ["protected-request-pattern"]
key-files:
  created:
    - "frontend/src/lib/apis/request.ts"
  modified:
    - "frontend/src/lib/api.ts"
key-decisions:
  - "D-03: request wrapper with BASE, subTeamStore, credentials:include, X-SubTeam-ID, ApiError, 204 handling all in apis/request.ts"
  - "auth.login remains raw fetch to /api/auth/token in api.ts (application/x-www-form-urlencoded)"
requirements-completed: ["FRONT-01", "FRONT-02", "FRONT-04", "FRONT-05"]
duration: "~10 min"
completed: "2026-04-27"
---

# Phase 21 Plan 02: Shared Request Wrapper Extraction Summary

Moved the `request()` function, `ApiError` interface, and `SubTeam` helper from `frontend/src/lib/api.ts` into `frontend/src/lib/apis/request.ts`. All protected behaviors preserved: `BASE = '/api'`, `credentials: 'include'`, `X-SubTeam-ID` injection, structured `ApiError.detail/status/payload`, 204 short-circuit. `api.ts` now imports `request` from `$lib/apis/request`. `auth.login` kept as a raw `fetch('/api/auth/token', ...)` call per the plan requirement. Existing `$lib/api` callsites unchanged.

Duration: ~10 min | Tasks: 3 | Files created: 1, modified: 1

## Deviations from Plan

None - plan executed exactly as written.

## Self-Check: PASSED

- `apis/request.ts` has all protected patterns ✅
- `api.ts` imports `request` from `$lib/apis/request` ✅
- `api.ts` has no local `async function request`, `interface ApiError`, or `interface SubTeam` ✅
- `auth.login` posts to `/api/auth/token` with `credentials: 'include'` ✅
- Existing `$lib/api` callsites unchanged ✅

Next: Ready for Plan 03 (feature API modules and temporary shim).
