# TeamFlow

**A private team task management platform for supervisors who need real control.**

## What This Is

TeamFlow is a full-stack web application for a supervisor and their team to manage work across multiple parallel projects. It replaces heavy tools like Jira or Trello with something purpose-built: fast task input, Kanban and sprint views, real-time collaboration, shared planning surfaces, and performance visibility for the people leading delivery.

The app is built and functional. This milestone focuses on making planning clearer in the product itself by regrouping navigation, improving the timeline and milestone experience, and tightening visibility to match real reporting lines.

## Core Value

The supervisor can open TeamFlow each morning and immediately know:

-   Who is overloaded or underloaded
-   What's at risk of missing a deadline
-   How each person has been performing over time

The team uses it willingly because it's simpler than Jira, the planning views are easier to scan, and collaboration is built in.

## Who It's For

-   **Supervisor (primary user):** Creates projects, assigns tasks, monitors team performance, and steers delivery
-   **Team members (5-15 people):** Update task status, create tasks, collaborate, and track their work
-   **Leadership roles:** Managers, supervisors, and assistant managers need different visibility scopes across teams and planning surfaces

## Current Milestone: v2.4 Professional Role-Aware Dashboard

**Goal:** Transform the existing basic dashboard (`/`) into a professional, role-aware overview surface where each role sees exactly what they need at a glance.

**Target features:**

-   Professional UI redesign: modern card hierarchy, visual health signals, progress indicators, and data visualizations replacing raw-number-only stat cards
-   My tasks & deadlines (all roles): personalized task queue for the logged-in user showing assigned tasks sorted by urgency, overdue flagged red, due-soon highlighted
-   Team health panel (supervisor / assistant manager / manager): workload distribution across members (overloaded/underloaded), at-risk signals from existing performance data
-   KPI summary strip (supervisor / assistant manager / manager): average KPI score, completion rate, needs-attention count with quick link to `/performance`
-   Activity feed (all roles): recent standup posts as a team pulse panel, scoped by visibility rules

## Requirements

### Validated (Milestone 1)

-   ✓ Task CRUD with status (todo/in_progress/review/done/blocked) and priority — Phase 1
-   ✓ Project and Milestone management — existing
-   ✓ Kanban board with drag-and-drop — existing
-   ✓ Agile sprint view — existing
-   ✓ AI task input (NLP -> task fields) — existing
-   ✓ Real-time WebSocket chat (channels, DMs, presence) — existing
-   ✓ Scheduler / calendar events — existing
-   ✓ Notification reminders (scheduler-driven) — existing
-   ✓ JWT cookie-based authentication — Phase 1
-   ✓ Docker containerization (backend, frontend, postgres) — existing
-   ✓ Alembic migrations, CORS env var, SECRET_KEY validation, rate limiting — Phase 1
-   ✓ RBAC roles (admin/supervisor/member), backend enforcement — Phase 2
-   ✓ Supervisor performance dashboard (`/performance`) — Phase 3
-   ✓ Team timeline / Gantt-style view (`/timeline`) — Phase 4
-   ✓ AI task breakdown and AI project status summary — Phase 5
-   ✓ Mobile-responsive UI (hamburger nav, touch Kanban) — Phase 6
-   ✓ Azure deployment + GitHub Actions CI/CD — Phase 7
-   ✓ User invite and team management (email token + code flow) — Phase 8

### Validated (Milestone 2.1)

-   ✓ Backend code organized into Open WebUI-style FastAPI package — Phase 20
-   ✓ Frontend code organized into Open WebUI-style SvelteKit folders — Phase 21
-   ✓ Runtime, Docker, Alembic, test, and development commands work after import/path migration — Phase 22
-   ✓ Refactor verified by backend tests, frontend build, and smoke checks — Phase 22

### Validated (Milestone 2.2)

-   ✓ Member can post a daily or weekly standup update with a frozen task snapshot — Phase 23
-   ✓ Standup updates are visible in a team feed with filtering and author-owned edits — Phase 23
-   ✓ Knowledge Sharing sessions can be scheduled inside `/schedule` with scoped visibility and reminders — Phase 24
-   ✓ Team Weekly Board supports markdown posts, week navigation, and AI summaries — Phase 25

