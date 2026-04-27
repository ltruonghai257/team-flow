<!-- refreshed: [YYYY-MM-DD] -->
# Architecture

**Analysis Date:** [YYYY-MM-DD]

## System Overview

```text
┌─────────────────────────────────────────────────────────────┐
│                      Client Layer                            │
├──────────────────┬──────────────────┬───────────────────────┤
│    SvelteKit     │  Svelte Stores   │   Lib / Components    │
│  `frontend/src/` │ `frontend/src/lib/stores/` │ `frontend/src/lib/components/` │
└────────┬─────────┴────────┬─────────┴──────────┬────────────┘
         │                  │                     │
         ▼                  ▼                     ▼
┌─────────────────────────────────────────────────────────────┐
│                      API Gateway (FastAPI)                   │
│         `backend/app/api/main.py` & `backend/app/routers/`   │
└─────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│  Database / ORM (SQLAlchemy)                                 │
│  `backend/app/db/database.py` & `backend/app/models.py`      │
└─────────────────────────────────────────────────────────────┘
```

## Component Responsibilities

| Component | Responsibility | File |
|-----------|----------------|------|
| SvelteKit Routes | Page routing, page-level data fetching, and layouts | `frontend/src/routes/` |
| Svelte Stores | Global state management (auth, notifications, teams) | `frontend/src/lib/stores/` |
| API Clients | Typing and handling HTTP requests to backend | `frontend/src/lib/apis/` |
| FastAPI Routers | Endpoint definitions, request validation, basic logic | `backend/app/routers/` |
| SQLAlchemy Models | Database schema definitions | `backend/app/models.py` |
| Pydantic Schemas | Request/Response validation and serialization | `backend/app/schemas/` |

## Pattern Overview

**Overall:** Client-Server SPA (Single Page Application) with RESTful API

**Key Characteristics:**
- **Asynchronous backend:** Heavy reliance on `async`/`await` in Python with Async SQLAlchemy and FastAPI.
- **Component-driven UI:** SvelteKit frontend utilizing reusable Svelte components.
- **Stateful stores:** Client-side caching and global state using Svelte stores (`authStore`, `notificationStore`).
- **Dependency Injection:** FastAPI `Depends` is used pervasively for DB sessions (`get_db`) and Auth (`get_current_user`).

## Layers

**Frontend Presentation Layer:**
- Purpose: UI rendering, user interaction, routing.
- Location: `frontend/src/routes/` and `frontend/src/lib/components/`
- Contains: `.svelte` and `.ts` files.
- Depends on: API clients, Svelte stores.
- Used by: End users.

**Frontend Data/State Layer:**
- Purpose: Managing application state, fetching data, handling logic outside UI.
- Location: `frontend/src/lib/stores/` and `frontend/src/lib/apis/`
- Contains: Typescript API clients and Svelte readable/writable stores.
- Depends on: Backend API.
- Used by: Presentation Layer.

**Backend API Layer:**
- Purpose: Expose endpoints, enforce authentication/authorization, parse requests.
- Location: `backend/app/routers/`
- Contains: FastAPI APIRouters.
- Depends on: Core/Services, Models.
- Used by: Frontend Data Layer.

**Backend Data Layer:**
- Purpose: Database interactions, transaction management.
- Location: `backend/app/db/` and `backend/app/models.py`
- Contains: SQLAlchemy ORM definitions and sessions.
- Depends on: PostgreSQL (implied by asyncpg/psycopg dependency).
- Used by: API Layer.

## Data Flow

### Primary Request Path (e.g., Fetching Tasks)

1. Svelte Component calls API method (`frontend/src/lib/apis/tasks.ts`)
2. FastAPI Router receives request (`backend/app/routers/tasks.py`)
3. FastAPI dependency injects DB session and verifies user (`get_db`, `get_current_user`)
4. Router queries DB via SQLAlchemy (`select(Task).where(...)`)
5. Data returned as Pydantic model response (`TaskOut`)
6. Frontend updates store/component state.

## Key Abstractions

**FastAPI Dependency Injection:**
- Purpose: Reusable logic for endpoints (Auth, DB, Limiting).
- Examples: `backend/app/db/database.py:get_db`, `backend/app/utils/auth.py:get_current_user`
- Pattern: Dependency Injection.

**Svelte Stores:**
- Purpose: Global, reactive state.
- Examples: `frontend/src/lib/stores/auth.ts`, `frontend/src/lib/stores/notifications.ts`
- Pattern: Observable / Publish-Subscribe.

## Entry Points

**Frontend Application:**
- Location: `frontend/src/app.html` & `frontend/src/routes/+layout.svelte`
- Triggers: Browser request.
- Responsibilities: Initialization, Auth check, Layout rendering.

**Backend Application:**
- Location: `backend/app/api/main.py`
- Triggers: Uvicorn/ASGI server startup.
- Responsibilities: Configure CORS, register routers, start schedulers, handle migrations.

## Architectural Constraints

- **Threading:** Asynchronous event loops in both JS (browser) and Python (asyncio/FastAPI).
- **Global state:** Handled locally in frontend via Svelte stores. Backend is mostly stateless across requests.
- **Database Sessions:** Managed exclusively via FastAPI Dependency Injection (`get_db()`) to ensure proper connection pooling and cleanup.

## Anti-Patterns

### Logic in Routers

**What happens:** Business logic and complex queries are sometimes written directly in `backend/app/routers/*.py`.
**Why it's wrong:** It makes testing difficult without a full HTTP context and reduces code reusability.
**Do this instead:** Extract complex operations into a dedicated `backend/app/services/` layer (e.g., `backend/app/services/task_service.py`).

## Error Handling

**Strategy:** Exception-based with unified HTTP error responses.

**Patterns:**
- Backend: Raising FastAPI `HTTPException` which gets translated to JSON error responses.
- Frontend: Try-catch blocks in API clients or components, often feeding into a toast notification system (`svelte-sonner`).

## Cross-Cutting Concerns

**Logging:** Standard Python `logging` module configured in the backend.
**Validation:** Pydantic schemas in the backend (`backend/app/schemas/`).
**Authentication:** JWT-based or Session-based, validated via `Depends(get_current_user)` in FastAPI.
