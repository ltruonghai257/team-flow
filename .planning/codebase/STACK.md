# Stack

*Mapped: 2026-04-22*

## Languages

- **Python 3.13** — backend (`backend/`)
- **TypeScript 5.4** — frontend (`frontend/src/`)
- **Svelte 5 / HTML/CSS** — UI templates

## Runtime & Servers

- **Uvicorn** (ASGI, `uvicorn[standard]>=0.30.0`) — serves FastAPI backend on port 8000
- **Vite 6 / Node** — SvelteKit dev server on port 5173; production build via `@sveltejs/adapter-node`

## Frameworks

| Layer | Framework | Version |
|-------|-----------|---------|
| Backend API | FastAPI | >=0.115.0 |
| Frontend | SvelteKit | ^2.5.7 |
| UI components | Svelte 5 | ^5.0.0 |
| CSS | TailwindCSS | ^3.4.4 |

## Key Libraries

### Backend
- `sqlalchemy>=2.0.36` + `asyncpg>=0.30.0` — async ORM + PostgreSQL driver
- `alembic>=1.14.0` — database migrations
- `pydantic>=2.10.0` + `pydantic-settings>=2.6.0` — schema validation + config
- `python-jose[cryptography]>=3.3.0` — JWT encoding/decoding
- `bcrypt>=4.0.0` — password hashing
- `litellm>=1.55.0` — unified LLM API gateway (OpenAI, Anthropic, Ollama, etc.)
- `apscheduler>=3.10.4` — background job scheduler (AsyncIOScheduler)
- `httpx>=0.28.0` — async HTTP client

### Frontend
- `lucide-svelte ^0.378.0` — icon library
- `svelte-dnd-action ^0.9.69` — drag-and-drop for Kanban
- `svelte-sonner ^0.3.27` — toast notifications
- `date-fns ^3.6.0` — date utilities

## Configuration

### Backend (`backend/app/config.py`)
Uses `pydantic-settings` `BaseSettings` reading from `.env`:
```
DATABASE_URL=postgresql+asyncpg://...
SECRET_KEY=...
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080  # 7 days
COOKIE_SECURE=True
AI_MODEL=gpt-4o
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=...
```

### Frontend (`frontend/vite.config.ts`)
- `PUBLIC_API_BASE` env var controls backend proxy target (default `http://localhost:8000`)
- `/api/*` and `/ws/*` proxied to backend

## Package Management
- **Backend**: pip / `requirements.txt` (no lock file)
- **Frontend**: yarn 1.22.22 (`yarn.lock`) + bun (`bun.lock` also present)

## Containerization
- `docker-compose.yml` — three services: `postgres:16-alpine`, `teamflow_backend`, `teamflow_frontend`
- Individual `Dockerfile`s in `backend/` and `frontend/`
- Backend port 8000, frontend port 3000 in container; postgres port 5432
