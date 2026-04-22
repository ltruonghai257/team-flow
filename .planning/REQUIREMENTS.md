# Requirements: TeamFlow

*Defined: 2026-04-22*
*Stack: FastAPI (Python 3.13) + SvelteKit 5 + PostgreSQL 16 + TailwindCSS*
*Deployment: Azure App Service (Linux) + Azure Database for PostgreSQL Flexible Server*

---

## Milestone 1: Production-Ready Team Management Platform

### Goal
Transform the existing TeamFlow codebase into a production-deployed, team-usable application with a supervisor performance layer — replacing Jira/Trello for a team of 5–15 people across multiple parallel projects.

---

## REQ-01: Production Hardening

**Priority:** Critical — must be done before any deployment

### Acceptance Criteria
- [ ] Alembic migrations set up and initial migration generated from existing `models.py`
- [ ] `create_all` replaced with `alembic upgrade head` run at container startup
- [ ] `SECRET_KEY` startup validation: app refuses to start if value matches the default (`"change-me-in-production"`)
- [ ] CORS allowed origins read from `ALLOWED_ORIGINS` env var (comma-separated), not hardcoded
- [ ] Rate limiting on `POST /api/auth/token` (max 10 req/min per IP)
- [ ] Rate limiting on `POST /api/ai/*` endpoints (max 30 req/min per user)
- [ ] All `datetime.utcnow()` replaced with `datetime.now(timezone.utc).replace(tzinfo=None)`

**Existing code refs:**
- `backend/app/main.py` — CORS setup
- `backend/app/config.py` — SECRET_KEY default
- `backend/app/database.py` — replace create_all

---

## REQ-02: Supervisor Performance Dashboard

**Priority:** High — core supervisor value

### Acceptance Criteria
- [ ] New route `/performance` (supervisor-only, redirect non-supervisors to `/`)
- [ ] Team overview table: all members with columns: Name | Active Tasks | Completed (30d) | On-time Rate | Avg Cycle Time | Status
- [ ] Status column uses traffic-light indicator: green (on track) / yellow (watch) / red (overloaded or has overdue tasks)
- [ ] Workload chart: bar chart showing active task count per member (visual scan for balance)
- [ ] At-risk panel: tasks where `due_date < now + 2 days` and status is `todo` or `in_progress`
- [ ] Clicking a member name opens their individual profile view
- [ ] Individual member view: tasks completed per week (last 8 weeks), on-time rate trend, current active tasks list
- [ ] Performance data is supervisor-only (role check: `current_user.role === "admin"` or `"supervisor"`)
- [ ] New `/api/dashboard/performance` endpoint returning aggregated per-member metrics

**Metrics computed from existing `Task` fields:**
- Completed (30d): `completed_at > now-30d AND status = done`
- On-time rate: `completed_at <= due_date` ratio (only tasks with due_date set)
- Avg cycle time: average `(completed_at - created_at)` in hours
- Active tasks: tasks where `assignee_id = member.id AND status NOT IN (done, blocked)`
- Overdue: `due_date < now AND status NOT IN (done)`

---

## REQ-03: Team Timeline / Project Overview

**Priority:** High — supervisor daily use

### Acceptance Criteria
- [ ] New route `/timeline` visible to all team members
- [ ] Horizontal Gantt-style timeline showing milestones and their tasks per project
- [ ] Color-coded by project (uses existing `project.color`)
- [ ] Time range selector: current week / current month / custom range
- [ ] Task bars show: title, assignee avatar initials, status color
- [ ] Overdue milestones/tasks visually distinct (red outline or marker)
- [ ] Milestone markers on the timeline axis
- [ ] Clicking a task opens task detail / edit

---

## REQ-04: Enhanced AI Capabilities

**Priority:** Medium

### REQ-04a: AI Task Breakdown
- [ ] New endpoint `POST /api/tasks/ai-breakdown` — accepts `{"description": "...", "project_id": N}` and returns a list of subtask drafts
- [ ] AI decomposes the description into 3–8 concrete tasks with title, priority, estimated_hours
- [ ] Frontend: button "Break down with AI" on task creation form — shows subtask list for review before creating
- [ ] User can edit/remove individual subtasks before batch-creating them

### REQ-04b: AI Project Status Summary
- [ ] New endpoint `POST /api/ai/project-summary` — accepts `{"project_id": N}` and returns natural-language status summary
- [ ] Summary includes: milestone progress, overdue tasks, recent completions, at-risk items
- [ ] Summary is generated from real project data (not just LLM hallucination) — data injected into prompt
- [ ] Accessible from project detail page via "Summarize" button
- [ ] Supervisor can also ask via AI assistant chat: "Summarize project X"

