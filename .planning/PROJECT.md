# TeamFlow

**A private team task management platform for supervisors who need real control.**

## What This Is

TeamFlow is a full-stack web application for a supervisor and their team to manage work across multiple parallel projects. It replaces heavy tools like Jira or Trello with something purpose-built: fast task input, Kanban and sprint views, real-time collaboration, shared planning surfaces, and performance visibility for the people leading delivery.

The app is built and functional. This milestone focuses on making planning clearer in the product itself by regrouping navigation, improving the timeline and milestone experience, and tightening visibility to match real reporting lines.

## Core Value

The supervisor can open TeamFlow each morning and immediately know:
- Who is overloaded or underloaded
- What's at risk of missing a deadline
- How each person has been performing over time

The team uses it willingly because it's simpler than Jira, the planning views are easier to scan, and collaboration is built in.

## Who It's For

- **Supervisor (primary user):** Creates projects, assigns tasks, monitors team performance, and steers delivery
- **Team members (5-15 people):** Update task status, create tasks, collaborate, and track their work
- **Leadership roles:** Managers, supervisors, and assistant managers need different visibility scopes across teams and planning surfaces

## Current Milestone: v2.3 Timeline Clarity, Navigation IA & Scoped Visibility

**Goal:** Make TeamFlow easier to scan and safer to use by regrouping navigation around workflows, turning timeline and milestones into clearer planning surfaces, and tightening team visibility around real reporting lines.

**Target features:**
- Sidebar information architecture: regroup related pages into item/sub-item sections so the sidebar reflects feature areas instead of a flat route list
- Timeline and Gantt clarity: improve `/timeline` with clearer milestone emphasis, task rollups, planning signal, and decision highlights
- Milestone planning visibility: make milestone views show planning state, decisions, and linked tasks more directly
- Scoped team visibility: members only see peers in their sub-team, supervisors and assistant managers see peer leaders at the same level, and managers can see everyone

## Requirements

### Validated (Milestone 1)

- ✓ Task CRUD with status (todo/in_progress/review/done/blocked) and priority — Phase 1
- ✓ Project and Milestone management — existing
- ✓ Kanban board with drag-and-drop — existing
- ✓ Agile sprint view — existing
- ✓ AI task input (NLP -> task fields) — existing
- ✓ Real-time WebSocket chat (channels, DMs, presence) — existing
- ✓ Scheduler / calendar events — existing
- ✓ Notification reminders (scheduler-driven) — existing
- ✓ JWT cookie-based authentication — Phase 1
- ✓ Docker containerization (backend, frontend, postgres) — existing
- ✓ Alembic migrations, CORS env var, SECRET_KEY validation, rate limiting — Phase 1
- ✓ RBAC roles (admin/supervisor/member), backend enforcement — Phase 2
- ✓ Supervisor performance dashboard (`/performance`) — Phase 3
- ✓ Team timeline / Gantt-style view (`/timeline`) — Phase 4
- ✓ AI task breakdown and AI project status summary — Phase 5
- ✓ Mobile-responsive UI (hamburger nav, touch Kanban) — Phase 6
- ✓ Azure deployment + GitHub Actions CI/CD — Phase 7
- ✓ User invite and team management (email token + code flow) — Phase 8

### Validated (Milestone 2.1)

- ✓ Backend code organized into Open WebUI-style FastAPI package — Phase 20
- ✓ Frontend code organized into Open WebUI-style SvelteKit folders — Phase 21
- ✓ Runtime, Docker, Alembic, test, and development commands work after import/path migration — Phase 22
- ✓ Refactor verified by backend tests, frontend build, and smoke checks — Phase 22

### Validated (Milestone 2.2)

- ✓ Member can post a daily or weekly standup update with a frozen task snapshot — Phase 23
- ✓ Standup updates are visible in a team feed with filtering and author-owned edits — Phase 23
- ✓ Knowledge Sharing sessions can be scheduled inside `/schedule` with scoped visibility and reminders — Phase 24
- ✓ Team Weekly Board supports markdown posts, week navigation, and AI summaries — Phase 25

### Active (Milestone 2.3)

- [ ] Sidebar groups related features into parent/child navigation sections without changing route URLs
- [ ] Timeline provides a clearer Gantt view with milestone-first emphasis and linked task rollups
- [ ] Milestone views highlight planning status, decisions, and related execution tasks
- [ ] Visibility rules are consistent across team, timeline, milestones, schedule, updates, and board screens
- [ ] Members only see peers in their own sub-team
- [ ] Supervisors and assistant managers can see same-level leaders in their allowed parent scope
- [ ] Managers can see everyone

### Out of Scope

- Native mobile apps (iOS/Android) — web-first is still sufficient
- Multi-tenant SaaS — this remains a private single-org deployment
- Public API / webhooks — internal tool only
- Route URL redesign — navigation clarity should come from grouping and hierarchy, not broken links

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Azure Web App Service | Managed hosting, no VM maintenance, easy to scale | Pending |
| Azure Database for PostgreSQL (flexible) | Managed Postgres, connect via connection string, compatible with existing asyncpg setup | Pending |
| GitHub Actions CI/CD + manual script | Automation as primary, escape hatch for direct deploys | Pending |
| Group navigation by workflow area, not by raw route list | Sidebar should mirror how supervisors think about work, planning, and people | Planned for v2.3 |
| Treat milestone planning and decisions as first-class timeline signals | Supervisors need milestone context, not only task bars, to judge risk | Planned for v2.3 |
| Plan v2.3 RBAC around manager / supervisor / assistant manager / member visibility rules | User-visible scope rules changed beyond the current admin/supervisor/member model and need explicit implementation phases | Planned for v2.3 |
| LiteLLM for AI | Swap any model via single env var | Existing |

## Context

**Tech stack:** FastAPI (Python 3.13) + SvelteKit 5 + PostgreSQL 16 + TailwindCSS

**Reference structure:** Open WebUI repository (`https://github.com/open-webui/open-webui`) inspired the current package organization. TeamFlow keeps backend under `backend/` and frontend under `frontend/`.

**Key concerns to address:**
- Keep existing route URLs stable while redesigning sidebar grouping and page hierarchy
- Preserve current timeline, milestone, and team data while improving how planning and decisions are surfaced
- Apply one consistent visibility model across backend queries, frontend stores, and navigation guards
- Preserve existing Alembic history and database state; any role or scope model change must migrate safely from the current data

**Deployment target:** Azure Web App Service (internal, browser-based). DB via connection string to Azure Database for PostgreSQL.

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition:**
1. Requirements invalidated? -> Move to Out of Scope with reason
2. Requirements validated? -> Move to Validated with phase reference
3. New requirements emerged? -> Add to Active
4. Decisions to log? -> Add to Key Decisions
5. "What This Is" still accurate? -> Update if drifted

**After each milestone:**
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-04-29 after starting milestone v2.3*
