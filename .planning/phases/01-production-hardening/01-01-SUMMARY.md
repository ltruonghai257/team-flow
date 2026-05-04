# Plan 01-01 Summary: Config Hardening + Rate Limiting

**Status:** Complete  
**Completed:** 2026-04-22

## What Was Built

- `backend/app/limiter.py` — extracted `Limiter` singleton to avoid circular imports
- `backend/app/config.py` — added `ENVIRONMENT`, `ALLOWED_ORIGINS` fields; `@field_validator` on `SECRET_KEY` rejects default in production; `cors_origins` property parses comma-separated origins
- `backend/app/main.py` — initialized SlowAPI middleware + 429 handler; CORS now uses `settings.cors_origins`
- `backend/app/routers/auth.py` — `@limiter.limit("10/minute")` on POST `/api/auth/token`
- `backend/app/routers/ai.py` — `@limiter.limit("30/minute")` on all 6 AI endpoints
- `backend/requirements.txt` — added `slowapi>=0.1.9`

## Decisions Made

- Limiter defined in `app.limiter` module (not `app.main`) to prevent circular imports when routers import it
- In-memory rate limit storage (default slowapi) — TODO comment left for Redis upgrade

## Verification

- `grep -q 'limiter.limit' backend/app/routers/auth.py` ✓
- `grep -q 'cors_origins' backend/app/main.py` ✓
- `grep -q 'ENVIRONMENT' backend/app/config.py` ✓
