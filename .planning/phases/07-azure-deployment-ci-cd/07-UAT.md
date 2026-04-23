---
status: testing
phase: 07-azure-deployment-ci-cd
source: 07-PLAN-01-svelte-adapter-static-SUMMARY.md, 07-PLAN-02-monolith-dockerfile-SUMMARY.md, 07-PLAN-03-azure-scripts-SUMMARY.md, 07-PLAN-04-gitlab-cicd-SUMMARY.md, 07-PLAN-05-env-config-docs-SUMMARY.md
started: 2026-04-23T22:30:00+07:00
updated: 2026-04-23T22:30:00+07:00
---

## Current Test

number: 1
name: Cold Start Smoke Test — Static Build
expected: |
  Run `bun run build` in the `frontend/` directory from scratch.
  It should exit with code 0 and produce `frontend/build/200.html` and `frontend/build/_app/`.
awaiting: user response

## Tests

### 1. Cold Start Smoke Test — Static Build
expected: Run `bun run build` in `frontend/` — exits 0, produces `frontend/build/200.html` and `frontend/build/_app/` directory with JS files
result: [pending]

### 2. SvelteKit adapter-static config
expected: Open `frontend/svelte.config.js` — it imports from `@sveltejs/adapter-static` (not adapter-node), has `fallback: '200.html'`, and `prerender.handleHttpError: 'warn'`
result: [pending]

### 3. SSR disabled globally
expected: Open `frontend/src/routes/+layout.ts` — file exists and contains `export const prerender = true` and `export const ssr = false`
result: [pending]

### 4. Monolith Dockerfile structure
expected: Open `Dockerfile` at the repo root — it has 3 FROM stages (oven/bun:1 as frontend-builder, python:3.12-slim as backend-deps, python:3.12-slim as final), installs nginx+supervisor, copies both frontend build and backend, exposes port 80
result: [pending]

### 5. nginx.conf routing
expected: Open `nginx.conf` at repo root — `/api/` location proxies to `http://127.0.0.1:8000`, `/ws/` location has `proxy_http_version 1.1` and `Connection "upgrade"`, `/` location uses `try_files $uri $uri/ /200.html`
result: [pending]

### 6. supervisord.conf process management
expected: Open `supervisord.conf` at repo root — has `[program:nginx]` and `[program:uvicorn]`, `nodaemon=true`, uvicorn command targets `app.main:app --host 127.0.0.1 --port 8000`, `directory=/app/backend`
result: [pending]

### 7. .dockerignore excludes secrets and build artifacts
expected: Open `.dockerignore` at repo root — contains `.git`, `.planning`, `**/node_modules`, `backend/.env`, `frontend/build`
result: [pending]

### 8. Azure setup script content
expected: Open `scripts/setup-azure.sh` — configurable variables at top (RG, LOCATION, ACR_NAME, APP_NAME, DB_SERVER_NAME), guard for empty DB_ADMIN_PASS, creates ACR with `az acr create`, assigns AcrPull managed identity, creates PostgreSQL Flexible Server
result: [pending]

### 9. Deploy script uses commit SHA
expected: Open `scripts/deploy.sh` — uses `COMMIT_SHA=$(git rev-parse --short HEAD)`, builds via `az acr build`, image tag is `teamflow:${COMMIT_SHA}` (no `:latest`), scripts are executable (`ls -la scripts/` shows `x` bit)
result: [pending]

### 10. GitLab CI/CD pipeline
expected: Open `.gitlab-ci.yml` — has `build` and `deploy` stages, deploy has `needs: [build]`, both trigger on `$CI_COMMIT_BRANCH == "main"`, uses `mcr.microsoft.com/azure-cli` image, no `docker:dind` or `privileged: true`, manual deploy job present
result: [pending]

### 11. Azure env template
expected: Open `backend/.env.azure.example` — contains `DATABASE_URL=postgresql+asyncpg://...?ssl=require`, `ENVIRONMENT=production`, `COOKIE_SECURE=True`, `WEBSITES_PORT=80`, `SECRET_KEY=REPLACE_WITH_64_CHAR_HEX_SECRET`
result: [pending]

### 12. README Azure deployment guide
expected: Open `README.md` — has `## Azure Deployment` section containing: architecture diagram, `bash scripts/setup-azure.sh` setup step, `bash scripts/deploy.sh` deploy step, table of 7 GitLab CI/CD variables (AZURE_CLIENT_ID etc.), `az ad sp create-for-rbac` command, `/api/health` verification curl
result: [pending]

## Summary

total: 12
passed: 0
issues: 0
pending: 12
skipped: 0
blocked: 0

## Gaps

[none yet]
