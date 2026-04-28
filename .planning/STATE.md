---
gsd_state_version: 1.0
milestone: v2.2
milestone_name: Team Updates, Knowledge Sharing & Weekly Board
status: executing
last_updated: "2026-04-28T07:27:48.996Z"
last_activity: 2026-04-28
progress:
  total_phases: 3
  completed_phases: 1
  total_plans: 8
  completed_plans: 5
  percent: 63
---

# State: TeamFlow

## Current Status

**Milestone:** v2.2 — Team Updates, Knowledge Sharing & Weekly Board
**Active Phase:** Phase 24 — Knowledge Sharing Scheduler (Ready to execute — 3 plans)
**Last Session:** 2026-04-28T07:11:03.163Z

## Current Position

Phase: 23 (standup-updates) — EXECUTING
Plan: 2 of 5
Status: Ready to execute
Last activity: 2026-04-28

## Session Notes

- Milestone 1 complete: all 11 phases done, 100% coverage.
- Milestone 2.0 roadmap: Phases 12-17. Phases 15 ✅ done. Phase 16 planned. Phase 17 (Sprint & Release Reminders) restored and planned. v2.1 starts AFTER Phase 17 completes.
- Milestone v2.1 started 2026-04-26: refactor backend/frontend structure to follow Open WebUI-inspired organization before continuing feature expansion.
- Reference repo: https://github.com/open-webui/open-webui
- v2.1 phase sequence: Phase 19 refactor map, Phase 20 backend restructure, Phase 21 frontend restructure, Phase 22 runtime/regression verification.
- User preference: Project uses Bun for frontend operations.
- SvelteKit uses adapter-static with fallback: 200.html (SPA mode).
- Monolith Dockerfile: nginx + uvicorn + supervisord, port 80 for Azure App Service.
- Zero new npm or Python packages unless a moved import cannot be resolved without one.
- All schema changes via Alembic migrations only; v2.1 should avoid schema changes unless required for runtime correctness.
- Milestone v2.2 roadmap created 2026-04-28: 3 phases, 22 requirements, 100% coverage.

## Resume Point

Phase 24 planned with research, UI-SPEC, and 3 execution plans. Next: `/gsd-execute-phase 24`.

## Accumulated Context

### Roadmap Evolution

- Milestone 1 (Phases 1-11) complete.
- Milestone 2.0 (Phases 12-17) roadmap created 2026-04-24 and paused for the structural refactor.
- Milestone v2.1 (Phases 18-21) roadmap created 2026-04-26 as an independent structural refactor before resuming feature expansion.
- Milestone v2.2 (Phases 23-25) roadmap created 2026-04-28: standup posts, KS scheduler, weekly board + AI summary.

### Architecture Decisions (Milestone 2.0)

- SubTeam not Team: single-org deployment; Organization wrapper adds a join with zero value.
- Dual-write for status migration: retain tasks.status enum alongside new tasks.custom_status_id FK for the full feature-build period; drop old column after KPI queries verified.
- is_done replaces hardcoded done check: update_task endpoint must use custom_status.is_done == true after Phase 15, not TaskStatus.done enum comparison.
- Sprint reminders via existing EventNotification table: insert rows on sprint activation; the existing 60s poll delivers them; unique constraint on (event_type, event_ref_id, user_id) prevents duplicates.
- KPI queries: all aggregations as single GROUP BY queries — no N+1.
- Verify layerchart version at Phase 16 kickoff (installed as next tag; code comments suggest it was bypassed).

### Architecture Decisions (Milestone v2.1)

- Follow Open WebUI structure as inspiration, not as an exact clone.
- Keep backend under `backend/` and frontend under `frontend/` unless a later plan explicitly accepts the runtime/build impact of moving SvelteKit to repo-root `src/`.
- Preserve API routes, Svelte routes, auth behavior, task workflows, AI task input, WebSocket chat, scheduler behavior, Docker/Azure runtime, and Alembic history.
- No new dependencies unless an existing import cannot be moved safely without one.

### Architecture Decisions (Milestone v2.2)

