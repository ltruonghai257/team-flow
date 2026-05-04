# Phase 7: Azure Deployment & CI/CD — Research

*Gathered: 2026-04-23*
*Phase: 07-azure-deployment-ci-cd*

## RESEARCH COMPLETE

---

## 1. SvelteKit 5 + adapter-static: Key Findings

### Current State
- `frontend/svelte.config.js` uses `@sveltejs/adapter-node` — **must be swapped to `@sveltejs/adapter-static`**
- `@sveltejs/adapter-static` is **not currently installed** — `frontend/package.json` only has `@sveltejs/adapter-node@^5.0.1`
- No `+page.ts` or `+layout.ts` files exist in `frontend/src/routes/` — all routes are pure `.svelte` files with no `load()` functions that would require SSR

### adapter-static Requirements for SvelteKit 5 SPA
- All routes must be client-side rendered — requires `export const prerender = true` OR global SPA fallback
- **SPA mode** (recommended for this app): set `fallback: '200.html'` in adapter config — nginx serves `200.html` for all paths, browser router handles client-side navigation
- `svelte.config.js` change:
  ```js
  import adapter from '@sveltejs/adapter-static';
  // ...
  adapter({ fallback: '200.html' })
  ```
- A root `+layout.ts` with `export const prerender = true; export const ssr = false;` is needed to disable SSR globally — this is the canonical SPA pattern for SvelteKit 5
- SvelteKit build output: `frontend/build/` — static HTML/CSS/JS served by nginx

### WebSocket URL Resolution (Critical)
- `websocket.ts` derives URL from `window.location.host` — uses same origin as page
- With monolith nginx: WS connects to `wss://teamflow.azurewebsites.net/ws/chat` → nginx proxies to uvicorn at `127.0.0.1:8000/ws/chat` ✓
- **No env var needed** — relative origin-based WS URL works correctly with monolith

### API Calls (Confirmed)
- `api.ts` uses `const BASE = '/api'` — all calls are relative (`/api/auth/token`, etc.)
- nginx proxies `/api/*` → `127.0.0.1:8000` — works out of the box ✓

---

## 2. Monolith Dockerfile Architecture

### Multi-Stage Build Plan
```
Stage 1: bun builder   → builds SvelteKit static output → frontend/build/
Stage 2: python deps   → installs pip requirements
Stage 3: final image   → debian:12-slim + nginx + python3 + supervisord
                         copies static build + backend code
```

### Base Image Selection
- **`debian:12-slim`** (Bookworm): smallest Debian with apt access to `nginx`, `supervisor`, `python3`
- Avoids Ubuntu bloat; `python3.12` available via `deadsnakes` PPA or via copying from the Python stage
- **Alternative**: copy Python binary from `python:3.12-slim` stage — avoids PPA complexity
- Recommended: copy `/usr/local` from `python:3.12-slim` stage into `debian:12-slim` or use `python:3.12-slim` as final stage and `apt-get install nginx supervisor`

### supervisord Config
```ini
[supervisord]
nodaemon=true
logfile=/dev/null
logfile_maxbytes=0

[program:nginx]
command=/usr/sbin/nginx -g "daemon off;"
autostart=true
autorestart=true
stdout_logfile=/dev/stdout
stdout_logfile_maxbytes=0
stderr_logfile=/dev/stderr
stderr_logfile_maxbytes=0

[program:uvicorn]
command=/usr/local/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 1
directory=/app/backend
autostart=true
autorestart=true
stdout_logfile=/dev/stdout
stdout_logfile_maxbytes=0
stderr_logfile=/dev/stderr
stderr_logfile_maxbytes=0
```

### Alembic Migration (Already Handled in main.py)
- **Critical finding**: `backend/app/main.py` already runs Alembic in the `lifespan` context:
  ```python
  await asyncio.to_thread(run_migrations)  # runs alembic upgrade head on startup
  ```
- This means **no separate migration step in supervisord or startup script is needed** — migrations run automatically when uvicorn starts
- The lifespan approach calls `sys.exit(1)` on migration failure — container will restart cleanly on Azure App Service

### nginx Config
```nginx
server {
    listen 80;
    root /app/frontend/build;
    index index.html 200.html;

    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /ws/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_read_timeout 3600s;
    }

    location / {
        try_files $uri $uri/ /200.html;
    }
}
```

### Azure App Service Port
- Azure App Service expects app to listen on port **80** (or env var `PORT` / `WEBSITES_PORT`)
- nginx listens on port 80 — correct ✓
- Set `WEBSITES_PORT=80` in Azure App Settings (optional but explicit)

---

## 3. GitLab CI/CD Pipeline

### Pipeline Structure
```yaml
# .gitlab-ci.yml
stages:
  - build
  - deploy

variables:
  IMAGE_TAG: $CI_COMMIT_SHORT_SHA

build:
  stage: build
  image: docker:24
  services:
    - docker:24-dind
  script:
    - az login --service-principal -u $AZURE_CLIENT_ID -p $AZURE_CLIENT_SECRET --tenant $AZURE_TENANT_ID
    - az acr build --registry $ACR_NAME --image teamflow:$IMAGE_TAG .
  only:
    - main

deploy:
  stage: deploy
  image: mcr.microsoft.com/azure-cli
  script:
    - az login --service-principal -u $AZURE_CLIENT_ID -p $AZURE_CLIENT_SECRET --tenant $AZURE_TENANT_ID
    - az webapp config container set --name $APP_NAME --resource-group $RG
        --container-image-name $ACR_NAME.azurecr.io/teamflow:$IMAGE_TAG
    - az webapp restart --name $APP_NAME --resource-group $RG
  only:
    - main
  when: on_success
```

