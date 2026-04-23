# Roadmap: TeamFlow

*Created: 2026-04-22*
*Milestone 1: Production-Ready Team Management Platform*

---

## Milestone 1 Overview

**Goal:** Ship a production-deployed TeamFlow with supervisor analytics, Azure hosting, and CI/CD - replacing Jira/Trello for a 5–15 person team.

**Definition of Done:** Supervisor can access `/performance` dashboard with real team data; app deployed on Azure App Service; CI/CD pipeline live; mobile-responsive.

---

## Phase 1: Production Hardening

**Goal:** Fix all critical issues that block production deployment.

**Delivers:**
- Alembic migrations set up, initial migration generated
- `create_all` replaced with `alembic upgrade head` at startup
- `SECRET_KEY` startup validation (rejects default value)
- CORS origins from env var (`ALLOWED_ORIGINS`)
- Rate limiting on auth and AI endpoints (`slowapi`)
- `datetime.utcnow()` → `datetime.now(timezone.utc)` throughout

**Depends on:** Nothing (foundational)

**Canonical refs:**
- `.planning/codebase/CONCERNS.md` - items 1, 2, 11, 12
- `backend/app/main.py`
- `backend/app/config.py`
- `backend/app/database.py`

---

## Phase 2: RBAC & Role Model

**Goal:** Formalize the role system so supervisor-only features are enforced server-side.

**Delivers:**
- `User.role` enum: `admin`, `supervisor`, `member`
- Backend dependency `require_supervisor()` for protected endpoints
- Registration defaults to `member`; role change by admin only
- Frontend routes guard based on role from auth store

**Depends on:** Phase 1 (needs stable auth layer)

**Canonical refs:**
- `backend/app/auth.py`
- `backend/app/models.py`
- `backend/app/routers/users.py`
- `.planning/REQUIREMENTS.md` REQ-07

---

## Phase 3: Supervisor Performance Dashboard

**Goal:** Build the `/performance` route and backing API so supervisors can evaluate team output.

**Delivers:**
- `GET /api/dashboard/performance` - per-member metrics (active tasks, completed 30d, on-time rate, avg cycle time, overdue count)
- `/performance` frontend route (supervisor-only, redirect others)
- Team overview table with traffic-light status indicator
- Workload bar chart (active tasks per member)
- At-risk panel (tasks due within 2 days, not done)
- Individual member detail view (weekly completions, on-time trend, active task list)

**Depends on:** Phase 2 (role checks)

**Canonical refs:**
- `.planning/REQUIREMENTS.md` REQ-02
- `.planning/research/RESEARCH.md` §2 (metrics formulas)
- `backend/app/models.py` - Task, User models
- `backend/app/routers/dashboard.py`

---

## Phase 4: Team Timeline View

**Goal:** Give supervisors and team members a Gantt-style visual of project progress.

**Delivers:**
- `/timeline` frontend route (all roles)
- Horizontal timeline showing milestones and tasks per project
- Color-coded by project, overdue items visually distinct
- Time range selector (week / month / custom)
- Task bars with assignee initials, status color, click-to-edit

**Depends on:** Phase 1 (stable DB), Phase 3 (establishes performance page pattern)

**Canonical refs:**
- `.planning/REQUIREMENTS.md` REQ-03
- `backend/app/models.py` - Milestone, Task, Project
- `frontend/src/routes/` - routing pattern

---

## Phase 5: Enhanced AI Features

**Goal:** Extend AI from task creation to task breakdown and project status summary.

**Delivers:**
- `POST /api/tasks/ai-breakdown` - NLP description → list of subtask drafts
- `POST /api/ai/project-summary` - project_id → natural-language status summary (data-grounded)
- Frontend: "Break down with AI" button on task creation (shows editable subtask list)
- Frontend: "Summarize" button on project detail page
- AI assistant chat understands "summarize project X" intent

**Depends on:** Phase 1 (stable AI rate limiting), Phase 3 (project data for summaries)

**Canonical refs:**
- `.planning/REQUIREMENTS.md` REQ-04
- `backend/app/routers/ai.py` - existing LiteLLM pattern
- `backend/app/routers/tasks.py` - existing ai-parse pattern
- `.planning/research/RESEARCH.md` §2 (metrics for summary prompt)

---

## Phase 6: Mobile-Responsive UI

**Goal:** Make TeamFlow usable on phones so team members can update tasks on the go.

**Delivers:**
- Sidebar collapses to hamburger menu on mobile (375px+)
- All existing routes mobile-adapted
- Kanban board horizontal scroll on mobile
- Performance dashboard table horizontally scrollable
- Task forms usable on mobile keyboard

**Depends on:** Phase 3, Phase 4 (need final UI structure before mobile pass)

**Canonical refs:**
- `.planning/REQUIREMENTS.md` REQ-06
- `frontend/src/routes/+layout.svelte` - sidebar
- `frontend/src/lib/components/tasks/KanbanBoard.svelte`

---

## Phase 8: User Invite & Team Management

**Goal:** Allow supervisors and admins to add or invite users to the team, with email-based invitation flow including a validation code and confirmation link.

**Delivers:**
- `POST /api/teams/invite` - send email invitation with unique token + 6-digit validation code (expires 72h)
- `POST /api/teams/add` - directly add an existing user to a team (supervisor/admin only)
- `GET /api/invites/validate?token=…` - validate invite token and return invite metadata
- `POST /api/invites/accept` - accept invite with token + validation code → creates/activates user account
- Email template: invite email with team name, sender name, validation code, and accept link
- Frontend: "Invite Member" modal on team management page (email input, role selector)
- Frontend: "Add Member" direct-add flow for existing users
- Frontend: Invite acceptance page at `/invite/accept?token=…` (code entry + account setup)
- Pending invites list visible to supervisors/admins
- Backend guards: `require_supervisor_or_admin()` dependency on invite/add endpoints

