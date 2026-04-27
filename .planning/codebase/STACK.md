# Technology Stack

**Analysis Date:** 2026-04-28

## Languages

**Primary:**
- TypeScript 5.4 - Frontend logic and components (`frontend/package.json`)
- Python 3.12 - Backend API and business logic (`Dockerfile`, `backend/requirements.txt`)

**Secondary:**
- Svelte/HTML/CSS - Frontend views (`frontend/src/`)
- Shell/Bash - Deployment and setup scripts (`scripts/deploy.sh`)

## Runtime

**Environment:**
- Node.js / Bun 1 - Frontend build environment (`Dockerfile`, `frontend/package.json`)
- Python 3.12-slim - Backend runtime (`Dockerfile`)
- Docker - Local development and production deployment (`docker-compose.yml`, `Dockerfile`)
- Nginx / Supervisor - Production process management and reverse proxy (`Dockerfile`)

**Package Manager:**
- Yarn / Bun - Frontend package managers (lockfiles present for both)
- pip - Backend package manager (`backend/requirements.txt`)
- Lockfile: present (`yarn.lock`, `bun.lock`)

## Frameworks

**Core:**
- SvelteKit 2.5 - Frontend framework for SPA building (`frontend/package.json`)
- FastAPI 0.115 - Backend REST API framework (`backend/requirements.txt`)

**Testing:**
- Playwright 1.59 - E2E testing for the frontend (`frontend/package.json`)
- Pytest - Backend testing (`backend/tests/`)

**Build/Dev:**
- Vite 6.0 - Frontend build tool (`frontend/vite.config.ts`)
- TailwindCSS 3.4 - Styling framework (`frontend/tailwind.config.js`)
- Uvicorn 0.30.0 - Backend ASGI server (`backend/requirements.txt`)
- Docker Compose - Local orchestrator (`docker-compose.yml`)

## Key Dependencies

**Critical:**
- SQLAlchemy 2.0.36 - Backend ORM for database interactions
- asyncpg 0.30.0 - Asynchronous PostgreSQL database driver
- Alembic 1.14.0 - Database migration tool
- svelte-dnd-action 0.9.69 - Drag and drop functionality for Kanban/boards
- layerchart & d3-shape - Data visualization on the frontend

**Infrastructure:**
- litellm 1.55.0 - Universal API client for AI model integrations
- apscheduler 3.10.4 - Backend background job scheduling
- fastapi-mail 1.4.1 - Sending emails asynchronously from FastAPI
- slowapi 0.1.9 - Rate limiting for FastAPI

## Configuration

**Environment:**
- Configured via `.env` file loaded through Pydantic's `BaseSettings` (`backend/app/core/config.py`).
- Requires variables like `DATABASE_URL`, `SECRET_KEY`, `OPENAI_API_KEY`/`ANTHROPIC_API_KEY`, and `MAIL_*` credentials.

**Build:**
- Frontend: `frontend/vite.config.ts`, `frontend/svelte.config.js`, `frontend/tailwind.config.js`
- Backend: `Dockerfile` (Monolith setup using multistage builds)
- Infrastructure: `docker-compose.yml`

## Platform Requirements

**Development:**
- Docker Desktop or equivalent (Docker Compose for `postgres`, `backend`, `frontend`)
- Node.js/Bun and Python 3.12 (if running natively)

**Production:**
- Azure App Service (deployed via Azure Container Registry). Built as a monolith container running Nginx, Supervisor, FastAPI, and Svelte static files (`scripts/deploy.sh`).

---

*Stack analysis: 2026-04-28*
