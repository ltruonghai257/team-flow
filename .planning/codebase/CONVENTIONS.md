# Coding Conventions

**Analysis Date:** 2024-05-18

## Naming Patterns

**Files:**
- **Backend:** Python files use `snake_case.py` (e.g., `performance.py`, `sub_teams.py`, `test_tasks.py`).
- **Frontend Components:** Svelte components use `PascalCase.svelte` (e.g., `KanbanCard.svelte`, `StatusTransitionEditor.svelte`).
- **Frontend Tests:** Playwright tests use `snake_case.spec.ts` or `kebab-case.spec.ts` (e.g., `sprint_board.spec.ts`, `task-modal.spec.ts`).

**Functions:**
- **Backend:** Python functions use `snake_case` (e.g., `def get_db():`, `def test_task_model_retains...`).
- **Frontend:** TypeScript/JavaScript functions use `camelCase` (e.g., `taskTypeValue`, `formatDate`, `isOverdue`).

**Variables:**
- **Backend:** `snake_case` for instances and variables. Constants likely use `UPPER_SNAKE_CASE`.
- **Frontend:** `camelCase` for state, props, and standard variables.

**Types & Classes:**
- **Backend & Frontend:** `PascalCase` for Python classes, Pydantic schemas, and TypeScript interfaces/types (e.g., `Project`, `Milestone`, `TaskOut`).

## Code Style

**Backend (Python/FastAPI):**
- **Type Hinting:** Fully typed using standard Python type hints and Pydantic models.
- **Decorators:** Extensive use of `@router.get`, `@router.post`, etc. 
- **Response Models:** Always defined explicitly in the decorator (e.g., `@router.get("/", response_model=List[ProjectOut])`).
- **Status Codes:** Explicit status codes are used for mutations (e.g., `status_code=201` for POST, `status_code=204` for DELETE).
- **ORM:** SQLAlchemy classes inherit from a declarative `Base` (`app.db.database.Base`).

**Frontend (SvelteKit):**
- **Component Structure:** `<script lang="ts">`, followed by HTML/Svelte markup, typically without `<style>` tags because Tailwind CSS is used.
- **Styling:** Tailwind CSS utility classes are used exclusively for styling.
- **Reactivity:** Using Svelte standard reactive declarations and event modifiers (`on:click|stopPropagation`).
- **Icons:** Uses `lucide-svelte` for iconography.

## Import Organization

**Backend:**
1. Standard library imports (e.g., `from datetime import datetime`).
2. Third-party packages (e.g., `from fastapi import APIRouter`, `from sqlalchemy import Column`).
3. Local application imports (e.g., `from app.models import Task`, `from app.db.database import get_db`).

**Frontend:**
1. Svelte/SvelteKit built-ins or libraries (`import { test, expect } from '@playwright/test';`).
2. Path aliases for internal utilities (`import { formatDate } from '$lib/utils';`).
3. Components (`import { Pencil } from 'lucide-svelte';`).

## Error Handling

**Backend Patterns:**
- FastAPI `HTTPException` is raised for business logic validation errors and resource not found errors.
- Structured details are returned in 422 errors for specific failures (e.g., `status_transition_blocked` with current and target status IDs).

## Logging

**Framework:** Standard console/print or Python logging module (implied, typical for FastAPI).

**Patterns:**
- Unhandled exceptions are caught by FastAPI's default handlers.

## Function Design

**Parameters:**
- Backend relies on dependency injection for request dependencies like `db_session: AsyncSession = Depends(get_db)`.

**Return Values:**
- Pydantic schemas (defined in `response_model`) strictly dictate the shape of API responses.

## Module Design

**Backend Exports:**
- Routers are initialized with `router = APIRouter(...)` and then mounted in `main.py`.

**Frontend Exports:**
- Components are exported implicitly by Svelte. Functions in utilities are explicitly exported using `export function` or `export const`.

---

*Convention analysis: 2024-05-18*
