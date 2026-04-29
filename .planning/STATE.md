---
gsd_state_version: 1.0
milestone: v2.3
milestone_name: Timeline Clarity, Navigation IA & Scoped Visibility
status: executing
last_updated: "2026-04-29T15:36:50.272Z"
last_activity: 2026-04-29
progress:
  total_phases: 5
  completed_phases: 2
  total_plans: 14
  completed_plans: 8
  percent: 57
---

# State: TeamFlow

## Current Status

**Milestone:** v2.3 — Timeline Clarity, Navigation IA & Scoped Visibility
**Active Phase:** Phase 28 — Milestone Planning & Decisions (Ready to execute)
**Last Session:** 2026-04-29T15:36:10.823Z

## Current Position

Phase: 29 (scoped-team-visibility-leadership-rbac) — EXECUTING
Plan: 2 of 4
Status: Ready to execute
Last activity: 2026-04-29

## Session Notes

- Milestone 1 complete: all 11 phases done, 100% coverage.
- Milestone 2.0 shipped with hierarchy, sprints, status sets, KPI work, reminders, and workflow rules.
- Milestone v2.1 started 2026-04-26 to refactor backend and frontend structure toward an Open WebUI-inspired organization before continuing feature expansion.
- User preference: Project uses Bun for frontend operations.
- SvelteKit uses adapter-static with fallback: 200.html (SPA mode).
- Monolith Dockerfile: nginx + uvicorn + supervisord, port 80 for Azure App Service.
- All schema changes go through Alembic migrations.
- Milestone v2.2 shipped on 2026-04-28: standup updates, knowledge-sharing scheduler, and weekly board with AI summary.
- Milestone v2.3 roadmap created 2026-04-29: 4 phases covering sidebar IA, clearer timeline and milestones, and scoped visibility / RBAC.

## Resume Point

Next: `/gsd-execute-phase 28` to build the milestone planning and decisions plans.

Alternative: `/gsd-review --phase 28 --all` to peer review the plans before execution.

## Accumulated Context

### Roadmap Evolution

- Milestone 1 (Phases 1-11) complete.
- Milestone 2.0 (Phases 12-18) shipped with hierarchy, sprints, statuses, KPI work, reminders, and workflow rules.
- Milestone v2.1 (Phases 19-22) shipped on 2026-04-28 as the structure refactor baseline.
- Milestone v2.2 (Phases 23-25) shipped on 2026-04-28: standup posts, knowledge-sharing scheduler, weekly board, and AI summary.
- Milestone v2.3 (Phases 26-29) planned on 2026-04-29: grouped navigation, clearer timeline and milestones, and scoped leadership visibility.
- Phase 30 added on 2026-04-29: Phase 18 status-transition follow-up hardening.

### Architecture Decisions (Milestone 2.0)

- SubTeam not Team: single-org deployment; Organization wrapper adds a join with zero value.
- Dual-write for status migration: retain tasks.status enum alongside new tasks.custom_status_id FK for the full feature-build period; drop old column after KPI queries verified.
- `is_done` replaces hardcoded done check: update_task endpoint must use `custom_status.is_done == true` after Phase 15, not `TaskStatus.done`.
- Sprint reminders reuse the existing `EventNotification` table and 60-second poller; unique constraint on `(event_type, event_ref_id, user_id)` prevents duplicates.
- KPI queries should stay as grouped aggregate queries, not N+1 loops.

### Architecture Decisions (Milestone v2.1)

- Follow Open WebUI structure as inspiration, not as an exact clone.
- Keep backend under `backend/` and frontend under `frontend/` unless a later plan explicitly accepts the runtime and build impact of moving SvelteKit to repo-root `src/`.
- Preserve API routes, Svelte routes, auth behavior, task workflows, AI task input, WebSocket chat, scheduler behavior, Docker/Azure runtime, and Alembic history.

### Architecture Decisions (Milestone v2.2)

- Standup posts store a server-side frozen task snapshot.
- Knowledge Sessions use a dedicated model and scoped visibility inside `/schedule`.
- Weekly Board summaries are cached per ISO week with on-demand cooldown plus scheduled generation.
- Frontend markdown rendering must stay sanitized before any `{@html}` usage.

### Architecture Decisions (Milestone v2.3)

- Keep existing public route URLs; improve navigation through grouping and hierarchy rather than route churn.
- Treat timeline and milestones as planning surfaces that must expose milestone state, related tasks, and decision signal together.
- The requested visibility model is broader than the current `admin` / `supervisor` / `member` enum, so Phase 29 must decide whether to add roles, add scope attributes, or map existing roles while preserving data.
- Apply visibility rules consistently across backend filters, frontend navigation, and every people-aware screen.

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

1. Existing route URLs must stay stable even though the sidebar structure changes.
2. Timeline clarity work should reuse current project, milestone, and task data before introducing new tables or state.
3. Milestone decision tracking may need persistence, but only if current milestone/task models cannot express it cleanly.
4. The requested leadership visibility rules are broader than the current enum and sub-team ownership model.
5. Existing uncommitted repo changes are unrelated; do not overwrite or revert them while planning v2.3.

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
**Completed Phase:** 19 (refactor-map-safety-baseline) — 4 plans — 2026-04-27 [v2.1]
**Completed Phase:** 20 (backend-package-restructure) — 5 plans — 2026-04-27 [v2.1]
**Completed Phase:** 21 (frontend-sveltekit-structure) — 4 plans — 2026-04-27 [v2.1]
**Completed Phase:** 22 (runtime-integration-regression-verification) — 4 plans — 2026-04-27 [v2.1]
**Completed Phase:** 23 (standup-updates) — 4 plans — 2026-04-28 [v2.2]
**Completed Phase:** 24 (knowledge-sharing-scheduler) — 3 plans — 2026-04-28 [v2.2]
**Completed Phase:** 25 (team-weekly-board-ai-summary) — 4 plans — 2026-04-28 [v2.2]
**Planned Phase:** 26 (navigation-information-architecture) — 3 plans — 2026-04-29 [v2.3]
**Planned Phase:** 27 (timeline-gantt-clarity) — 0 plans — 2026-04-29 [v2.3]
**Planned Phase:** 28 (milestone-planning-decisions) — 4 plans — 2026-04-29 [v2.3]
**Planned Phase:** 29 (scoped-team-visibility-leadership-rbac) — 0 plans — 2026-04-29 [v2.3]
