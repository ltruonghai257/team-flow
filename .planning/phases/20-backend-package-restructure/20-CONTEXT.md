# Phase 20: Backend Package Restructure - Context

**Gathered:** 2026-04-27
**Status:** Ready for planning

<domain>
## Phase Boundary

Reorganize TeamFlow's FastAPI backend into a maintainable Open WebUI-inspired package layout while preserving existing API behavior. This phase moves backend code, updates imports, adjusts router registration and app entrypoints, preserves Alembic/test/runtime compatibility, and documents old-to-new backend paths.

This phase does not change product behavior, public API paths, auth/session semantics, database schema design, frontend structure, UI behavior, Docker/Azure final runtime integration, or broad user-flow smoke coverage. Integrated runtime and end-to-end regression verification belongs to Phase 22.

</domain>

<decisions>
## Implementation Decisions

### Package Shape
- **D-01:** Keep `backend/app` as the backend package root.
- **D-02:** Reorganize backend internals into Open WebUI-inspired groups, using Open WebUI-leaning names translated where TeamFlow needs clearer naming.
- **D-03:** Move runtime-adjacent modules such as config, database, limiter, scheduler jobs, AI client, and email service into appropriate groups during Phase 20 rather than leaving them all at top level.
- **D-04:** Introduce a new canonical app target with a hybrid `create_app()` factory plus exported module-level `app`.
- **D-05:** Keep `app.main:app` as a temporary compatibility delegate so existing uvicorn, Docker, supervisor, Alembic, and test assumptions do not break abruptly.
- **D-06:** Keep routers flat by domain by default, but allow splitting very large routers such as tasks, statuses, performance, or websocket if dependency mapping supports a safe split.

### Model and Schema Split
- **D-07:** Split `models.py` by domain incrementally with aggregate exports or a compatibility import surface so migration risk stays controlled.
- **D-08:** Split `schemas.py` by model/domain area, generally matching model domains.
- **D-09:** Keep tightly coupled model clusters together when needed, especially work-management relationships across projects, milestones, sprints, tasks, statuses, and related enums.
- **D-10:** Keep temporary aggregate schema exports so old imports like `from app.schemas import TaskOut` can continue during the migration.
- **D-11:** Let the planner decide whether the original giant files become pure facades by the end of Phase 20 or retain hard-to-split leftovers temporarily.

### Compatibility Shims
- **D-12:** Planner decides shim surfaces per module based on dependency mapping and verification risk.
- **D-13:** Default bias is to update imports directly to canonical paths and add shims mainly for Alembic, runtime, tests, or clearly public compatibility surfaces.
- **D-14:** Document shims with short inline comments plus a backend migration guide.
- **D-15:** Remove low-risk shims before Phase 20 ends if verification shows they are unnecessary.
- **D-16:** Keep high-risk compatibility surfaces such as `app.main`, `app.models`, and `app.schemas` through Phase 22 runtime/regression verification unless planning finds a safer alternative.
- **D-17:** Test import migration is at the planner's discretion, with a bias toward canonical paths plus focused compatibility coverage for critical old surfaces.

### Verification Floor
- **D-18:** Phase 20 completion requires backend tests, Alembic validation, and uvicorn `/health` startup smoke.
- **D-19:** Run focused verification after risky migration slices, especially model/schema moves, app target changes, Alembic path changes, and runtime-adjacent module moves; run the full verification floor at the end.
- **D-20:** Include a concise backend migration guide with old-to-new paths, compatibility shims, and verification commands.
- **D-21:** Phase 20 smoke should cover `/health` plus router registration/import checks. Broader user-flow smoke checks such as login/session, task board behavior, WebSocket chat flow, scheduler/notifications behavior, and frontend integration remain Phase 22 scope.
- **D-22:** If an exact verification command is blocked by the local environment, document the command, the exact blocker, and the next-best fallback check that was run.

### Agent's Discretion
- Exact group names and file boundaries, provided they remain Open WebUI-inspired and TeamFlow-readable.
- Exact router split candidates, provided only genuinely large/high-coupling routers are split and behavior stays stable.
- Exact model cluster boundaries, provided relationship cycles and Alembic metadata registration remain safe.
- Exact shim set, test import migration sequence, and final facade cleanup timing within the rules above.

</decisions>

<specifics>
## Specific Ideas

