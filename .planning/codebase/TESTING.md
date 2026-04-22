# Testing

*Mapped: 2026-04-22*

## Current State

**No tests exist.** Neither the backend nor the frontend has any test files, test directories, or testing framework configuration.

```
backend/  — no tests/ directory, no test_*.py files
frontend/ — no tests/ directory, no *.test.ts / *.spec.ts files
```

## Backend — Testing Gap

### No test infrastructure found:
- No `pytest` in `requirements.txt`
- No `pytest.ini`, `pyproject.toml`, or `setup.cfg`
- No `conftest.py`
- No `tests/` directory

### What would be needed to add tests:
- `pytest>=8.x` + `pytest-asyncio` for async test support
- `httpx` (already in requirements) for `TestClient` / `AsyncClient`
- `pytest-cov` for coverage
- Database: either SQLite in-memory for unit tests or a dedicated test Postgres DB

### Recommended test patterns for this codebase:
```python
# Integration test pattern (FastAPI + async DB)
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_create_task():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/api/tasks/", json={"title": "Test task"})
        assert response.status_code == 201
```

### High-value test targets:
- `backend/app/auth.py` — `get_current_user`, `get_user_from_cookie` (auth boundary)
- `backend/app/routers/tasks.py` — AI parse endpoint (JSON extraction / coercion logic)
- `backend/app/scheduler_jobs.py` — `process_due_notifications` (time-sensitive logic)
- `backend/app/schemas.py` — `_to_naive_utc` validator (datetime normalization)

## Frontend — Testing Gap

### No test infrastructure found:
- No `vitest` or `playwright` in `package.json`
- No `*.test.ts`, `*.spec.ts`, or `*.test.svelte` files
- No `playwright.config.ts`

### What would be needed to add tests:
- `vitest` + `@testing-library/svelte` for unit/component tests
- `@playwright/test` for E2E tests
- `jsdom` or `happy-dom` as test environment

### High-value test targets:
- `frontend/src/lib/api.ts` — request wrapper (error handling, credentials)
- `frontend/src/lib/websocket.ts` — `ChatWebSocket` (reconnect logic, heartbeat)
- `frontend/src/lib/stores/auth.ts` — login/logout/loadMe flows
- `frontend/src/lib/stores/notifications.ts` — polling logic

## Testing Priority Recommendations

Given zero test coverage, recommended order:
1. **Backend auth tests** — highest security risk
2. **Task AI-parse endpoint** — complex logic with external dependency (LiteLLM)
3. **Notification scheduler** — time-dependent, hard to debug manually
4. **Frontend auth store** — guards all protected routes
