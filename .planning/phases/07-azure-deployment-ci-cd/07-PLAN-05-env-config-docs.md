---
plan: "07-05"
wave: 3
phase: 7
title: "Environment Config & README Azure Deployment Guide"
depends_on:
  - "07-03"
  - "07-04"
files_modified:
  - backend/.env.azure.example
  - README.md
autonomous: true
requirements_addressed:
  - REQ-05c
  - REQ-05d
---

# Plan 07-05: Environment Config & README Azure Deployment Guide

## Objective

Create `backend/.env.azure.example` (full env var template for Azure App Settings) and
add a comprehensive Azure setup + deployment guide section to `README.md`.

## Context (from CONTEXT.md decisions)

- **D-19**: No build-time env vars needed for frontend — all API calls use relative paths
- **D-20**: `backend/.env.azure.example` with placeholder `ALLOWED_ORIGINS` and inline comment
- **D-21**: `COOKIE_SECURE=True` confirmed for Azure HTTPS
- **D-22**: `DATABASE_URL` format: `postgresql+asyncpg://user:pass@host:5432/dbname?ssl=require`
- **D-25**: README section covering Azure setup, first deploy, GitLab CI variable setup, runner notes

## Tasks

### Task 1: Create backend/.env.azure.example

<read_first>
- `backend/.env.example` — existing local env template (field names to replicate + extend)
- `backend/app/config.py` — all Settings fields: DATABASE_URL, SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, ENVIRONMENT, ALLOWED_ORIGINS, COOKIE_SECURE, AI_MODEL, OPENAI_API_KEY, ANTHROPIC_API_KEY
</read_first>

<action>
Create `backend/.env.azure.example` with:

```bash
# ──────────────────────────────────────────────────────────────
# TeamFlow — Azure App Service Environment Variables Template
# Copy these values into Azure Portal:
#   App Service → Configuration → Application settings
# or use: az webapp config appsettings set --settings KEY=VALUE
# ──────────────────────────────────────────────────────────────

# Database — Azure Database for PostgreSQL Flexible Server
# Format: postgresql+asyncpg://USER:PASS@SERVER.postgres.database.azure.com:5432/DB?ssl=require
DATABASE_URL=postgresql+asyncpg://teamflowadmin:YOUR_DB_PASSWORD@YOUR_SERVER.postgres.database.azure.com:5432/teamflow?ssl=require

# Security — generate with: python -c "import secrets; print(secrets.token_hex(32))"
SECRET_KEY=REPLACE_WITH_64_CHAR_HEX_SECRET
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080

# Environment — must be "production" to enable SECRET_KEY validation and secure cookies
ENVIRONMENT=production

# CORS — set to your App Service URL (no trailing slash)
# Replace YOUR_APP with your actual App Service name
ALLOWED_ORIGINS=https://YOUR_APP.azurewebsites.net

# Cookies — True required for Azure HTTPS (do not change)
COOKIE_SECURE=True

# Azure App Service port — nginx listens on 80
WEBSITES_PORT=80

# AI Provider — uncomment and set the key for your chosen provider
AI_MODEL=gpt-4o
OPENAI_API_KEY=sk-REPLACE_WITH_OPENAI_KEY
# ANTHROPIC_API_KEY=REPLACE_WITH_ANTHROPIC_KEY
```
</action>

<acceptance_criteria>
- `backend/.env.azure.example` exists
- File contains `DATABASE_URL=postgresql+asyncpg://` with `?ssl=require`
- File contains `SECRET_KEY=REPLACE_WITH_64_CHAR_HEX_SECRET`
- File contains `ENVIRONMENT=production`
- File contains `ALLOWED_ORIGINS=https://YOUR_APP.azurewebsites.net`
- File contains `COOKIE_SECURE=True`
- File contains `WEBSITES_PORT=80`
- File contains `AI_MODEL=gpt-4o`
- File contains `OPENAI_API_KEY=sk-REPLACE_WITH_OPENAI_KEY`
</acceptance_criteria>

---

### Task 2: Add Azure deployment section to README.md

<read_first>
- `README.md` — existing README (read to find correct insertion point — append after existing content or insert before a relevant section)
- `scripts/setup-azure.sh` — variable names and steps
- `scripts/deploy.sh` — usage
- `.gitlab-ci.yml` — variable names
</read_first>

<action>
Append the following Azure deployment section to `README.md`. If README.md does not exist,
create it with this content plus a brief project description header.

Add this section at the end of README.md (or after any existing "Deployment" / "Getting Started"
section if present):

```markdown
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
```
</action>

<acceptance_criteria>
- `README.md` contains `## Azure Deployment` heading
- `README.md` contains `scripts/setup-azure.sh`
- `README.md` contains `scripts/deploy.sh`
- `README.md` contains table of GitLab CI/CD variables: `AZURE_CLIENT_ID`, `AZURE_CLIENT_SECRET`, `AZURE_TENANT_ID`, `AZURE_SUBSCRIPTION_ID`, `ACR_NAME`, `APP_NAME`, `RG`
- `README.md` contains `az ad sp create-for-rbac` service principal creation command
- `README.md` contains `/api/health` verification step
- `README.md` contains `backend/.env.azure.example` reference
</acceptance_criteria>

---

## Verification Criteria

- [ ] `backend/.env.azure.example` exists with all required Azure App Settings fields
- [ ] `backend/.env.azure.example` uses `postgresql+asyncpg://` with `?ssl=require`
- [ ] `backend/.env.azure.example` has `ENVIRONMENT=production`, `COOKIE_SECURE=True`, `WEBSITES_PORT=80`
- [ ] `README.md` has `## Azure Deployment` section with setup steps, CI variables table, and service principal creation
- [ ] `README.md` references `scripts/setup-azure.sh`, `scripts/deploy.sh`, and `.gitlab-ci.yml`

## must_haves

- `backend/.env.azure.example` covers every env var in `config.py` (D-20)
- `DATABASE_URL` format includes `?ssl=require` (D-22)
- README section explains GitLab CI variables, runner setup, and manual deploy (D-25)
- README includes verification step (`/api/health` curl)