- The new app entrypoint should improve testability with `create_app()` while preserving module-level `app` for uvicorn compatibility.
- The refactor should feel like a structural cleanup, not a product rewrite or an exact Open WebUI clone.
- The migration guide should be useful to Phase 22 and future contributors: concise path map, known shims, removal notes, and commands actually run.
- `.planning/REQUIREMENTS.md` currently contains stale v2.1 traceability that shifts phase numbers, but `.planning/ROADMAP.md`, `.planning/PROJECT.md`, and Phase 19 context identify Phase 20 as Backend Package Restructure. Downstream agents should treat the roadmap Phase 20 entry as source of truth.

</specifics>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Roadmap and Requirements
- `.planning/ROADMAP.md` - Phase 20 goal, dependency on Phase 19, success criteria, and Phase 20/21/22 sequencing.
- `.planning/PROJECT.md` - v2.1 milestone intent, Open WebUI reference, preserved behavior list, and no-new-dependencies constraint.
- `.planning/REQUIREMENTS.md` - BACK requirements and v2.1 backend/frontend/runtime/verification constraints; note stale traceability table and defer to ROADMAP for phase numbering.
- `.planning/STATE.md` - Active milestone notes, Bun preference, runtime watch-outs, and v2.1 architecture decisions.

### Prior Phase Context
- `.planning/phases/19-refactor-map-safety-baseline/19-CONTEXT.md` - Locked Phase 19 decisions for adapted Open WebUI structure, protected behavior, shim policy, and verification baseline.

### Existing Codebase Maps
- `.planning/codebase/STACK.md` - Backend stack, runtime, libraries, configuration, and package management context.
- `.planning/codebase/ARCHITECTURE.md` - Current FastAPI architecture, router prefixes, auth flow, WebSocket flow, notification flow, and runtime shape.
- `.planning/codebase/INTEGRATIONS.md` - Alembic, JWT/cookie auth, LiteLLM, WebSocket, scheduler, and frontend-backend proxy integration notes.

### Reference Structure
- `https://github.com/open-webui/open-webui` - Inspiration for backend grouping and app/package structure. Use as a reference pattern, not as a product architecture to copy exactly.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `backend/app/main.py`: Current FastAPI app object, lifespan, router registration, CORS middleware, rate limiter exception handler, scheduler startup/shutdown, Alembic upgrade call, and `/health` endpoint.
- `backend/app/routers/`: Existing flat domain router package; good default shape to preserve unless splitting the heaviest routers is justified.
- `backend/app/models.py`: Large SQLAlchemy model/enums module; target for domain split with aggregate exports and careful Alembic metadata registration.
- `backend/app/schemas.py`: Large Pydantic schema module; target for domain split with temporary aggregate exports.
- `backend/app/config.py`, `database.py`, `limiter.py`, `scheduler_jobs.py`, `ai_client.py`, `email_service.py`: Runtime-adjacent modules to move into clearer groups during Phase 20.
- `backend/app/services/`: Existing service package precedent, including reminder notification logic.
- `backend/app/websocket/manager.py` and `backend/app/routers/websocket.py`: WebSocket manager and router must preserve `/ws/chat` behavior while fitting the new package shape.
- `backend/alembic/env.py`: Imports `app.config`, `app.database.Base`, and `app.models`; must continue to locate metadata after model/package moves.
- `backend/tests/`: Existing backend tests import `app.main`, `app.models`, `app.schemas`, and services; these are a key compatibility and canonical-path migration surface.

### Established Patterns
- Backend imports currently use `from app...` throughout backend source, Alembic, scripts, and tests.
- FastAPI routers are registered explicitly in `main.py`; REST routes live under `/api/*`, WebSocket routes under `/ws`.
- Auth/session behavior depends on JWT in HttpOnly cookies plus Bearer fallback.
- Scheduler lifecycle is managed by FastAPI lifespan and must remain behaviorally unchanged.
- Alembic history should not be rewritten; metadata import paths must adapt to the new package shape.
- v2.1 structural work should avoid new Python dependencies unless an import cannot be resolved safely without one.

### Integration Points
- New canonical app target must be wired without breaking existing `uvicorn app.main:app` references in `backend/Dockerfile` and `supervisord.conf`.
- Alembic `env.py` must import the new metadata surface or a compatibility facade and validate migrations against the refactored paths.
- Tests should either migrate to canonical paths or intentionally cover compatibility paths according to the planner's sequence.
- Backend migration guide should connect Phase 20 output to Phase 22 runtime/Docker/Azure verification.

</code_context>

<deferred>
## Deferred Ideas

None - discussion stayed within phase scope.

</deferred>

---

*Phase: 20-backend-package-restructure*
*Context gathered: 2026-04-27*