**Note:** Using `az acr build` in the `build` job means Docker-in-Docker (`dind`) is not strictly needed — `az acr build` sends the build context to ACR and builds in the cloud. This simplifies self-hosted runner requirements (no privileged container needed for the runner).

### Simpler approach (recommended for self-hosted runner):
```yaml
build_and_deploy:
  stage: build
  image: mcr.microsoft.com/azure-cli
  script:
    - az login --service-principal -u $AZURE_CLIENT_ID -p $AZURE_CLIENT_SECRET --tenant $AZURE_TENANT_ID
    - az acr build --registry $ACR_NAME --image teamflow:$CI_COMMIT_SHORT_SHA .
    - az webapp config container set --name $APP_NAME --resource-group $RG
        --container-image-name $ACR_NAME.azurecr.io/teamflow:$CI_COMMIT_SHORT_SHA
  only:
    - main
```

### GitLab CI Variables Required
Masked variables in GitLab project Settings → CI/CD → Variables:
- `AZURE_CLIENT_ID`
- `AZURE_CLIENT_SECRET` (masked)
- `AZURE_TENANT_ID`
- `AZURE_SUBSCRIPTION_ID`
- `ACR_NAME` (e.g. `teamflowacr`)
- `APP_NAME` (e.g. `teamflow-app`)
- `RG` (resource group name)

---

## 4. Azure Provisioning (setup-azure.sh)

### Resource Creation Order
1. Resource group
2. ACR (Basic tier — cheapest, supports `az acr build`)
3. App Service plan (Linux, B1 SKU)
4. App Service (Linux container, assign `AcrPull` identity)
5. PostgreSQL Flexible Server (B1ms SKU — cheapest)
6. Configure App Service env vars (App Settings)

### ACR Managed Identity for App Service
```bash
# Assign managed identity + AcrPull role so App Service can pull images without credentials
az webapp identity assign --name $APP_NAME --resource-group $RG
PRINCIPAL_ID=$(az webapp identity show --name $APP_NAME --resource-group $RG --query principalId -o tsv)
ACR_ID=$(az acr show --name $ACR_NAME --resource-group $RG --query id -o tsv)
az role assignment create --assignee $PRINCIPAL_ID --role AcrPull --scope $ACR_ID
```

### PostgreSQL Connection String Format
`postgresql+asyncpg://adminuser:password@servername.postgres.database.azure.com:5432/teamflow?ssl=require`

---

## 5. Environment Variables (backend/.env.azure.example)

Required Azure App Settings:
```bash
DATABASE_URL=postgresql+asyncpg://USER:PASS@SERVER.postgres.database.azure.com:5432/teamflow?ssl=require
SECRET_KEY=<generate with: python -c "import secrets; print(secrets.token_hex(32))">
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080
ENVIRONMENT=production
ALLOWED_ORIGINS=https://YOUR_APP.azurewebsites.net
COOKIE_SECURE=True
AI_MODEL=gpt-4o
OPENAI_API_KEY=sk-...
# ANTHROPIC_API_KEY=...  # optional
WEBSITES_PORT=80
```

---

## 6. Validation Architecture

### Pre-Deploy Verification
- `docker build -t teamflow:local .` — verify monolith image builds without errors
- `docker run -p 80:80 --env-file backend/.env teamflow:local` — smoke test locally
- Confirm `/api/health` returns `{"status": "ok"}`
- Confirm SvelteKit static files are served at `/`

### Post-Deploy Verification
- `az webapp show --name $APP_NAME --resource-group $RG --query state` → `Running`
- `curl https://$APP_NAME.azurewebsites.net/api/health` → `{"status": "ok"}`
- Browser: load `https://$APP_NAME.azurewebsites.net` → SvelteKit SPA loads
- GitLab pipeline: green badge on `main` branch after commit

### CI Verification
- `.gitlab-ci.yml` `only: [main]` trigger fires on push to main
- `az acr build` exits 0 → image pushed to ACR
- `az webapp config container set` exits 0 → deployment queued
- App Service shows new container image in deployment logs

---

## Key Decisions Confirmed by Research

1. **Alembic migration is already handled** in `main.py` lifespan — no supervisord migration step needed
2. **SPA mode** (`fallback: '200.html'`) required for adapter-static — needs `+layout.ts` with `ssr = false`
3. **`@sveltejs/adapter-static` must be installed** — not in current `package.json`
4. **Single-job GitLab pipeline** (build + deploy in one job) is simpler for self-hosted runner — avoids Docker-in-Docker
5. **`az acr build`** handles Docker build in the cloud — self-hosted runner only needs Azure CLI, not Docker daemon
6. **nginx listens on port 80** — correct for Azure App Service default port mapping
7. **Managed identity** (AcrPull) preferred over stored registry credentials for App Service image pull
