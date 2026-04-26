# Milestones: TeamFlow

---

## v1.0 — Production-Ready Team Management Platform

**Status:** Complete ✓
**Completed:** 2026-04-24
**Phases:** 11 (8 implementation + 3 verification)

### What Shipped

- Production hardening — Alembic migrations, rate limiting, SECRET_KEY validation, CORS env var
- RBAC role model — admin/supervisor/member with backend enforcement
- Supervisor performance dashboard — `/performance` with per-member metrics, workload chart, at-risk panel
- Team timeline view — Gantt-style `/timeline` with project color-coding and task bars
- Enhanced AI features — AI task breakdown and AI project status summary
- Mobile-responsive UI — hamburger nav, touch-friendly Kanban, dvh-aware layouts
- Azure deployment + GitHub Actions CI/CD — App Service, ACR, deploy scripts, pipeline
- User invite & team management — email invites with token + 6-digit code, acceptance flow

### Exit Criteria Met

- ✓ All 11 phases complete
- ✓ `/performance` dashboard live with real team data
- ✓ `/timeline` view operational
- ✓ AI breakdown and project summary working
- ✓ App mobile-responsive
- ✓ Azure deployment scripts and CI/CD pipeline delivered
- ✓ Manual deploy script documented

---

## v2.0 — Team Hierarchy, Sprints & Advanced Analytics

**Status:** Paused / superseded for current planning focus
**Started:** 2026-04-24

### Goals

Transform TeamFlow from a single-team tool into a multi-team platform with sprint-driven project management, Trello-style customizable boards, and data-grounded KPI analytics.

### Completed Phases

| Phase | Name | Status | Completed |
|-------|------|--------|-----------|
| 15 | Custom Kanban Statuses | ✅ Done | 2026-04-26 |

Phase 15 delivered: DB-backed `StatusSet`/`CustomStatus` models, backend CRUD/reorder/safe-delete/project-override API, frontend API client + 5 reusable status components, Kanban board driven by DB statuses, `is_done` completion semantics, Manage Statuses panel on `/tasks`, Statuses panel on `/projects`.

### Current Note

v2.0 work remains available in prior roadmap and phase artifacts. The active planning focus moved to v2.1 on 2026-04-26 for an independent structural refactor before continuing feature expansion.

---

## v2.1 — Open WebUI-Style Project Structure Refactor

**Status:** Planning
**Started:** 2026-04-26

### Goals

Refactor TeamFlow's FastAPI backend and SvelteKit frontend into a cleaner Open WebUI-inspired repository structure while preserving existing behavior, deployment, and testability.
