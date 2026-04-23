# Phase 7: Azure Deployment & CI/CD - Context

**Gathered:** 2026-04-23
**Status:** Ready for planning

<domain>
## Phase Boundary

Deploy TeamFlow to Azure App Service as a **single monolith container** containing the FastAPI backend (uvicorn) + SvelteKit frontend (static build) served via nginx as the reverse proxy. Automated via GitLab CI/CD pipeline (self-hosted runner). One-time provisioning via `scripts/setup-azure.sh`; manual fallback via `scripts/deploy.sh`; full README section covering setup and deployment.

</domain>

<decisions>
## Implementation Decisions

### Container Architecture
- **D-01:** Single monolith Docker image — nginx + uvicorn + static frontend in one container. No separate App Service for frontend.
- **D-02:** Multi-stage `Dockerfile` at repo root: Stage 1 (Bun) builds SvelteKit → Stage 2 (Python) installs backend deps → Final stage copies both into a base image with nginx and supervisord.
- **D-03:** SvelteKit adapter changed from `adapter-node` to **`adapter-static`** so the build output is pure HTML/CSS/JS that nginx serves directly. No Node/Bun process at runtime.
- **D-04:** **supervisord** manages both nginx and uvicorn inside the container — handles crash restarts for both processes.
- **D-05:** nginx routing: `/api/*` proxied to `127.0.0.1:8000` (uvicorn), `/ws/*` proxied to `127.0.0.1:8000` with WebSocket upgrade headers, all other paths served from SvelteKit static build via `try_files`.

### Azure Resources
- **D-06:** Single Azure App Service (Linux, B1 SKU) hosting the monolith container — one URL for the entire app.
- **D-07:** Azure Container Registry (ACR) stores the built Docker image.
- **D-08:** Azure Database for PostgreSQL Flexible Server — connection via `DATABASE_URL` env var (asyncpg format, `?ssl=require`).
- **D-09:** All scripts use **variables at the top** (e.g. `RG`, `ACR_NAME`, `APP_NAME`, `LOCATION`) — configurable before first run. No hard-coded names throughout.
- **D-10:** Default Azure region: **`westus2`** (as variable default in scripts).

### Docker Image Tagging
- **D-11:** Images tagged with **git commit SHA only** (e.g. `teamflow:$CI_COMMIT_SHORT_SHA`). No `:latest` tag in CI to preserve rollback traceability.