**Depends on:** Phase 2 (RBAC roles), Phase 1 (stable auth layer)

**Canonical refs:**
- `.planning/REQUIREMENTS.md`
- `backend/app/auth.py`
- `backend/app/models.py`
- `backend/app/routers/`
- `frontend/src/routes/`

---

## Phase 7: Azure Deployment & CI/CD

**Goal:** Deploy TeamFlow to Azure App Service with automated CI/CD pipeline.

**Delivers:**
- `scripts/setup-azure.sh` - one-time Azure resource provisioning (ACR, App Service plans, App Services, PostgreSQL Flexible Server)
- `scripts/deploy.sh` - manual deploy script (ACR build + App Service update)
- `.github/workflows/deploy.yml` - CI/CD pipeline (OIDC auth, push-to-main trigger, builds backend + frontend Docker images, deploys to Azure)
- `backend/.env.azure.example` - full env var template for Azure App Settings
- Backend startup command: `alembic upgrade head && uvicorn app.main:app`
- README: Azure setup guide and deployment instructions
- App accessible at `https://teamflow-api.azurewebsites.net` (backend) and `https://teamflow.azurewebsites.net` (frontend)

**Depends on:** All prior phases (deploy the complete app)

**Canonical refs:**
- `.planning/REQUIREMENTS.md` REQ-05
- `.planning/research/RESEARCH.md` §1 (Azure App Service + ACR), §3 (GitHub Actions)
- `docker-compose.yml` - existing Docker setup
- `backend/Dockerfile`, `frontend/Dockerfile`

---

## Phase Sequence

```
Phase 1 - Production Hardening     [Critical blocker]
  └─ Phase 2 - RBAC                [Enables supervisor features]
       ├─ Phase 3 - Performance    [Core supervisor value]
       │    ├─ Phase 4 - Timeline  [Parallel to Phase 5 possible]
       │    └─ Phase 5 - AI        [Parallel to Phase 4 possible]
       │          └─ Phase 6 - Mobile UI
       │                └─ Phase 7 - Azure Deploy
       └─ Phase 8 - User Invite    [Parallel workstream from Phase 2]
```

---

## Phase 9: Generate Verification Documentation (Phases 1-3)

**Goal:** Create VERIFICATION.md files for foundational phases to enable requirement verification.

**Delivers:**
- VERIFICATION.md for Phase 1 (Production Hardening) - REQ-01 coverage table
- VERIFICATION.md for Phase 2 (RBAC Role Model) - REQ-07 coverage table
- VERIFICATION.md for Phase 3 (Supervisor Performance Dashboard) - REQ-02 coverage table
- VALIDATION.md frontmatter updates for Phases 2 and 3 (nyquist_compliant status)

**Depends on:** Phases 1, 2, 3 complete (documentation only)

**Canonical refs:**
- `.planning/v1.0-MILESTONE-AUDIT.md` - verification gaps
- `.planning/REQUIREMENTS.md` - REQ-01, REQ-02, REQ-07 acceptance criteria
- `.claude/get-shit-done/templates/VALIDATION.md` - template

---

## Phase 10: Generate Verification Documentation (Phases 4-5)

**Goal:** Create VERIFICATION.md files for feature phases to enable requirement verification.

**Delivers:**
- VERIFICATION.md for Phase 4 (Team Timeline View) - REQ-03 coverage table
- VERIFICATION.md for Phase 5 (Enhanced AI Features) - REQ-04 coverage table
- VALIDATION.md files for Phases 4 and 5 (missing entirely)

**Depends on:** Phases 4, 5 complete (documentation only)

**Canonical refs:**
- `.planning/v1.0-MILESTONE-AUDIT.md` - verification gaps
- `.planning/REQUIREMENTS.md` - REQ-03, REQ-04 acceptance criteria
- `.claude/get-shit-done/templates/VALIDATION.md` - template

---

## Phase 11: Generate Verification Documentation (Phases 6-8)

**Goal:** Create VERIFICATION.md files for deployment and management phases to enable requirement verification.

**Delivers:**
- VERIFICATION.md for Phase 6 (Mobile Responsive UI) - REQ-06 coverage table
- VERIFICATION.md for Phase 7 (Azure Deployment CI/CD) - REQ-05 coverage table
- VERIFICATION.md for Phase 8 (User Invite Team Management) - verification documentation
- VALIDATION.md files for Phases 7 and 8 (missing entirely)
- VALIDATION.md fix for Phase 6 (set nyquist_compliant: true)

**Depends on:** Phases 6, 7, 8 complete (documentation only)

**Canonical refs:**
- `.planning/v1.0-MILESTONE-AUDIT.md` - verification gaps
- `.planning/REQUIREMENTS.md` - REQ-05, REQ-06 acceptance criteria
- `.claude/get-shit-done/templates/VALIDATION.md` - template

---

## Milestone 1 Exit Criteria

- [ ] All 11 phases complete (8 implementation + 3 verification)
- [ ] `/performance` dashboard live with real team data
- [ ] `/timeline` view operational
- [ ] AI breakdown and project summary working
- [ ] App mobile-responsive
- [ ] Deployed on Azure - accessible via URL
- [ ] GitHub Actions CI/CD pipeline passing
- [ ] Manual deploy script documented
