# Phase 1: Production Hardening - Context

**Gathered:** 2026-04-22
**Status:** Ready for planning

<domain>
## Phase Boundary

Fix all critical issues that block production deployment:
- Alembic migrations initialized and replacing `create_all`
- `SECRET_KEY` startup validation (rejects default in production)
- CORS origins read from `ALLOWED_ORIGINS` env var
- Rate limiting on auth and AI endpoints via `slowapi`
- `datetime.utcnow()` → `datetime.now(timezone.utc)` across all files

New capabilities (RBAC, dashboard, deployment) are out of scope — those belong to later phases.

</domain>

<decisions>
## Implementation Decisions

### Alembic Startup
- **D-01:** Run `alembic upgrade head` inside the FastAPI lifespan hook (not as a pre-launch shell command). App auto-migrates on every startup.
- **D-02:** On migration failure, catch the exception, log a clear error message, then `sys.exit(1)`. No silent failures.

### SECRET_KEY Validation
- **D-03:** Reject the default `"change-me-in-production"` value only when `ENVIRONMENT=production`. Developers can leave the default locally.
- **D-04:** Validation implemented as a pydantic `@field_validator` in `config.py` — raises `ValueError` with a clear message before the app loads. Add `ENVIRONMENT: str = "development"` to `Settings`.

### Rate Limiting (slowapi)
- **D-05:** Use in-memory storage backend (default slowapi) — no Redis infrastructure needed for now. Add a `# TODO: upgrade to Redis-backed storage for multi-instance` comment at the limiter definition.
- **D-06:** Rate limits as specified in requirements: auth endpoints 10 req/min per IP, AI endpoints 30 req/min per user.
- **D-07:** On limit exceeded, return the default slowapi 429 response (no custom JSON body).

### ALLOWED_ORIGINS
- **D-08:** Accept `ALLOWED_ORIGINS` as a comma-separated string env var (e.g., `https://teamflow.azurewebsites.net,https://teamflow-frontend.azurewebsites.net`). Parse by splitting on `,` and stripping whitespace.
- **D-09:** If `ALLOWED_ORIGINS` is not set, fall back to the current localhost list (`localhost:5173`, `localhost:4173`, `localhost:3000`). This preserves dev behavior without any `.env` changes.

### datetime Fix
- **D-10:** Replace all `datetime.utcnow()` calls with `datetime.now(timezone.utc).replace(tzinfo=None)` — preserves naive UTC storage in the DB (no schema change needed). Apply across all 6 files (tasks.py, ai.py, dashboard.py, notifications.py, websocket.py, auth.py, models.py).

### Claude's Discretion
- Alembic `env.py` configuration (sync vs async migration runner) — pick the standard asyncio-compatible pattern
- Whether to inline the limiter decorator or use a dependency — use decorator per endpoint (cleaner)

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Concerns (root cause documentation)
- `.planning/codebase/CONCERNS.md` items 1, 2, 11, 12 — exact issues being fixed and their risk descriptions

### Files being modified
- `backend/app/main.py` — CORS middleware, lifespan hook (migration + validation)
- `backend/app/config.py` — `SECRET_KEY` validator, `ALLOWED_ORIGINS` field, `ENVIRONMENT` field
- `backend/app/database.py` — replace `create_all` reference; Alembic integration point
- `backend/app/auth.py` — `utcnow()` replacement
- `backend/app/routers/tasks.py` — `utcnow()` replacement
- `backend/app/routers/ai.py` — `utcnow()` replacement + rate limiting
- `backend/app/routers/dashboard.py` — `utcnow()` replacement
- `backend/app/routers/notifications.py` — `utcnow()` replacement
- `backend/app/routers/websocket.py` — `utcnow()` replacement
- `backend/app/models.py` — `utcnow` column defaults replacement

### Requirements
- `.planning/REQUIREMENTS.md` REQ-01 — full acceptance criteria for this phase

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `pydantic-settings` `BaseSettings` already in use in `config.py` — `@field_validator` fits naturally
- `alembic>=1.14.0` already in `requirements.txt` — just needs `alembic init` and initial migration
- `slowapi` NOT in `requirements.txt` — must be added

### Established Patterns
- Error handling: exceptions propagate to FastAPI; lifespan errors should `sys.exit(1)` after logging
- Config: all settings read via `app.config.settings` singleton — `ALLOWED_ORIGINS` and `ENVIRONMENT` follow same pattern
- Routers: each router file handles its own imports — rate limiting decorators applied per-endpoint

### Integration Points
- `main.py` lifespan: migration call goes here, replacing `Base.metadata.create_all`
- `main.py` CORS middleware: replace hardcoded list with `settings.allowed_origins` (parsed list)
- Router files: `slowapi` limiter applied as `@limiter.limit("10/minute")` on auth route, `"30/minute"` on AI routes

</code_context>

<specifics>
## Specific Ideas

- No specific references provided — standard approaches apply.
- `datetime.now(timezone.utc).replace(tzinfo=None)` is the exact replacement form (keeps naive UTC for existing DB schema — no migration needed for this change).

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 01-production-hardening*
*Context gathered: 2026-04-22*
