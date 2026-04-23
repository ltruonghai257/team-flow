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
