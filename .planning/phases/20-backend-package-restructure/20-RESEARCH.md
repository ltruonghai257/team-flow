# Phase 20: Backend Package Restructure - Research

**Researched:** 2026-04-27
**Status:** Complete

## Research Question

What do we need to know to plan Phase 20, a behavior-preserving FastAPI backend package restructure inspired by Open WebUI?

## Inputs Read

- `.planning/phases/20-backend-package-restructure/20-CONTEXT.md`
- `.planning/phases/19-refactor-map-safety-baseline/19-CONTEXT.md`
- `.planning/phases/19-refactor-map-safety-baseline/19-01-PLAN.md`
- `.planning/phases/19-refactor-map-safety-baseline/19-02-PLAN.md`
- `.planning/phases/19-refactor-map-safety-baseline/19-03-PLAN.md`
- `.planning/phases/19-refactor-map-safety-baseline/19-04-PLAN.md`
- `.planning/ROADMAP.md`
- `.planning/PROJECT.md`
- `.planning/REQUIREMENTS.md`
- `.planning/STATE.md`
- `.planning/codebase/STACK.md`
- `.planning/codebase/ARCHITECTURE.md`
- `.planning/codebase/INTEGRATIONS.md`
- `.planning/codebase/STRUCTURE.md`
- `backend/app/main.py`
- `backend/alembic/env.py`
- `backend/tests/conftest.py`
- `backend/app/routers/`
- `backend/app/models.py`
- `backend/app/schemas.py`

## External Reference Check

Open WebUI's current backend package, `backend/open_webui`, uses a package root with top-level `main.py`, `config.py`, `env.py`, and `tasks.py`, plus folders including `models`, `routers`, `socket`, `utils`, `internal`, `migrations`, `storage`, `retrieval`, and `tools`.

The two most relevant reference patterns for TeamFlow are:

- `backend/open_webui/routers/` keeps domain-specific router files such as `auths.py`, `users.py`, `groups.py`, `chats.py`, `models.py`, `tasks.py`, `configs.py`, and `utils.py`.
- `backend/open_webui/models/` keeps one domain model module per resource area, such as `users.py`, `groups.py`, `chats.py`, `channels.py`, `files.py`, `folders.py`, `prompts.py`, `tools.py`, and `access_grants.py`.

Source references:

- `https://github.com/open-webui/open-webui/tree/main/backend/open_webui`
- `https://github.com/open-webui/open-webui/tree/main/backend/open_webui/models`
- `https://github.com/open-webui/open-webui/tree/main/backend/open_webui/routers`

Use these as structure inspiration only. Do not import Open WebUI product vocabulary or unrelated AI platform concepts into TeamFlow.

## Current TeamFlow Backend Shape

TeamFlow currently uses `backend/app` as the package root:

- `backend/app/main.py` creates the FastAPI app, configures CORS, rate limiting, lifespan, scheduler startup/shutdown, Alembic-on-startup, router registration, and `/health`.
- `backend/app/routers/` contains flat domain routers.
- `backend/app/models.py` is about 607 lines and contains all SQLAlchemy models and enums.
- `backend/app/schemas.py` is about 904 lines and contains all Pydantic schemas.
- Large routers include `performance.py` (~986 lines), `statuses.py` (~671 lines), `tasks.py` (~611 lines), and `websocket.py` (~533 lines).
- `backend/alembic/env.py` imports `app.config`, `app.database.Base`, and `app.models`.
- Backend tests import `app.main`, `app.models`, services, and auth utilities.
- Runtime references currently use `uvicorn app.main:app` in `backend/Dockerfile` and `supervisord.conf`.

## Key Planning Constraints

