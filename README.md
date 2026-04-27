# TeamFlow — Private Team & Personal Task Manager

A full-stack private project management app with AI integration.

**Stack:** SvelteKit + Bun · FastAPI (Python) · PostgreSQL · LiteLLM

---

## Features

- **Dashboard** — stats overview, upcoming milestones, recent tasks
- **Projects** — organize tasks and milestones under projects
- **Tasks** — create/assign/filter tasks with priority, status, due dates, tags
- **Milestones** — track releases and major deliverables with timeline progress
- **Team** — view team members and their assigned workload
- **My Schedule** — personal calendar with event creation (visual calendar view)
- **AI Assistant** — persistent chat with LiteLLM (supports OpenAI, Anthropic, Ollama, etc.)

---

## Local Development

### Prerequisites
- Python 3.11+
- Bun (`brew install oven-sh/bun/bun`)
- PostgreSQL (local or via Docker)

### 1. Start PostgreSQL (Docker)
```bash
docker compose up postgres -d
```

### 2. Backend
```bash
cd backend
cp .env.example .env        # edit with your DB URL and AI API key
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```
Tables are auto-created on startup via SQLAlchemy.

### 3. Frontend
```bash
cd frontend
bun install
bun run dev                 # runs on http://localhost:5173
```

### 4. Register your first user
Visit `http://localhost:5173/register` and create an account.

---

## AI Configuration

Edit `backend/.env` — set `AI_MODEL` to any LiteLLM-supported model:

| Provider | Example value |
|---|---|
| OpenAI | `gpt-4o` |
| Anthropic | `claude-3-5-sonnet-20241022` |
| Ollama (local) | `ollama/llama3` |
| Gemini | `gemini/gemini-1.5-pro` |

Set the corresponding API key env var (`OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, etc.).

---

## Docker (Full Stack)

```bash
cp backend/.env.example backend/.env  # edit AI keys
docker compose up --build
```

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

## Project Structure

v2.1 structural refactor migration: see [`docs/MIGRATION-V2.1.md`](docs/MIGRATION-V2.1.md).

```
windsurf-project/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI app + lifespan
│   │   ├── models.py        # SQLAlchemy models
│   │   ├── schemas.py       # Pydantic schemas
│   │   ├── auth.py          # JWT auth
│   │   ├── config.py        # Settings
│   │   ├── database.py      # Async DB engine
│   │   └── routers/         # auth, users, projects, tasks, milestones, schedules, ai, dashboard
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── routes/          # +page.svelte for each section
│   │   ├── lib/
│   │   │   ├── api.ts       # API client
│   │   │   ├── utils.ts     # Helpers
│   │   │   └── stores/      # auth store
│   │   └── app.css          # Tailwind base
│   ├── package.json
│   ├── bunfig.toml
│   └── Dockerfile
└── docker-compose.yml
```

---

## Azure Deployment

TeamFlow deploys as a single monolith container (nginx + FastAPI + SvelteKit static files)
on Azure App Service.

### Architecture

```
Azure App Service (B1, Linux)
└── Docker container (port 80)
    ├── nginx          → serves /api/* → uvicorn, /ws/* → uvicorn (WebSocket), /* → static files
    └── uvicorn        → FastAPI backend (port 8000, internal only)
        └── Alembic    → runs migrations on startup via lifespan hook

Azure Container Registry (ACR)   → stores Docker images (tagged by git commit SHA)
Azure Database for PostgreSQL     → Flexible Server (B1ms, SSL required)
```

### Prerequisites

- [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli) installed and logged in (`az login`)
- Azure subscription with Contributor access
- Self-hosted GitLab instance with a runner (Docker executor)

---

### First-Time Setup

#### 1. Provision Azure Resources

```bash
export DB_ADMIN_PASS="your-secure-db-password"
bash scripts/setup-azure.sh
```

This creates: resource group, ACR, App Service plan, App Service (with AcrPull managed identity), and PostgreSQL Flexible Server.

After provisioning, update these App Settings in the Azure Portal (App Service → Configuration → Application settings):

| Setting | Value |
|---------|-------|
| `SECRET_KEY` | Generate: `python -c "import secrets; print(secrets.token_hex(32))"` |
| `OPENAI_API_KEY` | Your OpenAI API key (or `ANTHROPIC_API_KEY` for Anthropic) |

See `backend/.env.azure.example` for the full list of required settings.

#### 2. Deploy the First Image

```bash
bash scripts/deploy.sh
```

This builds the monolith Docker image via ACR (no local Docker daemon needed) and deploys it to App Service.

#### 3. Verify

```bash
APP_NAME="teamflow-app"   # your App Service name
curl https://$APP_NAME.azurewebsites.net/api/health
# → {"status":"ok"}
```

Open `https://YOUR_APP.azurewebsites.net` in a browser — the TeamFlow SPA should load.

---

### CI/CD with GitLab

The pipeline (`.gitlab-ci.yml`) runs automatically on push to `main`.

#### Required GitLab CI/CD Variables

Go to your GitLab project → Settings → CI/CD → Variables. Add these as **masked** variables:

| Variable | Description |
|----------|-------------|
| `AZURE_CLIENT_ID` | Service principal app ID |
| `AZURE_CLIENT_SECRET` | Service principal password (masked) |
| `AZURE_TENANT_ID` | Azure AD tenant ID |
| `AZURE_SUBSCRIPTION_ID` | Azure subscription ID |
| `ACR_NAME` | ACR name (e.g. `teamflowacr`) |
| `APP_NAME` | App Service name (e.g. `teamflow-app`) |
| `RG` | Resource group name (e.g. `teamflow-rg`) |

#### Create a Service Principal

```bash
az ad sp create-for-rbac \
  --name "teamflow-gitlab-ci" \
  --role Contributor \
  --scopes /subscriptions/YOUR_SUBSCRIPTION_ID/resourceGroups/teamflow-rg
```

Save the output — `appId` = `AZURE_CLIENT_ID`, `password` = `AZURE_CLIENT_SECRET`, `tenant` = `AZURE_TENANT_ID`.

#### GitLab Runner Requirements

The runner uses `mcr.microsoft.com/azure-cli` Docker image. The runner needs:
- Docker executor (no privileged mode needed — `az acr build` runs in the cloud)
- Outbound internet access to Azure endpoints

Register a runner:
```bash
gitlab-runner register \
  --url https://YOUR_GITLAB_URL \
  --token YOUR_RUNNER_TOKEN \
  --executor docker \
  --docker-image mcr.microsoft.com/azure-cli
```

#### Pipeline Stages

| Stage | What it does |
|-------|-------------|
| `build` | Logs in to Azure, runs `az acr build` to build and push `teamflow:{commit-sha}` to ACR |
| `deploy` | Updates App Service container image, restarts the app |

---

### Manual Deploy (without CI)

```bash
bash scripts/deploy.sh
```

---

### Environment Variables Reference

See `backend/.env.azure.example` for the full template. Key variables:

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | ✅ | PostgreSQL connection string with `?ssl=require` |
| `SECRET_KEY` | ✅ | 64-char hex secret (JWT signing) |
| `ENVIRONMENT` | ✅ | Must be `production` |
| `ALLOWED_ORIGINS` | ✅ | App Service URL for CORS |
| `OPENAI_API_KEY` | ✅ | AI provider key |
| `WEBSITES_PORT` | ✅ | `80` (nginx listener port) |