### Validated (Milestone 2.3)

-   ✓ Sidebar groups related features into parent/child navigation sections — Phase 26
-   ✓ Timeline provides milestone-first Gantt view with linked task rollups and planning signal — Phase 27
-   ✓ Milestone views show planning status, decisions, and related execution tasks — Phase 28
-   ✓ Visibility rules enforced across team, timeline, milestones, schedule, updates, and board screens — Phase 29
-   ✓ Members only see peers in their own sub-team — Phase 29
-   ✓ Supervisors and assistant managers can see same-level leaders in their allowed parent scope — Phase 29
-   ✓ Managers can see everyone — Phase 29

### Active (Milestone 2.4)

-   [ ] Dashboard has a professional visual layout with card hierarchy, health signals, and data visualizations
-   [ ] All roles see their own assigned tasks sorted by urgency on the dashboard
-   [ ] Overdue tasks are flagged red; tasks due within 48h are highlighted on the dashboard
-   [ ] Supervisor/assistant manager/manager sees team member workload status (overloaded/healthy/underloaded)
-   [ ] At-risk members are visually distinguished in the team health panel
-   [ ] Supervisor/assistant manager/manager sees KPI summary (avg score, completion rate, needs-attention count) on the dashboard
-   [ ] All roles see a scoped activity feed of recent standup posts on the dashboard
-   [ ] Activity feed respects existing visibility rules (member sees own team, supervisor/manager see their scope)

### Out of Scope

-   Native mobile apps (iOS/Android) — web-first is still sufficient
-   Multi-tenant SaaS — this remains a private single-org deployment
-   Public API / webhooks — internal tool only
-   Route URL redesign — navigation clarity should come from grouping and hierarchy, not broken links

## Key Decisions

| Decision                                                                                 | Rationale                                                                                                                 | Outcome          |
| ---------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------- | ---------------- |
| Azure Web App Service                                                                    | Managed hosting, no VM maintenance, easy to scale                                                                         | Pending          |
| Azure Database for PostgreSQL (flexible)                                                 | Managed Postgres, connect via connection string, compatible with existing asyncpg setup                                   | Pending          |
| GitHub Actions CI/CD + manual script                                                     | Automation as primary, escape hatch for direct deploys                                                                    | Pending          |
| Group navigation by workflow area, not by raw route list                                 | Sidebar should mirror how supervisors think about work, planning, and people                                              | Shipped v2.3     |
| Treat milestone planning and decisions as first-class timeline signals                   | Supervisors need milestone context, not only task bars, to judge risk                                                     | Shipped v2.3     |
| Plan v2.3 RBAC around manager / supervisor / assistant manager / member visibility rules | User-visible scope rules changed beyond the current admin/supervisor/member model and need explicit implementation phases | Shipped v2.3     |
| Extend dashboard API to return role-scoped data in one call                              | Avoid N+1 client-side calls; backend returns the right data shape for each role                                           | Planned for v2.4 |
| Dashboard UI uses role-conditional sections, not a single layout for all                 | Members, supervisors, and managers have meaningfully different information needs                                          | Planned for v2.4 |
| LiteLLM for AI                                                                           | Swap any model via single env var                                                                                         | Existing         |

## Context

**Tech stack:** FastAPI (Python 3.13) + SvelteKit 5 + PostgreSQL 16 + TailwindCSS

**Reference structure:** Open WebUI repository (`https://github.com/open-webui/open-webui`) inspired the current package organization. TeamFlow keeps backend under `backend/` and frontend under `frontend/`.

**Key concerns to address:**

-   Keep existing route URLs stable while redesigning sidebar grouping and page hierarchy
-   Preserve current timeline, milestone, and team data while improving how planning and decisions are surfaced
-   Apply one consistent visibility model across backend queries, frontend stores, and navigation guards
-   Preserve existing Alembic history and database state; any role or scope model change must migrate safely from the current data

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

_Last updated: 2026-05-06 after starting milestone v2.4_