1. Phase 20 must preserve public API routes, WebSocket path `/ws/chat`, `/health`, auth/session behavior, CORS, rate limiting, scheduler lifecycle, and Alembic history.
2. Phase 20 should keep `backend/app` as root but introduce a new canonical app target with `create_app()` and module-level `app`.
3. `app.main:app`, `app.models`, and `app.schemas` are high-risk compatibility surfaces and should remain valid through Phase 22 unless planning finds a safer equivalent.
4. Phase 20 should update imports directly where safe, but keep shims for Alembic/runtime/tests/public surfaces.
5. If Phase 19's backend map/playbook artifacts are not completed by execution time, Phase 20 execution should stop and run Phase 19 first. Current repository state has Phase 19 plans, not completed map artifacts.
6. No new Python dependencies are required for this refactor.

## Recommended Target Shape

The most practical adapted shape is:

```text
backend/app/
  api/
    main.py              # canonical create_app() + exported app
  main.py                # compatibility delegate for app.main:app
  config.py              # compatibility delegate
  database.py            # compatibility delegate
  limiter.py             # compatibility delegate
  auth.py                # compatibility delegate if moved
  core/
    config.py
    limiter.py
  db/
    database.py
  internal/
    scheduler_jobs.py
  models/
    __init__.py          # aggregate exports for app.models
    users.py
    teams.py
    work.py
    notifications.py
    communication.py
    ai.py
  schemas/
    __init__.py          # aggregate exports for app.schemas
    users.py
    teams.py
    work.py
    notifications.py
    communication.py
    ai.py
    dashboard.py
  routers/
    *.py                 # flat domain routers by default
  services/
    reminder_notifications.py
  socket/
    manager.py
  websocket/
    manager.py           # compatibility delegate if socket/ is canonical
  utils/
    auth.py
    ai_client.py
    email_service.py
```

The exact file names can be adjusted during execution, but the plan should keep the same responsibilities and compatibility intent.

## Migration Strategy

Use small waves:

1. Create package skeleton and canonical app target first, while preserving `app.main:app`.
2. Move runtime-adjacent modules into groups with compatibility delegates and focused import checks.
3. Convert `models.py` into `models/` package modules with aggregate exports before changing broad imports.
4. Convert `schemas.py` into `schemas/` package modules with aggregate exports.
5. Update routers/tests/Alembic toward canonical imports and split only helper-heavy parts of large routers where the dependency map shows low risk.
6. Write the backend migration guide and run the verification floor.

Avoid a single all-at-once rename pass. It will be harder to debug than the move itself.

## Risk Register

| Risk | Impact | Mitigation |
|------|--------|------------|
| Alembic cannot find metadata after model split | migrations fail | Keep `app.models` aggregate import and update `backend/alembic/env.py` deliberately |
| `uvicorn app.main:app` breaks | backend cannot start | Keep `app.main` delegate and add canonical app target tests |
| Circular imports in model split | app import failure | Keep tightly coupled work-management models together |
| Routers keep importing removed top-level modules | runtime import failure | Use direct import updates plus targeted compatibility delegates |
| Large router split changes behavior | API regressions | Keep endpoints in flat routers by default; extract only helpers where low risk |
| Tests validate old paths only | new structure not protected | Move most tests toward canonical imports, but keep focused old-path compatibility checks |

## Verification Architecture

Phase 20 should use a backend-only validation loop:

- Quick feedback after risky slices:
  - `rtk proxy python -m compileall backend/app`
  - focused import checks for canonical and compatibility surfaces
  - targeted pytest files when touched
- Final floor:
  - `rtk pytest backend/tests -q`
  - Alembic validation from `backend/`, preferring `rtk proxy alembic -c alembic.ini heads` and an upgrade/import check where the local DB configuration allows it
  - uvicorn `/health` startup smoke, plus router registration/import check
- If a command is blocked by environment, document the exact command, blocker, and next-best fallback in the migration guide.

## Planning Recommendation

Create five plans:

1. Package skeleton, canonical app factory, runtime-adjacent module relocation, and compatibility delegates.
2. Domain model package split with `app.models` aggregate export and Alembic metadata safety.
3. Domain schema package split with `app.schemas` aggregate export.
4. Router/service/import migration and selected helper extraction for large routers.
5. Backend migration guide, compatibility tests, Alembic/runtime smoke, and final verification.

## RESEARCH COMPLETE
