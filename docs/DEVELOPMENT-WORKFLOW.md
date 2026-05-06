# TeamFlow Development Workflow

This document describes the complete development workflow for TeamFlow, from initial setup to deployment.

## Overview

TeamFlow is a full-stack application with:
- **Backend:** FastAPI (Python 3.13) + PostgreSQL 16
- **Frontend:** SvelteKit 5 + Bun + TailwindCSS
- **Deployment:** Azure Web App Service + Azure PostgreSQL

## Prerequisites

- Python 3.11+
- Bun (`brew install oven-sh/bun/bun`)
- PostgreSQL (local via Docker) or Azure PostgreSQL for production
- Azure CLI (for deployment)
- Git

## Local Development Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd team-flow
```

### 2. Start PostgreSQL (Local)

```bash
docker compose up postgres -d
```

### 3. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your DATABASE_URL and AI_API_KEY
```

**Environment Variables Required:**
```env
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/teamflow
SECRET_KEY=your-secret-key-here
AI_MODEL=gpt-4o
OPENAI_API_KEY=your-api-key
ENVIRONMENT=development
```

### 4. Frontend Setup

```bash
cd frontend

# Install dependencies
bun install

# No additional config needed
```

### 5. Start Development Servers

**Backend (Terminal 1):**
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

**Frontend (Terminal 2):**
```bash
cd frontend
bun run dev
```

Access the application at `http://localhost:5173`.

## Development Workflow

### Feature Development

1. **Create a Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Backend Changes**
   - Add models to `backend/app/models/`
   - Add schemas to `backend/app/schemas/`
   - Add routes to `backend/app/routers/`
   - Register routes in `backend/app/main.py`
   - Create Alembic migration if schema changes
     ```bash
     cd backend
     alembic revision --autogenerate -m "description"
     alembic upgrade head
     ```

3. **Frontend Changes**
   - Add routes to `frontend/src/routes/`
   - Add API calls to `frontend/src/lib/api.ts`
   - Add utilities to `frontend/src/lib/utils.ts`
   - Update stores in `frontend/src/lib/stores/`

4. **Testing**
   ```bash
   # Backend tests
   cd backend
   pytest tests/
   
   # Frontend tests
   cd frontend
   bun run test
   ```

5. **Commit Changes**
   ```bash
   git add .
   git commit -m "feat: description of changes"
   ```

### Code Review Process

1. Push feature branch to remote
2. Create merge request (GitLab) or pull request (GitHub)
3. Request review from team lead
4. Address review feedback
5. Merge to `main` after approval

### Database Migrations

**Create Migration:**
```bash
cd backend
alembic revision --autogenerate -m "description"
```

**Apply Migration:**
```bash
alembic upgrade head
```

**Rollback Migration:**
```bash
alembic downgrade -1
```

**View Migration History:**
```bash
alembic history
```

## Testing

### Backend Tests

```bash
cd backend
pytest tests/ -v
```

Run specific test file:
```bash
pytest tests/test_tasks.py -v
```

Run with coverage:
```bash
pytest --cov=app tests/
```

### Frontend Tests

```bash
cd frontend
bun run test
```

Run Playwright E2E tests:
```bash
bun run playwright test
```

## Production Deployment

### Azure Deployment

**Prerequisites:**
- Azure CLI installed and configured (`az login`)
- Azure subscription with Contributor access

**First-Time Setup:**
```bash
# Set database password
export DB_ADMIN_PASS="your-secure-password"

# Provision Azure resources
bash scripts/setup-azure.sh
```

This creates:
- Resource group
- Azure Container Registry (ACR)
- App Service plan
- App Service (with AcrPull managed identity)
- PostgreSQL Flexible Server

**Configure App Settings:**
After provisioning, update these in Azure Portal (App Service → Configuration):
- `SECRET_KEY` - Generate with: `python -c "import secrets; print(secrets.token_hex(32))"`
- `OPENAI_API_KEY` - Your AI provider key
- `DATABASE_URL` - PostgreSQL connection string with `?ssl=require`
- `ENVIRONMENT` - Must be `production`
- `ALLOWED_ORIGINS` - Your App Service URL

**Deploy:**
```bash
bash scripts/deploy.sh
```

This builds the Docker image via ACR and deploys to App Service.

### CI/CD Pipeline

The `.gitlab-ci.yml` pipeline runs automatically on push to `main`.

**Required GitLab CI/CD Variables:**
- `AZURE_CLIENT_ID`
- `AZURE_CLIENT_SECRET`
- `AZURE_TENANT_ID`
- `AZURE_SUBSCRIPTION_ID`
- `ACR_NAME`
- `APP_NAME`
- `RG`

**Pipeline Stages:**
1. **Build** - Builds and pushes Docker image to ACR
2. **Deploy** - Updates App Service container image

## Troubleshooting

### Backend Issues

**Database Connection Error:**
- Verify PostgreSQL is running: `docker ps`
- Check DATABASE_URL in `.env`
- Ensure database exists: `docker exec -it teamflow-postgres psql -U user -d teamflow`

**Migration Error:**
- Check Alembic version: `alembic current`
- Manually mark migration as applied if needed: `alembic stamp head`

### Frontend Issues

**Build Errors:**
- Clear node_modules: `rm -rf node_modules && bun install`
- Check Bun version: `bun --version`

**API Connection Issues:**
- Verify backend is running on port 8000
- Check CORS settings in backend `.env`

## Common Commands

### Backend
```bash
# Run server
uvicorn app.main:app --reload --port 8000

# Run tests
pytest tests/

# Create migration
alembic revision --autogenerate -m "description"

# Apply migration
alembic upgrade head

# Seed demo data
python -m app.scripts.seed_demo
```

### Frontend
```bash
# Run dev server
bun run dev

# Build for production
bun run build

# Run tests
bun run test

# Type check
bun run check
```

### Docker
```bash
# Start PostgreSQL
docker compose up postgres -d

# Stop PostgreSQL
docker compose down

# Build and run full stack
docker compose up --build
```

## Best Practices

1. **Always run migrations locally before deploying**
2. **Write tests for new features**
3. **Use descriptive commit messages** (conventional commits)
4. **Keep branches focused on single features**
5. **Update documentation when changing APIs**
6. **Test in local environment before pushing**
7. **Review security implications of changes** (especially RBAC-related)

## Support

For issues or questions:
- Check existing documentation in `docs/`
- Review `.planning/` for phase-specific context
- Check GitHub/GitLab issues
- Contact team lead for production deployment issues
