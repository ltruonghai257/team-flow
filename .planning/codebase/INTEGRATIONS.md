# External Integrations

**Analysis Date:** 2026-04-28

## APIs & External Services

**AI Models:**
- LiteLLM - Used for AI features routing and processing (`backend/app/utils/ai_client.py`)
  - SDK/Client: `litellm`
  - Auth: `OPENAI_API_KEY`, `ANTHROPIC_API_KEY` (supports GPT-4o, Claude, etc.)

**Email Sending:**
- SMTP (FastAPI-Mail) - Sending user invites and KPI warnings (`backend/app/utils/email_service.py`)
  - SDK/Client: `fastapi-mail`
  - Auth: `MAIL_USERNAME`, `MAIL_PASSWORD`
  - Default Server: `smtp.gmail.com`

## Data Storage

**Databases:**
- PostgreSQL 16
  - Connection: `DATABASE_URL` (e.g. `postgresql+asyncpg://...`)
  - Client: `asyncpg` with `SQLAlchemy` ORM (`backend/app/core/config.py`)

**File Storage:**
- Local filesystem only

**Caching:**
- None detected (Local memory / direct database queries)

## Authentication & Identity

**Auth Provider:**
- Custom
  - Implementation: JWT (JSON Web Tokens) generated using `python-jose` with `HS256` and passwords hashed via `bcrypt` (`backend/requirements.txt`, `backend/app/core/config.py`).

## Monitoring & Observability

**Error Tracking:**
- None detected

**Logs:**
- Standard Python logging module (`logging`) to stdout/stderr. Used actively in services like `backend/app/utils/email_service.py`.

## CI/CD & Deployment

**Hosting:**
- Azure App Service (`scripts/deploy.sh`)

**CI Pipeline:**
- GitLab CI (`.gitlab-ci.yml` is present)
- Azure Container Registry (ACR) used for monolith container building.

## Environment Configuration

**Required env vars:**
- `DATABASE_URL` - Database connection string
- `SECRET_KEY` - Used for JWT signing (must be changed in production)
- `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` - For AI integration
- `MAIL_USERNAME`, `MAIL_PASSWORD`, `MAIL_SERVER` - For SMTP email sending
- `ENVIRONMENT` - 'development' or 'production'

**Secrets location:**
- Local: `.env` file (loaded by Pydantic `BaseSettings` in `backend/app/core/config.py`)
- Production: Azure App Service configuration settings

## Webhooks & Callbacks

**Incoming:**
- None detected

**Outgoing:**
- None detected

---

*Integration audit: 2026-04-28*
