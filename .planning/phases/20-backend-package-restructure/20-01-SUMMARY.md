---
phase: 20-backend-package-restructure
plan: 1
subsystem: backend-package
tags: [fastapi, package-restructure, compatibility-delegates]

# Dependency graph
requires:
  - phase: 19-refactor-map-safety-baseline
    provides: backend target structure, migration slices, protected behavior list
provides:
  - Open WebUI-inspired backend package groups (api/, core/, db/, internal/, socket/, utils/)
  - Canonical FastAPI app factory at app.api.main with create_app() and module-level app
  - Compatibility delegates preserving app.main:app for uvicorn/Docker/supervisord
  - Runtime-adjacent modules moved to canonical groups with old-path shims
  - Package structure import compatibility tests
affects: [20-02, 20-03, 20-04, 20-05, 22-runtime-integration-regression-verification]

# Tech tracking
tech-stack:
  added: []
  patterns: [canonical-imports, compatibility-delegates, app-factory-pattern]

key-files:
  created:
    - backend/app/api/main.py
    - backend/app/core/config.py
    - backend/app/core/limiter.py
    - backend/app/db/database.py
    - backend/app/internal/scheduler_jobs.py
    - backend/app/utils/auth.py
    - backend/app/utils/ai_client.py
    - backend/app/utils/email_service.py
    - backend/app/socket/manager.py
    - backend/tests/test_package_structure.py
  modified:
    - backend/app/main.py
    - backend/app/config.py
    - backend/app/database.py
    - backend/app/limiter.py
    - backend/app/auth.py
    - backend/app/ai_client.py
    - backend/app/email_service.py
    - backend/app/scheduler_jobs.py
    - backend/app/websocket/manager.py

key-decisions:
  - "Keep app.main:app as compatibility delegate through Phase 22 to preserve uvicorn/Docker/supervisord references"
  - "Use canonical app.api.main for new imports while maintaining old-path shims for runtime safety"
  - "Preserve app.socket.manager and app.websocket.manager as dual paths for WebSocket manager singleton"

patterns-established:
  - "Pattern 1: Canonical imports in new code (app.core.config, app.db.database, etc.)"
  - "Pattern 2: One-line compatibility delegates with Phase 20/Phase 22 removal notes"
  - "Pattern 3: App factory pattern with create_app() and module-level app export"

requirements-completed: ["BACK-01", "BACK-03", "BACK-05"]

# Metrics
duration: 0min
completed: 2026-04-28T00:55:00Z
---

# Phase 20 Plan 01: Package Skeleton and App Runtime Target Summary

**Open WebUI-inspired backend package groups with canonical app factory and compatibility delegates preserving app.main:app**

## Performance

- **Duration:** 0min (work was already complete)
- **Started:** 2026-04-28T00:55:00Z
- **Completed:** 2026-04-28T00:55:00Z
- **Tasks:** 5
- **Files modified:** 15

## Accomplishments

- Backend package groups created (api/, core/, db/, internal/, socket/, utils/) with __init__.py files
- Canonical FastAPI app factory at app.api.main with create_app() and module-level app export
- Runtime-adjacent modules moved to canonical groups with Phase 20 compatibility delegates
- app.main:app preserved as compatibility delegate for uvicorn/Docker/supervisord
- Package import compatibility tests covering canonical and old-path imports

## Task Commits

Work was already complete at execution start. No task commits were made during this session.

**Plan metadata:** (pending commit)

## Files Created/Modified

### Created (Canonical Modules)

- `backend/app/api/main.py` - FastAPI app factory with create_app(), lifespan, router registration, CORS, rate limiter
- `backend/app/core/config.py` - Pydantic settings with environment variable configuration
- `backend/app/core/limiter.py` - Slowapi rate limiter singleton
- `backend/app/db/database.py` - SQLAlchemy engine, session, Base metadata, get_db dependency
- `backend/app/internal/scheduler_jobs.py` - APScheduler start/shutdown and job functions
- `backend/app/utils/auth.py` - JWT helpers, password hashing, user authentication
- `backend/app/utils/ai_client.py` - LiteLLM acompletion() wrapper
- `backend/app/utils/email_service.py` - Email sending for invites and KPI warnings
- `backend/app/socket/manager.py` - WebSocket ConnectionManager singleton
- `backend/tests/test_package_structure.py` - Import compatibility tests for canonical and old paths

### Modified (Compatibility Delegates)

- `backend/app/main.py` - Compatibility delegate re-exporting from app.api.main
- `backend/app/config.py` - Compatibility delegate re-exporting from app.core.config
- `backend/app/database.py` - Compatibility delegate re-exporting from app.db.database
- `backend/app/limiter.py` - Compatibility delegate re-exporting from app.core.limiter
- `backend/app/auth.py` - Compatibility delegate re-exporting from app.utils.auth
- `backend/app/ai_client.py` - Compatibility delegate re-exporting from app.utils.ai_client
- `backend/app/email_service.py` - Compatibility delegate re-exporting from app.utils.email_service
- `backend/app/scheduler_jobs.py` - Compatibility delegate re-exporting from app.internal.scheduler_jobs
- `backend/app/websocket/manager.py` - Compatibility delegate re-exporting from app.socket.manager

## Decisions Made

- Keep app.main:app as compatibility delegate through Phase 22 to preserve uvicorn/Docker/supervisord references
- Use canonical app.api.main for new imports while maintaining old-path shims for runtime safety
- Preserve app.socket.manager and app.websocket.manager as dual paths for WebSocket manager singleton
- All compatibility delegates include Phase 20/Phase 22 removal notes for clear lifecycle

## Deviations from Plan

None - plan executed exactly as written. Work was already complete at execution start.

## Issues Encountered

None - work was already complete and verified.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

Plan 20-02 (domain model package split) can proceed. Backend package skeleton is in place with canonical imports and compatibility delegates verified.

---
*Phase: 20-backend-package-restructure*
*Completed: 2026-04-28*
