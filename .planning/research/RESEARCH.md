# Research: TeamFlow — Domain Findings

*Gathered: 2026-04-22*

## 1. Azure Deployment — FastAPI + Docker on Azure App Service

**Source:** Microsoft Learn — Deploy containerized FastAPI on Azure App Service

### Recommended Architecture
- **Azure Container Registry (ACR)** — private Docker image registry; images pushed here, pulled by App Service via managed identity (no credentials needed)
- **Azure App Service (Linux, B1+ SKU)** — `az webapp create --container-image-name registry.azurecr.io/image:tag` pulls from ACR
- **Managed Identity** — App Service is assigned `AcrPull` role on the resource group; no explicit registry credentials stored
- **Connection string config** — `DATABASE_URL`, `SECRET_KEY`, `AI_MODEL`, etc. set as Azure App Service Application Settings (environment variables injected at runtime)

### Deployment Steps (for our backend)
```
az acr build --registry $ACR_NAME --image teamflow-backend:latest ./backend
az webapp create --resource-group $RG --plan webplan --name teamflow-api \
  --assign-identity [system] --role AcrPull \
  --container-image-name $ACR_NAME.azurecr.io/teamflow-backend:latest
```

### Frontend
- SvelteKit with `adapter-node` → Docker container → same pattern (separate App Service or served from same container with nginx)
- Alternative: Azure Static Web Apps for the SvelteKit build output (cheaper, simpler)

### Key Findings
- Azure App Service supports Docker containers natively on Linux plans
- B1 SKU (~$13/month) sufficient for a team of 5–15
- WebSocket connections are supported on Azure App Service (no configuration needed for FastAPI WebSocket)
- `DATABASE_URL` connection string to Azure Database for PostgreSQL Flexible Server is a direct drop-in replacement for the existing asyncpg config

---

## 2. Team Performance Metrics — What to Measure

**Source:** Atlassian — Five Agile Metrics; Jellyfish, Cortex — Engineering KPIs

### The 5 Core Agile Metrics (supervisor-relevant)

| Metric | What it measures | How to compute from existing data |
|--------|-----------------|----------------------------------|
| **Sprint Velocity** | Tasks/points completed per sprint | Count `done` tasks per sprint period grouped by milestone |
| **Sprint Burndown** | Work remaining vs time | Track `todo+in_progress` task count over time within a sprint |
| **Cycle Time** | Time from `in_progress` → `done` per task | `completed_at - updated_at` (when status flipped to in_progress) |
| **On-time Rate** | % tasks completed before `due_date` | `completed_at <= due_date` ratio per member |
| **Workload Distribution** | Tasks assigned per member right now | Count `assignee_id` tasks in active (non-done) states |

### Individual Performance (per team member)
- Tasks completed (last 7 / 30 / 90 days)
- On-time completion rate
- Average cycle time
- Current active task count (workload indicator)
- Overdue task count

### Supervisor-only view
- Team comparison table (all members side-by-side)
- Highlight: overloaded (>X active tasks) / underloaded (<Y tasks)
- At-risk items: tasks with `due_date < now + 2 days` still in `todo` or `in_progress`

### Anti-patterns to avoid
- Don't compare velocity across members as absolute ranking (estimation is subjective)
- Don't penalize members who break down work into smaller tasks (higher task count ≠ less efficient)
- Frame metrics as coaching data, not punishment data

---

## 3. GitHub Actions CI/CD → Azure App Service

**Source:** Microsoft Learn — Deploy to Azure App Service by using GitHub Actions

### Recommended Pipeline Structure
```yaml
# .github/workflows/deploy.yml
name: Deploy to Azure
on:
  push:
    branches: [main]
permissions:
  id-token: write
  contents: read

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: azure/login@v2
        with:
          client-id: ${{ secrets.AZURE_CLIENT_ID }}
          tenant-id: ${{ secrets.AZURE_TENANT_ID }}
          subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}
      # Build and push Docker images to ACR
      - name: Build backend
        run: az acr build --registry ${{ secrets.ACR_NAME }} --image teamflow-backend:${{ github.sha }} ./backend
      - name: Build frontend
        run: az acr build --registry ${{ secrets.ACR_NAME }} --image teamflow-frontend:${{ github.sha }} ./frontend
      # Deploy to App Service
      - uses: azure/webapps-deploy@v3
        with:
          app-name: teamflow-api
          images: ${{ secrets.ACR_NAME }}.azurecr.io/teamflow-backend:${{ github.sha }}
```

### Auth Method: OpenID Connect (Recommended)
- No long-lived credentials stored in GitHub secrets
- Uses Azure Federated Credentials + GitHub OIDC
- Secrets needed: `AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, `AZURE_SUBSCRIPTION_ID`, `ACR_NAME`

### Manual Deploy Script (fallback)
```bash
#!/bin/bash
# scripts/deploy.sh
az acr build --registry $ACR_NAME --image teamflow-backend:latest ./backend
az acr build --registry $ACR_NAME --image teamflow-frontend:latest ./frontend
az webapp config container set --name teamflow-api --resource-group $RG \
  --container-image-name $ACR_NAME.azurecr.io/teamflow-backend:latest
az webapp config container set --name teamflow-frontend --resource-group $RG \
  --container-image-name $ACR_NAME.azurecr.io/teamflow-frontend:latest
```

### Database Migration Strategy
- Alembic `alembic upgrade head` should run as a startup command (not in CI)
- Azure App Service startup command: `alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000`

---

## Key Decisions Informed by Research

1. **Deployment model**: Two separate Azure App Service instances (backend + frontend) sharing one ACR + one Azure DB for PostgreSQL Flexible Server
2. **Auth for CI/CD**: OIDC federated credentials (no stored service principal secrets)
3. **Alembic migrations**: Run at container startup via startup command (not as a CI step)
4. **Performance metrics**: Compute from existing `Task` model fields (`status`, `due_date`, `completed_at`, `assignee_id`, `created_at`) — no new DB columns needed for v1
5. **WebSocket on Azure**: Supported natively on App Service Linux — no special config needed
