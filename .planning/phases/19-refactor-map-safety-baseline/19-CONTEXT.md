# Phase 19: Refactor Map & Safety Baseline - Context

**Gathered:** 2026-04-27
**Status:** Ready for planning

<domain>
## Phase Boundary

Create the refactor playbook for TeamFlow's Open WebUI-inspired structure before any code moves happen. This phase documents the approved target structure, maps current backend/frontend files to target locations, identifies protected behavior that must not change, and establishes the pre-refactor verification commands and fallback rules.

This phase does not move code, rename packages, change API behavior, redesign UI, add dependencies, or alter database schema. It prepares Phase 20 (backend restructure), Phase 21 (frontend restructure), and Phase 22 (runtime integration and regression verification).

</domain>

<decisions>
## Implementation Decisions

### Target Structure Strictness
- **D-01:** Use an adapted Open WebUI style: keep `backend/app` and `frontend/src` as roots, then reorganize internal folders toward Open WebUI-style groups.
- **D-02:** Treat Open WebUI as structural inspiration, not an exact clone. Translate concepts into TeamFlow-native names instead of importing Open WebUI product vocabulary.
- **D-03:** Do not move the SvelteKit app to repo-root `src` during this milestone unless a later plan explicitly accepts the Docker/build/runtime impact.

### Backend Split Granularity
- **D-04:** Leave backend split depth to the planner's discretion after dependency mapping. Phase 19 should expose current coupling and target module candidates rather than forcing a full split up front.
- **D-05:** Temporary compatibility shims are allowed when they reduce migration risk, but they must be small, documented, and include removal notes.
- **D-06:** Backend restructuring should preserve FastAPI startup, router registration, auth/session behavior, rate limiting, CORS, scheduler startup/shutdown, WebSocket routing, health checks, Alembic history, and test imports.

### Frontend Split Granularity
- **D-07:** Prioritize scalable frontend structure, not the smallest possible move.
- **D-08:** The Phase 19 map may include a full frontend structure pass: shared library cleanup, route-local component extraction, component hierarchy cleanup, and type/API organization where it improves maintainability.
- **D-09:** Current route URLs and visual behavior must remain stable. This refactor must not become a UI redesign.
- **D-10:** Split API clients and shared types by feature domain, e.g. `src/lib/apis/{domain}.ts` and `src/lib/types/{domain}.ts`, while keeping request/auth behavior centralized.

### Safety Baseline
- **D-11:** Define the full available baseline as mandatory before code moves: backend tests, Alembic validation, frontend `check`, frontend production build, Docker/runtime command review, and manual smoke checklist.
- **D-12:** If a command is blocked by local environment, document the exact command, failure reason, and the next-best fallback check that was run instead. Blocked checks must not be skipped silently.
- **D-13:** Manual smoke coverage must include login/session, task board load, AI task input, WebSocket chat connection, scheduler/notifications, `/health`, and current Svelte routes.

### Migration Map Format
- **D-14:** Phase 19 output should be a refactor playbook, not only old-to-new tables.
- **D-15:** The playbook should include target structure, backend old-to-new map, frontend old-to-new map, protected behavior list, verification commands, sequencing notes, and temporary shim notes.
- **D-16:** Use separate backend and frontend tracks for sequencing. Phase 20 and Phase 21 should be independently plannable after Phase 19, and Phase 22 should handle integrated runtime verification and smoke checks.

### Agent's Discretion
- Exact backend module split depth for `models.py`, `schemas.py`, services, and domain packages, provided the playbook exposes coupling and lets Phase 20 choose the safest migration slices.
- Exact naming of TeamFlow-native target folders when multiple names fit the same Open WebUI-inspired concept.
- Exact frontend route-local component boundaries, provided route URLs and visual behavior remain unchanged and the result prioritizes scalable organization.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Roadmap and Requirements
- `.planning/ROADMAP.md` - Phase 19 goal, success criteria, and Phase 20/21/22 sequencing.
- `.planning/PROJECT.md` - v2.1 milestone intent, Open WebUI reference, preserved behavior list, and no-new-dependencies constraint.
- `.planning/REQUIREMENTS.md` - STRUCT requirements and v2.1 backend/frontend/runtime/verification constraints.
- `.planning/STATE.md` - Active milestone notes, user preference for Bun, runtime watch-outs, and existing v2.1 architecture decisions.

