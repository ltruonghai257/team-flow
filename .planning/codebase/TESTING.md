# Testing Patterns

**Analysis Date:** 2024-05-18

## Test Framework

**Backend:**
- **Runner:** `pytest` with `pytest-asyncio` for async support.
- **Assertion Library:** Built-in Python `assert`.
- **Database:** Uses `sqlite+aiosqlite` configured in memory or local test db for fast isolation during tests.

**Frontend:**
- **Runner:** `@playwright/test` for E2E and component testing.
- **Assertion Library:** Playwright's `expect` matchers.
- **Config:** `frontend/playwright.config.ts`

**Run Commands:**
```bash
# Frontend Playwright (Mobile Chrome)
yarn test:mobile              # Run mobile tests headlessly
yarn test:mobile:ui           # Run mobile tests with Playwright UI
```

## Test File Organization

**Location:**
- **Backend:** `backend/tests/` (e.g., `backend/tests/test_tasks.py`).
- **Frontend:** `frontend/tests/` and mobile-specific tests in `frontend/tests/mobile/` (e.g., `frontend/tests/mobile/task-modal.spec.ts`).

**Naming:**
- **Backend:** Files prefixed with `test_` (e.g., `test_projects.py`, `test_sprints.py`).
- **Frontend:** Files suffixed with `.spec.ts` (e.g., `sprint_board.spec.ts`).

## Test Structure

**Backend Suite Organization:**
```python
@pytest.mark.asyncio
async def test_task_sprint_id_persistence(db_session):
    """SPRINT-03: Task create/edit accepts and persists sprint_id"""
    # Create test data
    sub_team = SubTeam(name="Test Team")
    # ... session adds and commits ...

    # Act
    task = Task(...)
    
    # Assert
    assert task.sprint_id == sprint.id
```

**Frontend Suite Organization:**
```typescript
import { test, expect } from '@playwright/test';
import { loginAs } from '../helpers/auth';

test.describe('Task modal on mobile', () => {
    test.use({ viewport: { width: 375, height: 812 } });

    test.beforeEach(async ({ page }) => {
        await loginAs(page);
    });

    test('task modal is visible', async ({ page }) => {
        await page.goto('/tasks');
        await page.getByRole('button', { name: /new task/i }).click();
        const modal = page.locator('.max-h-\\[92dvh\\]');
        await expect(modal).toBeVisible();
    });
});
```

## Mocking and Fixtures

**Backend Fixtures:**
- Defined in `backend/tests/conftest.py`.
- **`db_session`**: Provides an `AsyncSession` with an automatically provisioned and torn-down SQLite database.
- **`async_client`**: An `httpx.AsyncClient` that overrides the FastAPI `get_db` dependency to use the test `db_session`.
- **Domain Fixtures**: `sub_team`, `user_with_sub_team` are provided to quickly bootstrap users.

**Frontend Helpers:**
- Uses helper functions to encapsulate common test setups, e.g., `loginAs(page)` imported from `../helpers/auth`.

## Common Patterns

**Async Testing (Backend):**
- Mark tests with `@pytest.mark.asyncio`.
- Heavily relies on `await db_session.commit()` and `await db_session.refresh(model)` after inserting test data to access DB-generated properties (like `.id`).

**API Testing (Backend):**
- Use the injected `async_client: AsyncClient` fixture.
- Pattern involves a `_login` helper to obtain a JWT token, which is passed in the `Authorization` header of the HTTPX client for protected routes.

**Error Testing (Backend):**
```python
response = await async_client.patch(f"/api/tasks/{task_id}", json=payload, headers=headers)
assert response.status_code == 422
detail = response.json()["detail"]
assert detail["code"] == "status_transition_blocked"
```

**Known Issues/Pending Implementation:**
- Uses `@pytest.mark.xfail(reason="...")` for tests covering features that are intentionally missing or scheduled for later phases (e.g., `test_moving_to_is_done_status_sets_completed_at`).

## Test Types

**Integration/Unit Tests (Backend):**
- Comprehensive tests hitting local endpoints and validating DB state. Evaluates exact JSON responses and status codes.

**E2E Tests (Frontend):**
- Extensive focus on responsive and mobile scenarios (e.g., simulating `Pixel 5` viewport dimensions).
- Validates CSS classes (`.max-h-[92dvh]`), DOM layout, and scrollability properties via client-side evaluation (`el.scrollTop`).

---

*Testing analysis: 2024-05-18*
