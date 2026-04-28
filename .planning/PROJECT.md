# TeamFlow

**A private team task management platform for supervisors who need real control.**

## What This Is

TeamFlow is a full-stack web application for a supervisor (and their team of 5–15 people) to manage work across multiple parallel projects. It replaces heavy tools like Jira/Trello with something purpose-built: fast task input (including AI), Kanban and Agile sprint views, real-time collaboration via WebSocket chat, and a performance layer that gives the supervisor the data needed to evaluate team members fairly.

## Current State

v2.2 is shipped: standup updates, knowledge sharing scheduler, and weekly board are live and archived in `.planning/milestones/`.

## Next Milestone Goals

- Define fresh v2.3 requirements from scratch
- Clarify timeline, navigation IA, and scoped visibility behavior
- Keep the existing task, scheduler, and AI workflows stable while expanding the product

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

## Archived Milestone Snapshot: v2.2 Team Updates, Knowledge Sharing & Weekly Board

**Goal:** Empower team members with a daily/weekly standup flow, a knowledge sharing scheduler embedded in the existing calendar, and a team-wide weekly markdown board with AI-generated summaries.

**Target features:**
- Member Updates: freeform standup post (what I did, pending, blockers) plus task status snapshot, visible to the whole team and supervisor
- Knowledge Sharing Scheduler: new "Knowledge Sessions" tab inside the existing Calendar — manager schedules sessions with topic, description, source/references, presenter (assignee), session type (presentation/demo/workshop/Q&A), duration, and tags
- Team Weekly Board: shared markdown space where any member posts weekly updates; AI generates a summary automatically at end of week and on demand

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

### Validated (Milestone 2.1)

- ✓ Backend code organized into Open WebUI-style FastAPI package — Phase 20
- ✓ Frontend code organized into Open WebUI-style SvelteKit folders — Phase 21
- ✓ Runtime, Docker, Alembic, test, and development commands work after import/path migration — Phase 22
- ✓ Refactor verified by backend tests, frontend build, and smoke checks — Phase 22

### Validated (Milestone 2.2)

- ✓ Member can post a daily/weekly standup update (what I did, pending items, blockers)
- ✓ Standup post includes a snapshot of the member's current task statuses
- ✓ Standup updates are visible to all team members and the supervisor
- ✓ Manager can schedule Knowledge Sharing sessions (topic, description, references, presenter, session type, duration, tags)
- ✓ Knowledge Sessions appear as a dedicated tab/section within the existing Calendar view
- ✓ Team members can view upcoming Knowledge Sessions
- ✓ Any team member can post a weekly markdown update to the Team Weekly Board
- ✓ AI generates a weekly summary of all board posts automatically (end of week) and on demand

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
*Last updated: 2026-04-28 after starting milestone v2.2*
