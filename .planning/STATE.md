---
gsd_state_version: 1.0
milestone: v2.1
milestone_name: Open WebUI-Style Project Structure Refactor
status: executing
last_updated: "2026-04-27T14:36:49.012Z"
last_activity: 2026-04-27 -- Phase 19 execution complete
progress:
  total_phases: 4
  completed_phases: 1
  total_plans: 4
  completed_plans: 4
  percent: 25
---

# State: TeamFlow

## Current Status

**Milestone:** v2.1 — Open WebUI-Style Project Structure Refactor
**Active Phase:** Phase 19 — Refactor Map & Safety Baseline (COMPLETE)
**Last Session:** 2026-04-27

## Current Position

Phase: 19 (refactor-map-safety-baseline) — COMPLETE
Plan: 4 of 4
Status: All plans complete — ready for Phase 20 and Phase 21
Last activity: 2026-04-27 -- Phase 19 execution complete

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

## Resume Point

Phase 19 complete. Phase 20 (backend restructure) and Phase 21 (frontend restructure) can now be planned independently. Next: `/gsd-discuss-phase 20` or `/gsd-plan-phase 20`.

## Accumulated Context

### Roadmap Evolution

- Milestone 1 (Phases 1-11) complete.
- Milestone 2.0 (Phases 12-17) roadmap created 2026-04-24 and paused for the structural refactor.
- Milestone v2.1 (Phases 18-21) roadmap created 2026-04-26 as an independent structural refactor before resuming feature expansion.

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

### Pending Todos

- `2026-04-26-status-transition-graph-workflow.md` — Status transition graph / workflow rules (YouTrack-style) [area: ui]

### Watch-Out List

1. Open WebUI uses `backend/open_webui/` and root `src/`; TeamFlow currently uses `backend/app/` and `frontend/src/`, so phase plans must decide what to mirror exactly versus adapt safely.
2. Current imports use `from app...`; backend restructuring must update uvicorn targets, tests, Alembic env, scripts, and Docker startup together.
3. Frontend route URLs must not change during structure moves.
4. Existing uncommitted frontend changes and phase summaries predate v2.1; do not overwrite or revert them.

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
