---
phase: 27-timeline-gantt-clarity
plan: 02
subsystem: ui
tags: [sveltekit, svelte-gantt, timeline, gantt, view-model]
requires:
  - phase: 27-timeline-gantt-clarity
    provides: expanded typed timeline payload and role-safe contract from 27-01
provides:
  - milestone-first timeline derivation model for progress, risk, decision, and expansion behavior
  - milestone parent gantt rows with expandable task rows and member-view context badges
  - page-level focus continuity between project/member modes without route churn
affects: [timeline, gantt, milestone-planning, member-view]
tech-stack:
  added: []
  patterns: [derived timeline view model, focus continuity across view toggles, tree-row gantt headers]
key-files:
  created:
    - frontend/src/lib/components/timeline/timeline-view-model.ts
  modified:
    - frontend/src/routes/timeline/+page.svelte
    - frontend/src/lib/components/timeline/TimelineGantt.svelte
key-decisions:
  - "Kept all milestone risk/decision/planning signals derived from existing timeline payload fields, with no new persistence."
  - "Used svelte-gantt tree rows and milestone headerHtml blocks so milestone rows stay non-draggable while task bars remain draggable/editable."
patterns-established:
  - "Timeline rendering logic belongs in a dedicated view-model helper instead of inline page code."
  - "Focus state is owned at page level and passed into view components so reloads and mode switches preserve context."
requirements-completed: [TL-01, TL-02, TL-03, TL-04, TL-05]
duration: 35min
completed: 2026-04-29
---

# Phase 27 Plan 02: Timeline Milestone-First UI Summary

**Rebuilt `/timeline` into a milestone-first gantt surface with derived milestone progress/risk/decision signals and preserved focus/date context across project/member views.**

## Performance

- **Duration:** 35 min
- **Started:** 2026-04-28T18:40:00Z
- **Completed:** 2026-04-28T19:15:00Z
- **Tasks:** 2
- **Files modified:** 3

## Accomplishments
- Added a reusable timeline view-model module that derives milestone progress rollups, status counts, risk/decision signals, default expansion, and task ordering.
- Added page-level focused milestone/task state that persists through timeline reloads and view mode switches while preserving the selected date range and existing edit/reschedule workflow.
- Refactored the gantt presentation to milestone-first tree rows with rich milestone parent headers, member-view milestone context badges, and focused milestone banner cues.

## Task Commits

1. **Task 1: Create the derived timeline view model and preserve focus state at the page level** - `17fc020` (feat)
2. **Task 2: Render milestone-first gantt rows and member-view context cues** - `79a5c72` (feat)

## Files Created/Modified
- `frontend/src/lib/components/timeline/timeline-view-model.ts` - Builds milestone-first derived presentation data and exported derivation helpers.
- `frontend/src/routes/timeline/+page.svelte` - Owns focused milestone/task continuity and keeps reload + modal behavior intact.
- `frontend/src/lib/components/timeline/TimelineGantt.svelte` - Renders milestone tree rows, milestone header signals, member context badges, and focus banner while retaining task drag/edit behavior.

## Decisions Made
- Derived all milestone risk, planning, and decision markers from existing milestone/task fields delivered in 27-01.
- Kept route URL and task interaction model unchanged; refactor is presentation/state only.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed Svelte `onMount` cleanup typing after async gantt initialization**
- **Found during:** Task 2
- **Issue:** `bun run check` failed due to invalid `onMount(async () => return cleanup)` signature.
- **Fix:** Converted to non-async `onMount` with inner async initializer and explicit teardown handler.
- **Files modified:** `frontend/src/lib/components/timeline/TimelineGantt.svelte`
- **Verification:** `cd frontend && bun run check` and `cd frontend && bun run build` passed.
- **Committed in:** `79a5c72`

---

**Total deviations:** 1 auto-fixed (Rule 1)
**Impact on plan:** Required for correctness; no scope creep.

## Issues Encountered

- `bun run check` initially failed on a component typing mismatch in new gantt mount logic; resolved within Task 2.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Phase 27-03 can add targeted regression checks against milestone-first row rendering, focus continuity, and preserved task edit/reschedule behavior.
- Timeline UI now has a dedicated derivation layer for milestone logic, reducing coupling in route-level code.

## Known Stubs

None.

## Self-Check: PASSED

- FOUND: `.planning/phases/27-timeline-gantt-clarity/27-02-SUMMARY.md`
- FOUND: commit `17fc020`
- FOUND: commit `79a5c72`
