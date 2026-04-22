# Concerns

*Mapped: 2026-04-22*

## Critical

### 1. No database migrations — `create_all` in production
- **File**: `backend/app/main.py:14`, `backend/app/database.py`
- **Risk**: Schema changes in production will not apply automatically. `create_all` only creates missing tables; it does NOT alter existing ones. Any column addition/rename will silently not apply on deployed DBs.
- **Impact**: Data loss risk, deployment failures on schema changes
- **Fix**: Set up Alembic migrations (`alembic init`, generate initial migration, replace `create_all` with `alembic upgrade head` in deployment)

### 2. Hardcoded default `SECRET_KEY`
- **File**: `backend/app/config.py:6`
- **Risk**: `SECRET_KEY: str = "change-me-in-production"` — if deployed without setting this env var, all JWT tokens are predictably forgeable
- **Impact**: Complete auth bypass in production
- **Fix**: Add startup validation that rejects the default value in non-dev environments

### 3. Zero test coverage
- **Files**: entire codebase
- **Risk**: Regressions undetectable, auth logic and AI parsing untested
- **Impact**: High risk for any future refactoring or dependency upgrades
- **Fix**: Add `pytest` + `pytest-asyncio` backend tests; `vitest` frontend tests (see TESTING.md)

## High

### 4. WebSocket state is purely in-memory
- **File**: `backend/app/websocket/manager.py`
- **Risk**: All channel subscriptions and assistant conversation history are lost on server restart or crash. Multi-instance deployment impossible without sticky sessions.
- **Impact**: Users lose assistant context on every server restart; channel subscription state desynchronizes
- **Fix**: Persist assistant history to DB (use existing `AIConversation`/`AIMessage` models); use Redis for channel sub state if multi-instance needed

### 5. N+1 query in `handle_dm_conversations`
- **File**: `backend/app/routers/websocket.py:310-336`
- **Risk**: For each DM conversation, two separate DB queries are fired (one for the other user, one for last message) inside a loop
- **Impact**: Performance degrades linearly with number of conversations; slow for active users
- **Fix**: Single JOIN query fetching all conversation data at once

### 6. `datetime.utcnow()` deprecated in Python 3.12+
- **Files**: `backend/app/models.py`, `backend/app/auth.py`, `backend/app/routers/websocket.py`, multiple others
- **Risk**: `datetime.utcnow()` is deprecated since Python 3.12 and will be removed in a future version; codebase uses Python 3.13
- **Impact**: Future Python upgrade or strict deprecation warnings will break the build
- **Fix**: Replace with `datetime.now(timezone.utc).replace(tzinfo=None)` for naive UTC storage

### 7. Tags stored as comma-separated string
- **File**: `backend/app/models.py:112` — `tags = Column(String, nullable=True)`
- **Risk**: No DB-level query/filter support for individual tags; searching by tag requires string matching
- **Impact**: Can't efficiently query "all tasks with tag X"; data integrity issues if tags contain commas
- **Fix**: Use PostgreSQL array type or a `tags` junction table

## Medium

### 8. `import json` inside hot loop
- **File**: `backend/app/routers/websocket.py:511`
- **Risk**: `import json` is called inside the WebSocket message loop on every message
- **Impact**: Negligible performance overhead (Python caches imports), but it's a code smell
- **Fix**: Move `import json` to the top of the file

### 9. `asyncio.get_event_loop()` deprecated
- **File**: `backend/app/routers/websocket.py:486,492`
- **Risk**: `asyncio.get_event_loop()` is deprecated in Python 3.10+; should use `asyncio.get_running_loop()`
- **Impact**: DeprecationWarning; will break in future Python versions
- **Fix**: Replace with `asyncio.get_running_loop()`

### 10. No input length limits on chat/AI content
- **Files**: `backend/app/routers/websocket.py`, `backend/app/routers/ai.py`
- **Risk**: Unlimited message content could cause excessive LLM token usage or DB storage abuse
- **Impact**: Cost and availability risk (unbounded LLM API calls)
- **Fix**: Add max content length validation (e.g. 4000 chars for chat, 10000 for AI messages)

### 11. `COOKIE_SECURE=True` default may break local dev
- **File**: `backend/app/config.py:10`
- **Risk**: `COOKIE_SECURE: bool = True` means the cookie will only be sent over HTTPS. In local dev (HTTP), auth will silently fail if this isn't overridden
- **Impact**: Developer friction; may cause confusing auth failures
- **Fix**: Default to `False`, document that production must set it to `True`; or use `ENVIRONMENT` var to auto-detect

### 12. No rate limiting on auth or AI endpoints
- **Files**: `backend/app/routers/auth.py`, `backend/app/routers/ai.py`
- **Risk**: No brute-force protection on login; no throttle on LLM API calls (cost exposure)
- **Impact**: Credential stuffing attacks; runaway LLM API costs
- **Fix**: Add `slowapi` or similar rate limiting middleware

### 13. Root-level `src/lib/components/` directory
- **File**: `/src/lib/components/tasks/` (at project root)
- **Risk**: Orphaned directory — not part of the frontend build (which lives under `frontend/src/`)
- **Impact**: Confusion for developers; possible stale components
- **Fix**: Delete or consolidate into `frontend/src/lib/components/`

## Low

### 14. No `.env` validation on startup
- **File**: `backend/app/config.py`
- **Risk**: Missing required env vars (e.g. `AI_MODEL` left blank) fail silently until first request
- **Impact**: Silent runtime failures rather than fast startup errors
- **Fix**: Add validators that raise on startup if critical vars are empty/default

### 15. Frontend has both `yarn.lock` and `bun.lock`
- **File**: `frontend/yarn.lock`, `frontend/bun.lock`
- **Risk**: Two package managers in same directory — could produce inconsistent installs
- **Impact**: CI/deployment confusion
- **Fix**: Pick one package manager and remove the other lock file

### 16. No CORS restriction on API in production
- **File**: `backend/app/main.py:31`
- **Risk**: `allow_origins` hardcoded to localhost origins only — needs to be environment-configurable for production deployment
- **Impact**: Cross-origin requests will fail in production; CORS origins not configurable without code change
- **Fix**: Read allowed origins from env var
