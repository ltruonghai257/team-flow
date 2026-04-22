# Integrations

*Mapped: 2026-04-22*

## Database

- **PostgreSQL 16** (via Docker image `postgres:16-alpine`)
  - Connection: `postgresql+asyncpg://postgres:password@localhost:5432/taskmanager`
  - ORM: SQLAlchemy 2.x async engine (`backend/app/database.py`)
  - Migrations: Alembic (configured, `backend/app/` — migration files not yet generated)
  - Schema auto-created on startup via `Base.metadata.create_all`

## AI / LLM

- **LiteLLM** (`backend/app/routers/ai.py`) — provider-agnostic LLM gateway
  - Configured via `AI_MODEL` setting (default `gpt-4o`)
  - Supports: OpenAI (`OPENAI_API_KEY`), Anthropic (`ANTHROPIC_API_KEY`), Ollama (local), and any LiteLLM-supported provider
  - Used for: persistent AI conversation history, single-turn quick-chat, AI task parsing (NLP/JSON modes)

## Authentication

- **JWT / Cookie-based** (no third-party auth provider)
  - `python-jose` for JWT sign/verify (`backend/app/auth.py`)
  - `bcrypt` for password hashing
  - Token delivered as `HttpOnly` cookie `access_token`; also accepts Bearer header
  - 7-day expiry (`ACCESS_TOKEN_EXPIRE_MINUTES=10080`)

## WebSocket

- **FastAPI native WebSocket** (`backend/app/routers/websocket.py`, `backend/app/websocket/manager.py`)
  - Single `/ws/chat` endpoint multiplexed for: assistant chat, team channel messages, direct messages, presence updates
  - Client: `frontend/src/lib/websocket.ts` — `ChatWebSocket` class with heartbeat (30s), exponential backoff reconnect (max 5 attempts)
  - Auth via `access_token` cookie during WS handshake

## Background Jobs

- **APScheduler** (`AsyncIOScheduler`) — `backend/app/scheduler_jobs.py`
  - Job: `process_due_notifications` — polls every 60s, flips `EventNotification` rows from `pending` → `sent`
  - Lifecycle managed in FastAPI lifespan context manager

## Frontend → Backend Proxy

- Vite dev server proxies `/api/*` and `/ws/*` to backend (`frontend/vite.config.ts`)
- Production: SvelteKit node adapter; proxy/reverse-proxy must be configured externally (nginx/caddy)

## No External Integrations (currently)

- No email sending (notifications are in-app only)
- No OAuth providers
- No file storage (S3, etc.)
- No analytics or monitoring services
- No push notification services
