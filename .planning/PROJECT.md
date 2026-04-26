# TeamFlow

**A private team task management platform for supervisors who need real control.**

## What This Is

TeamFlow is a full-stack web application for a supervisor (and their team of 5–15 people) to manage work across multiple parallel projects. It replaces heavy tools like Jira/Trello with something purpose-built: fast task input (including AI), Kanban and Agile sprint views, real-time collaboration via WebSocket chat, and a performance layer that gives the supervisor the data needed to evaluate team members fairly.

The app is built and partially functional. This milestone focuses on hardening what exists, adding the supervisor performance/analytics layer, and making it production-ready on Azure.

## Core Value

The supervisor can open TeamFlow each morning and immediately know:
- Who is overloaded or underloaded
- What's at risk of missing a deadline
- How each person has been performing over time

The team uses it willingly because it's simpler than Jira — AI helps them create tasks, the board is clean, and collaboration is built in.

## Who It's For

- **Supervisor (primary user)**: Creates projects, assigns tasks, monitors team performance, pulls reports
- **Team members (5–15 people)**: Update task status, create tasks via AI input, chat, see their own and teammates' tasks
- **Visibility model**: Tasks visible to all team. Performance/evaluation metrics visible to supervisor only.

## Current Milestone: v2.1 Open WebUI-Style Project Structure Refactor

**Goal:** Refactor TeamFlow's FastAPI and SvelteKit code organization to follow the proven Open WebUI repository structure while preserving existing behavior.

**Target features:**
- Backend package structure aligned with Open WebUI: app package, routers, models/domain modules, schemas, migrations, utils, socket/websocket, config, and entrypoint
- Frontend SvelteKit structure aligned with Open WebUI: `src/lib/apis`, `components`, `stores`, `types`, `utils`, and route organization
- Import paths, build scripts, Docker/runtime entrypoints, Alembic config, and tests updated to match the new layout
- Zero behavior regressions: API contracts, auth, task workflows, AI task input, WebSocket chat, scheduler, and current UI routes keep working

## Requirements

### Validated (Milestone 1)

- ✓ Task CRUD with status (todo/in_progress/review/done/blocked) and priority — Phase 1
- ✓ Project and Milestone management — existing
- ✓ Kanban board with drag-and-drop — existing
- ✓ Agile sprint view — existing
- ✓ AI task input (NLP → task fields) — existing
- ✓ Real-time WebSocket chat (channels, DMs, presence) — existing
- ✓ Scheduler / calendar events — existing
- ✓ Notification reminders (scheduler-driven) — existing
- ✓ JWT cookie-based authentication — Phase 1
- ✓ Docker containerization (backend, frontend, postgres) — existing
- ✓ Alembic migrations, CORS env var, SECRET_KEY validation, rate limiting — Phase 1
- ✓ RBAC roles (admin/supervisor/member), backend enforcement — Phase 2
- ✓ Supervisor performance dashboard (/performance) — Phase 3
- ✓ Team timeline / Gantt-style view (/timeline) — Phase 4
- ✓ AI task breakdown and AI project status summary — Phase 5
- ✓ Mobile-responsive UI (hamburger nav, touch Kanban) — Phase 6
- ✓ Azure deployment + GitHub Actions CI/CD — Phase 7
- ✓ User invite & team management (email token + code flow) — Phase 8

### Active (Milestone 2.1)

- [ ] Backend code is organized into an Open WebUI-style FastAPI package without changing API behavior
- [ ] Frontend code is organized into Open WebUI-style SvelteKit folders without changing UI behavior
- [ ] Runtime, Docker, Alembic, test, and development commands work after import/path migration
- [ ] Refactor is verified by backend tests, frontend checks/builds, and targeted smoke checks for critical flows

### Out of Scope

- Native mobile apps (iOS/Android) — web-first is sufficient for team adoption
- Multi-tenant SaaS — this is a single-org private deployment
- Email notifications — in-app and push reminders are sufficient for v1
- Public API / webhooks — internal tool only

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Azure Web App Service | Managed hosting, no VM maintenance, easy to scale | — Pending |
| Azure Database for PostgreSQL (flexible) | Managed Postgres, connect via connection string, compatible with existing asyncpg setup | — Pending |
| GitHub Actions CI/CD + manual script | Automation as primary, escape hatch for direct deploys | — Pending |
| Hybrid visibility model | Team sees tasks; supervisor-only performance data | — Decided |
| LiteLLM for AI | Swap any model (OpenAI/Anthropic/Ollama) via single env var | — Existing |

## Context

**Tech stack:** FastAPI (Python 3.13) + SvelteKit 5 + PostgreSQL 16 + TailwindCSS

**Reference structure:** Open WebUI repository (`https://github.com/open-webui/open-webui`) — root SvelteKit app in `src/`, backend package under `backend/open_webui/`, backend subpackages for routers/models/migrations/utils/socket, and frontend `src/lib` groups for APIs, components, stores, types, and utils.

**Key concerns to address:**
- Avoid broad rewrites: this milestone is structural, not a feature redesign
- Keep public API paths, Svelte routes, auth behavior, task workflows, AI features, WebSocket chat, scheduler, and deployment commands stable
- Move code in small slices with compatibility shims only where needed during transition
- Preserve existing Alembic history and database state; no schema changes unless required for import-path/runtime correctness

**Deployment target:** Azure Web App Service (internal, browser-based, no custom domain required initially). DB via connection string to Azure Database for PostgreSQL.

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition:**
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone:**
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-04-26 after starting milestone v2.1*