### GitLab CI/CD Pipeline
- **D-12:** Pipeline file: `.gitlab-ci.yml` at repo root.
- **D-13:** Repository: **self-hosted GitLab** instance.
- **D-14:** Azure authentication: **service principal credentials** stored as masked GitLab CI/CD variables (`AZURE_CLIENT_ID`, `AZURE_CLIENT_SECRET`, `AZURE_TENANT_ID`, `AZURE_SUBSCRIPTION_ID`, `ACR_NAME`, `APP_NAME`, `RG`). Uses `az login --service-principal` in pipeline.
- **D-15:** Pipeline triggers: **push to `main` branch** + **manual `workflow: manual` job option** (GitLab equivalent of `workflow_dispatch` — a manual trigger stage or `when: manual` deploy job).
- **D-16:** Build strategy: **parallel** — separate `build` stage runs backend image build, then a single `deploy` stage deploys. (Since it's one monolith image, parallel is: build image → deploy to App Service as sequential stages, but build is fast as one step.)
- **D-17:** No health check / deploy gate for v1. Azure App Service deployment success is sufficient.
- **D-18:** Alembic `alembic upgrade head` runs as the **container startup command** (not in CI), via supervisord or entrypoint before uvicorn starts.

### Environment Configuration
- **D-19:** **No build-time env vars needed for frontend** — all API calls use relative paths (`/api/*`), served from the same nginx origin.
- **D-20:** `backend/.env.azure.example` — full env var template for Azure App Settings. `ALLOWED_ORIGINS` set to placeholder `https://YOUR_APP.azurewebsites.net` with inline README comment to replace with the actual App Service URL.
- **D-21:** `COOKIE_SECURE=True` (already the default in `config.py`) — confirmed for Azure HTTPS deployment.
- **D-22:** `DATABASE_URL` format: `postgresql+asyncpg://user:pass@host:5432/dbname?ssl=require` (Azure PostgreSQL Flexible Server requires SSL).

### Scripts & Documentation
- **D-23:** `scripts/setup-azure.sh` — one-time provisioning: resource group, ACR, App Service plan, App Service, PostgreSQL Flexible Server. Variables at top.
- **D-24:** `scripts/deploy.sh` — manual deploy: builds image via `az acr build`, updates App Service container config. Variables at top.
- **D-25:** README section: step-by-step Azure setup, first deploy, GitLab CI variable setup, and GitLab runner registration notes (self-hosted).

### Claude's Discretion
- Dockerfile base image selection for the final stage (debian-slim vs. ubuntu-slim — pick smallest that supports nginx + python + supervisord)
- supervisord config file structure (number of workers, log paths)
- nginx worker process count and keep-alive settings
- GitLab CI image to use in jobs (e.g. `mcr.microsoft.com/azure-cli` or install az CLI inline)
- `setup-azure.sh` whether to create DB as part of the same script or note it as a separate step

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Requirements
- `.planning/REQUIREMENTS.md` § REQ-05 — Full Azure deployment acceptance criteria (infrastructure, CI/CD, manual scripts, env config)

### Research
- `.planning/research/RESEARCH.md` §1 — Azure App Service + ACR deployment pattern (az acr build, managed identity, connection string config)
- `.planning/research/RESEARCH.md` §3 — GitHub Actions CI/CD pattern (adapt for GitLab CI — same Azure CLI commands, different pipeline YAML syntax)

### Existing Docker Setup
- `docker-compose.yml` — existing dev orchestration; reference for service names and port mapping
- `backend/Dockerfile` — existing backend image (multi-stage not yet; this phase upgrades to monolith Dockerfile)
- `frontend/Dockerfile` — existing frontend image (uses `oven/bun:1`; this phase replaces with adapter-static build stage)

### Backend Config
- `backend/app/config.py` — env var schema; `ALLOWED_ORIGINS`, `COOKIE_SECURE`, `DATABASE_URL` already env-driven
- `backend/.env.example` — existing local env template; reference for field names in `backend/.env.azure.example`

### Frontend Config
- `frontend/svelte.config.js` — adapter-node currently; must be changed to adapter-static
- `frontend/package.json` — Bun scripts; `bun run build` is the build command

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `backend/Dockerfile`: Python 3.12-slim base, pip install, `uvicorn app.main:app --host 0.0.0.0 --port 8000` CMD — reuse as a stage in the monolith Dockerfile
- `frontend/Dockerfile`: `oven/bun:1` builder stage, `bun install --frozen-lockfile`, `bun run build` — reuse as a stage; discard the `CMD` (no runtime Node process needed with adapter-static)
- `docker-compose.yml`: shows service port mapping (backend:8000, frontend:3000, postgres:5432) — informs nginx proxy_pass ports

### Established Patterns
- Frontend uses **Bun** (not npm/yarn) — `bun install --frozen-lockfile` and `bun run build` are the correct commands
- `ENVIRONMENT=production` already triggers `SECRET_KEY` validation and should be set in Azure App Settings
- `COOKIE_SECURE=True` is the existing default — correct for Azure HTTPS
- `DATABASE_URL` uses `postgresql+asyncpg://` format — Azure PostgreSQL needs `?ssl=require` appended

### Integration Points
- nginx must handle WebSocket upgrade for `/ws/*` — FastAPI WebSocket connections already work on App Service (per RESEARCH.md §1)
- `alembic upgrade head` must run before `uvicorn` starts — supervisord config should sequence this (entrypoint script or `command=` in supervisord backend section)
- `ALLOWED_ORIGINS` in `config.py` is already parsed from comma-separated env var — Azure App Setting can contain multiple origins

</code_context>

<specifics>
## Specific Ideas

- User specifically requested **monolith architecture with nginx** — this overrides the two-App-Service pattern from RESEARCH.md and ROADMAP.md
- User uses **self-hosted GitLab**, not GitHub — `deploy.yml` (GitHub Actions) from ROADMAP.md becomes `.gitlab-ci.yml`
- Default region is **`westus2`** (user-specified)
- **adapter-static** is required for nginx to serve the frontend as static files — researcher should confirm SvelteKit 5 compatibility with `@sveltejs/adapter-static` and any `prerender` config needed for a client-side SPA

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 07-azure-deployment-ci-cd*
*Context gathered: 2026-04-23*
