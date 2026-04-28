---
phase: 27-timeline-gantt-clarity
plan: 01
subsystem: api
tags: [fastapi, timeline, sveltekit, typing, pytest]
requires:
  - phase: 26-navigation-information-architecture
    provides: stable route structure and scoped sub-team context behavior
provides:
  - richer timeline milestone/task payload for Phase 27 derivations
  - role-visibility regression tests for member/supervisor/admin timeline responses
  - typed frontend timeline API contract exports
affects: [timeline, gantt, milestone-planning, role-visibility]
tech-stack:
  added: []
  patterns: [explicit timeline response schemas, contract-first API assertions]
key-files:
  created: []
  modified:
    - backend/app/routers/timeline.py
    - backend/app/schemas/work.py
    - backend/tests/test_timeline.py
    - frontend/src/lib/apis/timeline.ts
key-decisions:
  - "Preserved existing member/supervisor/admin timeline filtering and only expanded payload fields."
  - "Used existing milestone/task/custom-status fields for risk/decision derivation inputs rather than adding persistence."
patterns-established:
  - "Timeline contract changes must ship with role-scoped API regression checks."
  - "Frontend timeline API wrapper exports typed interfaces instead of any-shaped payloads."
requirements-completed: [TL-02, TL-03, TL-05]
duration: 20min
completed: 2026-04-29
---

# Phase 27 Plan 01: Timeline Contract Expansion Summary

**Expanded `/api/timeline/` milestone/task metadata with preserved role visibility and a typed frontend timeline contract for milestone-first Gantt derivations.**

## Performance

- **Duration:** 20 min
- **Started:** 2026-04-28T18:16:00Z
- **Completed:** 2026-04-28T18:35:52Z
- **Tasks:** 2
- **Files modified:** 4

## Accomplishments
- Expanded timeline schemas and router payload to include milestone description/completed state and task description/tags/custom status.
- Preserved existing role-based visibility semantics for members, supervisors, and admins in timeline route behavior.
- Replaced placeholder timeline tests with concrete role visibility + payload shape assertions against real API calls.
- Added explicit exported frontend timeline interfaces (`TimelineProject`, `TimelineMilestone`, `TimelineTask`) and typed request return.

## Task Commits

1. **Task 1: Expand the timeline API payload using existing milestone and task fields** - `c9c3ff4` (feat)
2. **Task 2: Lock the contract with backend assertions and typed frontend interfaces** - `008d878` (test)

## Files Created/Modified
- `backend/app/routers/timeline.py` - Adds custom status eager loading and milestone description/completed fields to timeline payload assembly.
- `backend/app/schemas/work.py` - Extends timeline response models with milestone and task metadata fields needed for Phase 27 derivation logic.
- `backend/tests/test_timeline.py` - Adds seeded role-scoped timeline integration assertions for visibility and payload contract shape.
- `frontend/src/lib/apis/timeline.ts` - Defines exported typed timeline interfaces and typed `timeline.get()` return contract.

## Decisions Made
- Kept timeline access semantics unchanged and validated them through tests instead of altering filter logic.
- Exposed only existing model fields required by timeline clarity work; no new tables, computed persistence, or background jobs.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

- Backend verification initially failed in fixture setup due to string datetime inserts; fixed by using Python `datetime` values in seeded milestones.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Timeline UI work can now derive progress/risk/decision hints from the richer contract without backend persistence changes.
- Role visibility behavior is locked by regression tests to guard Phase 27 frontend refactors.

## Self-Check: PASSED

- FOUND: `.planning/phases/27-timeline-gantt-clarity/27-01-SUMMARY.md`
- FOUND: commit `c9c3ff4`
- FOUND: commit `008d878`
