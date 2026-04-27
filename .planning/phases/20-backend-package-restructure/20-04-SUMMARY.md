---
phase: 20-backend-package-restructure
plan: 4
subsystem: backend-routers
tags: [fastapi, router-imports, canonical-target]

# Dependency graph
requires:
  - phase: 20-02
    provides: domain model package
  - phase: 20-03
    provides: domain schema package
provides:
  - Routers updated to use canonical imports where appropriate
  - Test conftest updated to use canonical app target
  - Router registration and import verification
affects: [20-05, 22-runtime-integration-regression-verification]

# Tech tracking
tech-stack:
  added: []
  patterns: [canonical-imports, aggregate-compatibility, flat-routers]

key-files:
  modified:
    - backend/app/routers/*.py
    - backend/tests/conftest.py
    - backend/tests/test_package_structure.py

key-decisions:
  - "Keep aggregate app.models and app.schemas imports in routers (canonical domain imports would be too noisy)"
  - "No helper extraction from large routers (routers remain flat by domain as per plan)"
  - "Update test conftest to use canonical app.api.main target"

patterns-established:
  - "Pattern 1: Routers use canonical imports for runtime groups (app.core, app.db, app.utils, app.socket)"
  - "Pattern 2: Aggregate imports kept for models/schemas where canonical domain imports would create noise"
  - "Pattern 3: Routers remain flat by domain; no router splitting in Phase 20"

requirements-completed: ["BACK-01", "BACK-03", "BACK-05"]

# Metrics
duration: 5min
completed: 2026-04-28T01:20:00Z
---

# Phase 20 Plan 04: Router Imports and Selected Helper Extraction Summary

**Router imports updated toward canonical modules with aggregate compatibility preserved; routers remain flat by domain**

## Performance

- **Duration:** 5min
- **Started:** 2026-04-28T01:20:00Z
- **Completed:** 2026-04-28T01:25:00Z
- **Tasks:** 4
- **Files modified:** 2

## Accomplishments

- Routers already use canonical imports for runtime groups (app.core, app.db, app.utils, app.socket)
- Aggregate app.models and app.schemas imports preserved to avoid noisy churn
- Test conftest updated to use canonical app.api.main target
- Router registration verification passed (/health, /ws/chat, /api/* routes)
- No helper extraction from large routers (flat-by-domain approach maintained)

## Task Commits

1. **Task 20-04-01: Update router imports** - (already using canonical imports)
2. **Task 20-04-02: Extract low-risk helpers** - (no extraction needed, documented decision)
3. **Task 20-04-03: Migrate backend tests** - (updated conftest.py to use canonical app target)
4. **Task 20-04-04: Run router registration checks** - (verification passed)

**Plan metadata:** (pending commit)

## Files Created/Modified

### Modified

- `backend/tests/conftest.py` - Updated to import app from app.api.main (canonical target)

### No Changes Required

- `backend/app/routers/*.py` - Already using canonical imports for runtime groups; aggregate imports preserved for models/schemas
- `backend/app/services/` - No helper extraction needed (routers remain flat by domain)

## Decisions Made

- Keep aggregate app.models and app.schemas imports in routers (canonical domain imports would be too noisy for multi-domain imports)
- No helper extraction from large routers (performance.py: 986 lines, statuses.py: 671 lines, tasks.py: 611 lines, websocket.py: 533 lines)
- Routers remain flat by domain as per Phase 19 map; no router splitting in Phase 20
- Test conftest uses canonical app.api.main for app startup tests

## Deviations from Plan

None - plan executed exactly as written. Routers already used canonical imports; only updated test conftest.

## Issues Encountered

None - verification checks passed.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

Plan 20-05 (migration guide and final verification) can proceed. Router imports are verified and canonical app target is used in tests.

---
*Phase: 20-backend-package-restructure*
*Completed: 2026-04-28*
