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

## Requirements

### Validated

- ✓ Task CRUD with status (todo/in_progress/review/done/blocked) and priority — existing
- ✓ Project and Milestone management — existing
- ✓ Kanban board with drag-and-drop — existing
- ✓ Agile sprint view — existing
- ✓ AI task input (NLP → task fields) — existing
- ✓ Real-time WebSocket chat (channels, DMs, presence) — existing
- ✓ Scheduler / calendar events — existing
- ✓ Notification reminders (scheduler-driven) — existing
- ✓ JWT cookie-based authentication — existing
- ✓ Docker containerization (backend, frontend, postgres) — existing

### Active

- [ ] Supervisor performance dashboard — per-member metrics (tasks completed, velocity, on-time rate, workload)
- [ ] Team timeline / Gantt-style view — visual project timeline across team members
- [ ] AI project status summary — "how is the project going?" answered with real data
- [ ] AI task breakdown — describe a feature, AI decomposes it into subtasks
- [ ] Azure production deployment — Azure Web App Service + Azure Database for PostgreSQL (flexible connection string config)
- [ ] CI/CD pipeline — GitHub Actions auto-deploy to Azure on push to main + manual deploy script fallback
- [ ] Production hardening — Alembic migrations, env-configurable CORS, secure SECRET_KEY validation, rate limiting on auth/AI endpoints
- [ ] Mobile-responsive UI — team accesses on phone, not just desktop

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

**Key concerns to address:**
- No Alembic migrations yet (`create_all` only — not production safe)
- Hardcoded `SECRET_KEY` default must be blocked in production
- CORS origins are hardcoded (need env var for Azure deployment)
- Zero test coverage (auth and AI endpoints are highest risk)
- In-memory WebSocket state (acceptable for single-instance Azure deployment)

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
*Last updated: 2026-04-22 after initialization*
