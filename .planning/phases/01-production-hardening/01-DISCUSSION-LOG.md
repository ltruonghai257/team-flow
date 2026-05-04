# Phase 1: Production Hardening - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-22
**Phase:** 01-production-hardening
**Areas discussed:** Alembic startup behavior, SECRET_KEY validation scope, Rate limit storage backend, ALLOWED_ORIGINS env format

---

## Alembic Startup Behavior

| Option | Description | Selected |
|--------|-------------|----------|
| Run in lifespan hook (auto) | Call alembic upgrade head inside FastAPI lifespan — app refuses to start if migrations fail | ✓ |
| Startup command (not in app) | Run as shell command before uvicorn starts; app assumes DB is already migrated | |
| You decide | Claude picks whichever approach is cleaner | |

**User's choice:** Run in lifespan hook (auto)

| Option | Description | Selected |
|--------|-------------|----------|
| Crash hard — let the process die | Let exception propagate; container manager restarts | |
| Log error and exit cleanly | Catch exception, log clear error message, then sys.exit(1) | ✓ |
| You decide | Claude chooses the safest approach | |

**User's choice:** Log error and exit cleanly
**Notes:** Zero-touch for developers; readable error on failure rather than a cryptic exception trace.

---

## SECRET_KEY Validation Scope

| Option | Description | Selected |
|--------|-------------|----------|
| Always reject default — no exceptions | Reject if SECRET_KEY matches default string, regardless of environment | |
| Reject only in production | Add ENVIRONMENT=production var; reject default only when set | ✓ |
| Reject if key is too short or default | Validate both default string and minimum length, all environments | |

**User's choice:** Reject only in production

| Option | Description | Selected |
|--------|-------------|----------|
| ValueError raised from Settings model | pydantic @field_validator in config.py — raises before app loads | ✓ |
| Explicit check in lifespan hook | Check in main.py lifespan; log then sys.exit(1) | |

**User's choice:** ValueError raised from Settings model
**Notes:** Keeps validation co-located with config definition; pydantic raises clearly before any routes register.

---

## Rate Limit Storage Backend

| Option | Description | Selected |
|--------|-------------|----------|
| In-memory (simple, single-instance) | Default slowapi in-memory storage; no infrastructure needed | |
| Redis-backed | Shared across instances; requires Redis service | |
| In-memory for now, Redis later | Ship in-memory with TODO comment noting Redis upgrade path | ✓ |

**User's choice:** In-memory for now, Redis later

| Option | Description | Selected |
|--------|-------------|----------|
| Default slowapi 429 response | Standard HTTP 429 with slowapi's default message | ✓ |
| Custom JSON error body | Return {"detail": "Rate limit exceeded..."} consistent with FastAPI format | |

**User's choice:** Default slowapi 429 response
**Notes:** Keeps implementation minimal; Redis deferred until multi-instance Azure scaling is needed.

---

## ALLOWED_ORIGINS Env Format

| Option | Description | Selected |
|--------|-------------|----------|
| Comma-separated string | ALLOWED_ORIGINS=url1,url2 — simple for Azure App Settings | ✓ |
| JSON array string | ALLOWED_ORIGINS=["url1","url2"] — pydantic-settings parses natively | |

**User's choice:** Comma-separated string

| Option | Description | Selected |
|--------|-------------|----------|
| Yes — fallback to localhost list | If ALLOWED_ORIGINS not set, default to current localhost origins | ✓ |
| No — require explicit origins always | Require explicit setting in production; raise startup error if missing | |

**User's choice:** Yes — fallback to localhost list
**Notes:** Preserves current dev experience without requiring .env changes for existing developers.

---

## Claude's Discretion

- Alembic `env.py` configuration style (asyncio-compatible migration runner pattern)
- Whether to use slowapi decorator or dependency pattern — decided: decorator per endpoint

## Deferred Ideas

None raised during discussion.
