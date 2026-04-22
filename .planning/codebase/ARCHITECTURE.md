# Architecture

*Mapped: 2026-04-22*

## Pattern

**Full-stack monorepo with decoupled frontend/backend.**

- Backend: FastAPI REST API + WebSocket server (async Python)
- Frontend: SvelteKit SPA with server-side routing
- Database: PostgreSQL (single schema, auto-migrated on startup)
- Communication: REST over HTTP + multiplexed WebSocket for real-time

## Layers

```
┌─────────────────────────────────────────┐
│  Frontend (SvelteKit / Svelte 5)        │
│  Routes → Components → Stores → API    │
└──────────────┬──────────────────────────┘
               │ HTTP REST /api/*
               │ WebSocket  /ws/chat
┌──────────────▼──────────────────────────┐
│  Backend (FastAPI)                      │
│  Routers → Auth → DB Session           │
│  WebSocket Manager (in-memory)         │
│  APScheduler (background jobs)         │
└──────────────┬──────────────────────────┘
               │ asyncpg / SQLAlchemy async
┌──────────────▼──────────────────────────┐
│  PostgreSQL 16                          │
└─────────────────────────────────────────┘
```

## Backend Components

### Entry Point
`backend/app/main.py` — creates `FastAPI` app, registers all routers, sets up CORS middleware, manages lifespan (DB init + scheduler start/stop)

### Routers (`backend/app/routers/`)
Each router is a self-contained module with its own `APIRouter` prefix:

| Router | Prefix | Responsibility |
|--------|--------|----------------|
| `auth.py` | `/api/auth` | Login (form), register, `/me`, logout |
| `users.py` | `/api/users` | User CRUD, list team |
| `projects.py` | `/api/projects` | Project CRUD |
| `milestones.py` | `/api/milestones` | Milestone CRUD, filter by project |
| `tasks.py` | `/api/tasks` | Task CRUD, filters, AI-parse endpoint |
| `schedules.py` | `/api/schedules` | Calendar event CRUD with date range filter |
| `notifications.py` | `/api/notifications` | Reminder CRUD, bulk set, dismiss |
| `ai.py` | `/api/ai` | Persistent AI conversations + quick-chat via LiteLLM |
| `chat.py` | `/api/chat` | Channel management |
| `dashboard.py` | `/api/dashboard` | Aggregated stats |
| `websocket.py` | `/ws` | Real-time WebSocket (chat, presence, assistant streaming) |

### Auth Flow
1. `POST /api/auth/token` — returns JWT, sets `access_token` HttpOnly cookie
2. Subsequent requests: `get_current_user` dependency reads cookie OR Bearer header
3. WebSocket: `get_user_from_cookie` validates token during handshake

### WebSocket Architecture (`backend/app/websocket/manager.py`)
- `ConnectionManager` singleton — in-memory, multi-device per user
- Tracks: active sockets, channel subscriptions, assistant history per connection, cancel events for streaming
- Message routing: type-dispatched JSON messages (`type` field)

### Database Session
`get_db()` — async generator providing `AsyncSession`, auto-commit on success, rollback on exception

## Frontend Components

### Routing (`frontend/src/routes/`)
SvelteKit file-based routing:
- `/` — Dashboard
- `/projects` — Project list
- `/tasks` — Task board (Kanban + Agile sprint views)
- `/milestones` — Milestone tracker
- `/team` — Team management + presence
- `/schedule` — Calendar scheduler
- `/ai` — AI assistant chat
- `/login`, `/register` — Auth pages

### State Management (`frontend/src/lib/stores/`)
Svelte writable stores:
- `auth.ts` — `authStore` (user, loading), `currentUser` derived, `isLoggedIn` derived
- `chat.ts` — chat channel/DM state
- `notifications.ts` — notification polling store

### API Client (`frontend/src/lib/api.ts`)
Thin fetch wrapper with `credentials: 'include'` for cookie auth. Organized by domain: `auth`, `users`, `projects`, `milestones`, `tasks`, `schedules`, `notifications`, `ai`, `chat`, `dashboard`.

### WebSocket Client (`frontend/src/lib/websocket.ts`)
`ChatWebSocket` singleton — single multiplexed WS connection, listener pattern, heartbeat + reconnect.

## Data Flow

### REST Request
`Component` → `api.ts request()` → `fetch /api/*` → FastAPI router → `get_current_user` → DB → response

### WebSocket Message
`Component` → `chatWS.send({type, ...})` → `/ws/chat` → `websocket.py` dispatch → `ConnectionManager` → broadcast to target users

### Notification Flow
`APScheduler` (60s) → `process_due_notifications()` → DB query pending → flip to `sent` → frontend polling store detects new → toast notification

## Key Design Decisions

- **No Alembic migrations in use yet** — schema created via `create_all` on startup (dev-friendly, not production-safe)
- **In-memory WebSocket state** — channel subs and assistant history lost on server restart; not persisted to DB
- **LiteLLM as AI abstraction** — easy model/provider switching via single `AI_MODEL` env var
- **Cookie-based auth** — avoids localStorage token; works with SameSite cookies for CSRF protection
