---
plan: "07-02"
wave: 1
phase: 7
title: "Monolith Dockerfile (nginx + uvicorn + supervisord)"
depends_on:
  - "07-01"
files_modified:
  - Dockerfile
  - nginx.conf
  - supervisord.conf
  - .dockerignore
autonomous: true
requirements_addressed:
  - REQ-05a
  - REQ-05b
---

# Plan 07-02: Monolith Dockerfile

## Objective

Create a single multi-stage `Dockerfile` at the repo root that builds the complete TeamFlow
application — SvelteKit static frontend + FastAPI backend — into one container image.
nginx serves static files and proxies `/api/*` and `/ws/*` to uvicorn (port 8000).
supervisord manages both nginx and uvicorn processes.

## Context (from CONTEXT.md decisions)

- **D-01/D-02**: Multi-stage Dockerfile at repo root — Bun stage builds frontend, Python stage installs backend deps, final stage combines both with nginx + supervisord
- **D-03**: SvelteKit `adapter-static` build output (from Plan 07-01) serves as static files — no Node runtime
- **D-04**: supervisord manages nginx + uvicorn crash restarts
- **D-05**: nginx routing: `/api/*` → uvicorn port 8000, `/ws/*` → uvicorn with WS upgrade, `/` → static files with `try_files`
- **D-06**: Single App Service (Linux, B1) — one container, port 80
- **D-18**: Alembic `upgrade head` runs via `main.py` lifespan — **no separate migration step needed** (already implemented)

## Tasks

### Task 1: Create nginx.conf

<read_first>
- `docker-compose.yml` — port mappings (backend:8000, frontend:3000)
- `backend/app/main.py` — WebSocket router included at `/ws/`
- `frontend/src/lib/websocket.ts` — WS connects to `window.location.host + /ws/chat`
</read_first>

<action>
Create `nginx.conf` at the repo root with:

```nginx
worker_processes 1;
error_log /dev/stderr warn;
pid /tmp/nginx.pid;

events {
    worker_connections 1024;
}

http {
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;
    access_log    /dev/stdout;
    sendfile      on;
    keepalive_timeout 65;

    server {
        listen 80;
        root /app/frontend/build;
        index 200.html;

        location /api/ {
            proxy_pass http://127.0.0.1:8000;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_read_timeout 120s;
        }

        location /ws/ {
            proxy_pass http://127.0.0.1:8000;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_read_timeout 3600s;
        }

        location / {
            try_files $uri $uri/ /200.html;
        }
    }
}
```
</action>

<acceptance_criteria>
- `nginx.conf` exists at repo root
- File contains `proxy_pass http://127.0.0.1:8000` in the `/api/` block
- File contains `proxy_http_version 1.1` and `Connection "upgrade"` in the `/ws/` block
- File contains `try_files $uri $uri/ /200.html` in the `/` location
- File contains `listen 80`
</acceptance_criteria>

---

### Task 2: Create supervisord.conf

<read_first>
- `backend/app/main.py` — uvicorn startup: `app.main:app`, port 8000; Alembic runs in lifespan
- `backend/requirements.txt` — to confirm uvicorn path will be `/usr/local/bin/uvicorn`
</read_first>

<action>
Create `supervisord.conf` at the repo root with:

```ini
[supervisord]
nodaemon=true
logfile=/dev/null
logfile_maxbytes=0
user=root

[program:nginx]
command=/usr/sbin/nginx -c /etc/nginx/nginx.conf -g "daemon off;"
autostart=true
autorestart=true
priority=10
stdout_logfile=/dev/stdout
stdout_logfile_maxbytes=0
stderr_logfile=/dev/stderr
stderr_logfile_maxbytes=0

[program:uvicorn]
command=/usr/local/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 1
directory=/app/backend
autostart=true
autorestart=true
priority=20
stdout_logfile=/dev/stdout
stdout_logfile_maxbytes=0
stderr_logfile=/dev/stderr
stderr_logfile_maxbytes=0
environment=PYTHONUNBUFFERED="1"
```

Note: uvicorn `priority=20` starts after nginx (`priority=10`) — nginx is fast to start
and this avoids brief 502s. Alembic migration runs inside uvicorn's lifespan startup
so no separate migration program is needed.
</action>

<acceptance_criteria>
- `supervisord.conf` exists at repo root
- File contains `[program:nginx]` and `[program:uvicorn]`
- File contains `nodaemon=true`
- File contains `command=/usr/local/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000`
- File contains `directory=/app/backend` under the uvicorn program block
- File does NOT contain an alembic migration program (handled in lifespan)
</acceptance_criteria>

---

### Task 3: Create monolith Dockerfile at repo root

<read_first>
- `backend/Dockerfile` — existing backend image: `python:3.12-slim`, pip install, uvicorn CMD
- `frontend/Dockerfile` — existing frontend: `oven/bun:1` builder, `bun install --frozen-lockfile`, `bun run build`
- `backend/requirements.txt` — pip dependencies list
- `nginx.conf` — just created (to verify COPY path)
- `supervisord.conf` — just created (to verify COPY path)
</read_first>

<action>
Create `Dockerfile` at the repo root with:

```dockerfile
# Stage 1: Build SvelteKit static frontend
FROM oven/bun:1 AS frontend-builder
WORKDIR /app
COPY frontend/package.json frontend/bun.lock* ./
RUN bun install --frozen-lockfile
COPY frontend/ .
RUN bun run build

# Stage 2: Install Python backend dependencies
FROM python:3.12-slim AS backend-deps
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Stage 3: Final monolith image
FROM python:3.12-slim AS final

# Install nginx and supervisor
RUN apt-get update && apt-get install -y --no-install-recommends \
    nginx \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from backend-deps stage
COPY --from=backend-deps /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=backend-deps /usr/local/bin /usr/local/bin

# Copy SvelteKit static build
COPY --from=frontend-builder /app/build /app/frontend/build

# Copy backend application
COPY backend/ /app/backend/

# Copy nginx and supervisord configs
COPY nginx.conf /etc/nginx/nginx.conf
COPY supervisord.conf /etc/supervisor/conf.d/teamflow.conf

# Azure App Service listens on port 80
EXPOSE 80

CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/teamflow.conf"]
```
</action>

<acceptance_criteria>
- `Dockerfile` exists at repo root
- File contains `FROM oven/bun:1 AS frontend-builder`
- File contains `FROM python:3.12-slim AS backend-deps`
- File contains `FROM python:3.12-slim AS final`
- File contains `apt-get install -y --no-install-recommends nginx supervisor`
- File contains `COPY --from=frontend-builder /app/build /app/frontend/build`
- File contains `COPY backend/ /app/backend/`
- File contains `COPY nginx.conf /etc/nginx/nginx.conf`
- File contains `EXPOSE 80`
- File contains `CMD ["/usr/bin/supervisord"`
</acceptance_criteria>

---

### Task 4: Create .dockerignore at repo root

<read_first>
- `docker-compose.yml` — reference for what's in repo root
- `.gitignore` — existing ignore patterns to mirror
</read_first>

<action>
Create `.dockerignore` at the repo root with:

```
.git
.planning
.windsurf
.claude
**/__pycache__
**/*.pyc
**/*.pyo
**/.pytest_cache
**/node_modules
frontend/build
backend/.env
backend/.env.azure.example
*.md
.gitignore
docker-compose.yml
test-results/
tests/
```

This excludes planning docs, git history, node_modules (installed fresh in builder stage),
and the local `.env` file from the Docker build context.
</action>

<acceptance_criteria>
- `.dockerignore` exists at repo root
- File contains `.git`
- File contains `**/__pycache__`
- File contains `**/node_modules`
- File contains `backend/.env`
- File contains `.planning`
</acceptance_criteria>

---

### Task 5: Smoke-test the Docker build locally

<read_first>
- `Dockerfile` — just created
- `.dockerignore` — just created
- `nginx.conf` — just created
- `supervisord.conf` — just created
</read_first>

<action>
Run a local Docker build to verify the monolith image builds without errors:

```bash
docker build -t teamflow:local .
```

If the build succeeds, run a quick smoke test (requires a local `.env` or inline env vars):

```bash
docker run --rm -p 8080:80 \
  -e DATABASE_URL="postgresql+asyncpg://postgres:password@host.docker.internal:5432/taskmanager" \
  -e SECRET_KEY="test-secret-key-not-for-production" \
  -e ENVIRONMENT="development" \
  -e ALLOWED_ORIGINS="http://localhost:8080" \
  teamflow:local &

sleep 5
curl -sf http://localhost:8080/api/health
```

Expected: `{"status": "ok"}`
</action>

<acceptance_criteria>
- `docker build -t teamflow:local .` exits with code 0
- Docker image `teamflow:local` exists in local Docker images (`docker images | grep teamflow`)
- `curl http://localhost:8080/api/health` returns `{"status":"ok"}` when container is run with valid DB env vars (or migration failure is the only error, not nginx/uvicorn startup)
</acceptance_criteria>

---

## Verification Criteria

- [ ] `nginx.conf` at repo root with correct proxy_pass and WebSocket upgrade blocks
- [ ] `supervisord.conf` at repo root with nginx and uvicorn programs, `nodaemon=true`
- [ ] `Dockerfile` at repo root with 3 stages (frontend-builder, backend-deps, final)
- [ ] `.dockerignore` excludes `.git`, `node_modules`, `.env`, `.planning`
- [ ] `docker build -t teamflow:local .` exits 0
- [ ] Container serves `/api/health` → `{"status":"ok"}`

## must_haves

- Single Docker image that serves both frontend static files and backend API
- nginx correctly proxies `/api/*` and `/ws/*` to uvicorn on port 8000
- nginx serves SvelteKit `200.html` as SPA fallback for all other paths
- supervisord keeps both nginx and uvicorn running with auto-restart
- Image listens on port 80 (Azure App Service default)
- Alembic migrations run automatically via uvicorn lifespan (no separate step)

## threat_model

| Threat | Mitigation |
|--------|-----------|
| `.env` secrets copied into image | `.dockerignore` excludes `backend/.env` |
| `SECRET_KEY` default value in production | `config.py` validator rejects default when `ENVIRONMENT=production` |
| nginx serves arbitrary files outside `build/` | `root` is scoped to `/app/frontend/build`; no directory listing (`autoindex off` default) |
| Container runs as root | Acceptable for B1 SKU single-tenant container; future hardening: add non-root user |