- New models: StandupPost (models/updates.py), KnowledgeSession (models/knowledge.py), WeeklyPost + WeeklyBoardSummary (models/board.py).
- StandupPost stores task_snapshot as JSONB (frozen at submit time, server-side — never a live query).
- NotificationEventType PostgreSQL enum: add `knowledge_session` value via ALTER TYPE migration with execute_as_transaction=False (must be outside a transaction block).
- KS sessions use a separate KnowledgeSession table (not the existing Schedule model which is user_id-scoped).
- KS sessions appear as a tab inside /schedule — no new top-level route.
- New routes: /updates (standup feed + form), /board (weekly board).
- Frontend markdown rendering: marked + DOMPurify; install both in Phase 23 alongside first {@html} usage. Never use {@html} without DOMPurify.sanitize().
- AI summary: cached per ISO week in WeeklyBoardSummary; 30-min cooldown on on-demand trigger; short-circuit with "no updates this week" if no posts exist.
- APScheduler CronTrigger(day_of_week='sun', hour=23) added to internal/scheduler_jobs.py for auto weekly summary.
- AI generation follows existing routers/ai.py project summary pattern via utils/ai_client.py.
- Zero new backend packages (apscheduler, litellm, sqlalchemy, alembic, pydantic already installed).

### Deferred Items

Items acknowledged and deferred at milestone close on 2026-04-28:

| Category | Item | Status |
|----------|------|--------|
| todo | 2026-04-26-status-transition-graph-workflow.md | pending |
| uat_gap | Phase 02: 02-UAT.md (7 pending scenarios) | testing |
| uat_gap | Phase 07: 07-UAT.md (12 pending scenarios) | testing |
| uat_gap | Phase 18: 18-UAT.md (4 pending scenarios) | testing |

### Pending Todos

- `2026-04-26-status-transition-graph-workflow.md` — Status transition graph / workflow rules (YouTrack-style) [area: ui]

### Watch-Out List

1. Open WebUI uses `backend/open_webui/` and root `src/`; TeamFlow currently uses `backend/app/` and `frontend/src/`, so phase plans must decide what to mirror exactly versus adapt safely.
2. Current imports use `from app...`; backend restructuring must update uvicorn targets, tests, Alembic env, scripts, and Docker startup together.
3. Frontend route URLs must not change during structure moves.
4. Existing uncommitted frontend changes and phase summaries predate v2.1; do not overwrite or revert them.
5. ALTER TYPE for NotificationEventType must run outside a transaction block — test against PostgreSQL container (SQLite silently passes).
6. StandupPost task_snapshot must be JSONB stored server-side at POST time — a live query at render time makes historical standups meaningless.
7. Always wrap markdown rendering: DOMPurify.sanitize(marked.parse(raw)) — stored XSS risk if sanitization is skipped.
8. AI summary: short-circuit with "no updates this week" if no posts exist to avoid hallucination on empty input.

## Flags

None

**Completed Phase:** 11 (verification-doc-phases-6-8) — 2026-04-24T02:00:00.000Z
**Completed Phase:** 10 (verification-doc-phases-4-5) — 2026-04-24T02:00:00.000Z
**Completed Phase:** 09 (verification-doc-phases-1-3) — 2026-04-24T01:30:00.000Z
**Completed Phase:** 03 (supervisor-performance-dashboard) — 2026-04-23T00:15:00.000Z
**Completed Phase:** 04 (team-timeline-view) — 2026-04-23T00:42:00.000Z
**Completed Phase:** 05 (enhanced-ai-features) — 2026-04-23T14:10:00.000Z
**Completed Phase:** 06 (mobile-responsive-ui) — 2026-04-23T14:30:00.000Z
**Completed Phase:** 07 (azure-deployment-ci-cd) — 2026-04-23T22:30:00.000Z
**Completed Phase:** 08 (user-invite-team-management) — 2026-04-24T00:00:00.000Z

**Completed Phase:** 15 (custom-kanban-statuses) — 2026-04-26
**Planned Phase:** 16 (advanced-kpi-dashboard) — 5 plans — 2026-04-26
**Planned Phase:** 17 (sprint-release-reminders) — 5 plans — 2026-04-26
**Planned Phase:** 18 (status-transition-graph) — 4 plans — 2026-04-26
**Completed Phase:** 19 (refactor-map-safety-baseline) — 4 plans — 2026-04-27 [v2.1]
**Completed Phase:** 20 (backend-package-restructure) — 5 plans — 2026-04-27 [v2.1]
**Completed Phase:** 21 (frontend-sveltekit-structure) — 4 plans — 2026-04-27 [v2.1]
**Completed Phase:** 22 (runtime-integration-regression-verification) — 4 plans — 2026-04-27 [v2.1]