### Existing Codebase Maps
- `.planning/codebase/STRUCTURE.md` - Current backend/frontend layout and key file locations.
- `.planning/codebase/ARCHITECTURE.md` - FastAPI/SvelteKit architecture, router prefixes, auth flow, WebSocket flow, notification flow, and runtime shape.
- `.planning/codebase/TESTING.md` - Historical testing map; note that current repo now contains backend tests and frontend Playwright config, so Phase 19 should verify current commands rather than rely on this file alone.
- `.planning/codebase/CONVENTIONS.md` - Backend/frontend style conventions, API client pattern, store pattern, and UI conventions.

### Reference Structure
- `https://github.com/open-webui/open-webui` - Inspiration for package grouping and frontend shared-code organization. Use as a reference pattern, not as a product architecture to copy exactly.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `backend/app/main.py`: Current FastAPI entrypoint, router registration, middleware, lifespan, and scheduler startup/shutdown must be mapped before backend moves.
- `backend/app/routers/`: Existing one-router-per-domain layout is a good anchor for target backend grouping.
- `backend/app/models.py` and `backend/app/schemas.py`: Large shared modules likely need target-domain mapping, but actual split depth should wait for Phase 20 dependency analysis.
- `backend/app/services/`: Existing service package pattern already exists and can guide future service extraction.
- `backend/alembic/` and `backend/alembic.ini`: Migration history and env imports are protected behavior; Phase 19 must include them in the backend map and verification baseline.
- `backend/tests/`: Existing backend tests should become part of the mandatory pre-move baseline.
- `frontend/src/lib/api.ts`: Current centralized API client should be mapped toward feature API modules while keeping the shared request/auth behavior centralized.
- `frontend/src/lib/components/`, `frontend/src/lib/stores/`, `frontend/src/lib/utils.ts`, and `frontend/src/lib/websocket.ts`: Existing shared code groups are the natural input for Open WebUI-inspired `apis`, `components`, `stores`, `types`, and `utils` mapping.
- `frontend/src/routes/`: Route URLs must remain stable; large route files can be mapped to route-local components for scalability without changing URLs.
- `frontend/playwright.config.ts`, `frontend/package.json`, and `frontend/bun.lock`: Frontend verification should account for Bun preference and existing Playwright/mobile scripts.
- `Dockerfile`, `backend/Dockerfile`, `frontend/Dockerfile`, `docker-compose.yml`, and `supervisord.conf`: Runtime entrypoints must be reviewed before later path changes.

### Established Patterns
- Backend imports currently use the `app` package path and FastAPI routers under `backend/app/routers`.
- Frontend API calls use a centralized request wrapper with cookie credentials.
- SvelteKit routes are user-facing product routes and must not be renamed during structure work.
- WebSocket chat uses `/ws/chat`; REST APIs use `/api/*`.
- Notification delivery depends on scheduler jobs and frontend polling.
- The project prefers structural refactor slices over behavior changes.
- v2.1 should avoid new Python or frontend dependencies unless an existing import cannot be resolved safely without one.

### Integration Points
- Phase 19 playbook should map backend files, Alembic config, tests, scripts, Docker targets, and uvicorn targets together so Phase 20 does not miss runtime imports.
- Phase 19 playbook should map frontend shared modules, route files, route-local extraction candidates, API/type modules, Svelte config, Vite config, and package scripts together so Phase 21 can move code without route or UI changes.
- Phase 19 should explicitly reserve integrated Docker/Azure/runtime smoke verification for Phase 22 while still defining pre-move baseline commands.

</code_context>

<specifics>
## Specific Ideas

- The output should feel like a refactor playbook: target structure, file map, behavior guardrails, verification commands, sequencing notes, and shim policy.
- Frontend structure should prioritize scalability, even if that means mapping more than only `src/lib/api.ts`.
- Backend package roots should stay conservative (`backend/app`) to reduce runtime churn.
- Shims are acceptable only as temporary safety tools with documented removal notes.

</specifics>

<deferred>
## Deferred Ideas

None - discussion stayed within phase scope.

</deferred>

---

*Phase: 19-Refactor Map & Safety Baseline*
*Context gathered: 2026-04-27*