---

## REQ-05: Azure Deployment

**Priority:** Critical — delivery mechanism

### REQ-05a: Infrastructure
- [ ] Azure Container Registry (ACR) for Docker images
- [ ] Azure App Service (Linux, B1 SKU) for backend (FastAPI) — separate instance from frontend
- [ ] Azure App Service (Linux, B1 SKU) for frontend (SvelteKit node adapter)
- [ ] Azure Database for PostgreSQL Flexible Server — connection via `DATABASE_URL` connection string env var
- [ ] All secrets (SECRET_KEY, AI keys, DB URL) stored as Azure App Service Application Settings

### REQ-05b: GitHub Actions CI/CD Pipeline
- [ ] `.github/workflows/deploy.yml` triggered on push to `main`
- [ ] Uses OIDC federated credentials (no stored service principal secrets)
- [ ] Pipeline steps: checkout → Azure login → build backend image to ACR → build frontend image to ACR → deploy backend App Service → deploy frontend App Service
- [ ] Alembic migration runs as backend container startup command (not in CI)
- [ ] Pipeline status visible in GitHub — green/red badge

### REQ-05c: Manual Deploy Script
- [ ] `scripts/deploy.sh` — manually triggers ACR build + App Service container update
- [ ] `scripts/setup-azure.sh` — one-time Azure resource provisioning (ACR, App Service plan, App Services, DB)
- [ ] README section: step-by-step Azure setup and first deploy instructions

### REQ-05d: Environment Configuration
- [ ] `backend/.env.azure.example` — template for all Azure App Service env vars
- [ ] `ALLOWED_ORIGINS` includes the Azure App Service URLs
- [ ] `COOKIE_SECURE=True` default confirmed for HTTPS-only Azure deployment
- [ ] `DATABASE_URL` format: `postgresql+asyncpg://user:pass@host:5432/dbname?ssl=require`

---

## REQ-06: Mobile-Responsive UI

**Priority:** Medium — team adoption

### Acceptance Criteria
- [ ] All existing routes (dashboard, tasks, projects, milestones, team, schedule, AI) render correctly on mobile (375px+)
- [ ] Sidebar collapses to hamburger menu on mobile
- [ ] Kanban board scrolls horizontally on mobile (columns don't collapse)
- [ ] Performance dashboard table is scrollable horizontally on mobile
- [ ] Task creation form is usable on mobile (inputs not obscured by keyboard)

---

## REQ-07: Role-Based Access Control (RBAC) Clarification

**Priority:** Medium — existing partial implementation

### Acceptance Criteria
- [ ] `User.role` enum values formally defined: `admin`, `supervisor`, `member`
- [ ] Supervisor and admin can: create/delete projects, view performance dashboard
- [ ] Members can: create tasks, update task status, view their own metrics
- [ ] Backend middleware enforces role checks (not just frontend routing)
- [ ] Registration defaults to `member` role; role upgrade done by admin only

---

## Non-Requirements (Out of Scope for Milestone 1)

- Native iOS/Android apps
- Multi-tenant / SaaS features
- Email notifications
- OAuth / SSO (existing username/password auth is sufficient)
- Public API / webhooks
- Custom domain setup (Azure default `.azurewebsites.net` URL is acceptable for v1)
- Time tracking / billing integration
- File attachments on tasks

---

## Constraints

- Must run on existing tech stack (no framework changes)
- PostgreSQL schema changes via Alembic only (no manual DB edits)
- All AI calls via LiteLLM (model swappable via `AI_MODEL` env var)
- Single Azure region deployment (no geo-redundancy for v1)
- Azure B1 SKU budget constraint (~$26/month total for both App Services)

---

## Definition of Done (Milestone 1)

- [ ] All REQ-01 items passing
- [ ] Supervisor can log in and see the `/performance` dashboard with real team data
- [ ] `/timeline` route shows project milestones and tasks across projects
- [ ] AI task breakdown and AI project summary working end-to-end
- [ ] App is deployed and accessible at Azure App Service URL
- [ ] GitHub Actions pipeline deploys successfully on push to `main`
- [ ] Manual deploy script documented and tested
- [ ] App loads on mobile (iPhone-sized viewport)
- [ ] README updated with deployment instructions
