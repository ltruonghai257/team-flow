---
plan: "19-02"
phase: "19-refactor-map-safety-baseline"
status: complete
completed: "2026-04-27"
---

# Plan 19-02 Summary: Backend Target Map

## What Was Built

Created `19-BACKEND-MAP.md` — the TeamFlow-native backend target structure, current-to-target file map, and Phase 20 migration slices.

## Tasks Completed

- **19-02-01:** Documented backend target structure keeping `backend/app` as root with Open WebUI-inspired groupings
- **19-02-02:** Mapped all current backend files to target locations including every router, models.py, schemas.py, alembic, tests, scripts, services, websocket, and runtime references
- **19-02-03:** Defined 8 backend migration slices (B0–B7) with dependencies and per-slice verification

## Key Outputs

- Backend target structure covering all required groups: routers, models/domain, schemas, config, migrations, utils, websocket, scripts
- Full current-to-target table for 30+ backend files including all 17 routers, models.py (monolith default + domain split option), schemas.py (monolith default + domain split option), alembic/env.py, tests, runtime references
- Domain split candidates listed for models (8 modules) and schemas (14 modules) — Phase 20 discretion
- B0–B7 migration slices with explicit dependencies and protected behavior per slice
- Open WebUI groups excluded from TeamFlow listed explicitly

## Deviations

None. No backend code was moved or modified.
