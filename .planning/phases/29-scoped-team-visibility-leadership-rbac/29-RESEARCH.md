# Phase 29: Scoped Team Visibility & Leadership RBAC - Research

**Date:** 2026-04-29
**Scope:** Current TeamFlow role enum, auth dependencies, sub-team scoping, team/invite management, and cross-surface visibility filters
**Research depth:** Level 0 - codebase pattern audit

## Summary

Phase 29 should replace the unreleased `admin` / `supervisor` / `member` role shape with the locked four-role model: `manager`, `supervisor`, `assistant_manager`, and `member`. Because the app is pre-release, the safest implementation is a clean role/scope update: remove old `admin` assumptions, update the demo seed reset path, and verify every people-aware backend surface through focused API tests.

The implementation should start by centralizing role and scope logic before touching individual routers. Today, each router applies sub-team filtering differently, and several detail/update endpoints fetch by ID without checking scope. A shared visibility helper or service will reduce drift and make VIS-05 testable.

## Current Code Findings

### Current Role Model

- `backend/app/models/enums.py` currently defines `UserRole` as `admin`, `supervisor`, and `member`.
- `backend/app/models/users.py` stores `User.role`, `User.sub_team_id`, `SubTeam.supervisor_id`, and `TeamInvite.role/sub_team_id`.
- `frontend/src/lib/stores/auth.ts` hardcodes the same three role strings and derives `isAdmin` / `isSupervisor`.
- `frontend/src/lib/navigation/sidebar.ts` also hardcodes role visibility for Performance as `admin` / `supervisor`.
- `backend/app/scripts/seed_demo.py` currently seeds one supervisor and several members only; it does not model manager or assistant-manager visibility.

### Auth And Scope Baseline

- `backend/app/utils/auth.py` centralizes `get_current_user`, `require_supervisor`, `require_admin`, `require_supervisor_or_admin`, and `get_sub_team`.
- `get_sub_team` currently treats members as their `User.sub_team_id`, supervisors as the first `SubTeam.supervisor_id == current_user.id`, and admins as all teams unless `X-SubTeam-ID` is provided.
- This model is too narrow for Phase 29 because assistant managers do not exist and managers should replace admins.
- It also couples one supervisor to one sub-team through `SubTeam.supervisor_id`, while the context says leaders have an allowed scope and can see peer leaders in the same parent/team scope.

### Backend Enforcement Gaps

- `backend/app/routers/users.py` filters list results by `get_sub_team` but `GET /users/{id}` and `PATCH /users/{id}` currently fetch by ID without scoped visibility.
- `backend/app/routers/projects.py` filters list/create by sub-team context but detail/update/delete endpoints fetch by project ID without scoped visibility.
- `backend/app/routers/tasks.py` filters list by project sub-team when a sub-team context exists, but detail/update/delete endpoints fetch task ID directly.
- `backend/app/routers/timeline.py` has list-level project filtering, but its member behavior is still old: members see only projects where they have assigned tasks instead of all team data in their own sub-team per VIS-01.
- `backend/app/routers/milestones.py` currently depends only on authentication and does not scope list/detail/write behavior to visible projects.
- `backend/app/routers/updates.py`, `backend/app/routers/board.py`, and `backend/app/services/weekly_board.py` mostly filter by sub-team context, but helper reuse is limited.
- `backend/app/routers/schedules.py` is user-owned only. Phase 29 needs a decision during implementation: keep schedule personal or expose scoped schedule visibility if the v2.3 schedule surface is expected to be team-aware.
- `backend/app/services/knowledge_sessions.py` already has scoped query helper patterns, but they use old admin/supervisor/member role assumptions.
- `backend/app/routers/performance.py` is privileged and sub-team aware, but it still uses `require_supervisor` and old admin terminology.

### Team And Invite Management Baseline

- `backend/app/routers/invites.py` lets supervisors/admins send invites and direct-add users. Non-admins cannot assign non-member roles today.
- Pending invite list and cancellation are not scoped; they return/cancel all pending invites for any supervisor/admin caller.
- Team management in `backend/app/routers/sub_teams.py` allows supervisor/admin creation/update/list, but only admins can delete.
- The `/team` frontend exposes sub-team tabs, invite role selects, direct-add role selects, and reminder proposal review with old `admin` labels.

### Frontend Integration Points

- `frontend/src/routes/+layout.svelte` shows the sub-team switcher only for `admin`, redirects non-supervisors away from `/performance`, and filters navigation through `sidebar.ts`.
- `frontend/src/routes/team/+page.svelte` contains old role labels, invite role options, sub-team supervisor selectors, and reminder settings behavior that distinguishes `admin` from everyone else.
- API clients are thin wrappers, so most frontend work is type/role copy, option filtering, and UI visibility rather than deep client state changes.
- Existing Playwright tests mock role strings as `member`; role fixture updates will be needed after replacing `admin`.

## Planning Implications

1. Create a shared role/scope foundation first. Rename/replace active roles, update auth dependencies, and add helper predicates for manager, leader, and member scope behavior.
2. Add backend tests for role predicates and visible user/team scope before broad router rewrites. The test should prove members are sub-team-only, supervisors/assistant managers see scoped members plus peer leaders, and managers see everyone.
3. Update team/invite management after the role foundation so role assignment and scope validation reuse the same helpers.
4. Roll the shared visibility helpers through project, task, timeline, milestone, updates, board, schedule/knowledge-session, notification, and performance surfaces.
5. Update frontend role typing, navigation filtering, `/team` controls, and demo seed data last so the UI and seed data match the backend contract.

## Constraints

- Do not build matrix management, many-to-many reporting lines, cross-team exceptions, or an org directory.
- Do not preserve old `admin` compatibility paths; the app is pre-release and the demo reset path is `python -m app.scripts.seed_demo`.
- Do not fold status-transition graph work into Phase 29.
- Backend filtering is the source of truth. Frontend hiding is helpful but not sufficient.
- Avoid scattering bespoke role checks. Shared helpers/services should be preferred.

## Validation Architecture

Phase 29 is authorization-heavy. Validation must prioritize focused backend tests that prove data cannot leak across scopes, then frontend tests that prove navigation and team-management affordances match the new roles.

- Backend quick check: `cd backend && rtk uv run pytest tests/test_visibility.py -q`
- Backend scoped regression check: `cd backend && rtk uv run pytest tests/test_visibility.py tests/test_sub_teams.py tests/test_projects.py tests/test_tasks.py tests/test_timeline.py tests/test_milestones.py tests/test_board.py tests/test_knowledge_sessions.py -q`
- Frontend quick check: `cd frontend && bun run check`
- Frontend browser check: `cd frontend && bun x playwright test tests/navigation-groups.spec.ts tests/team-visibility.spec.ts --workers=1`
- Seed check: `cd backend && python -m app.scripts.seed_demo`
- Full phase check: backend scoped regression check plus frontend quick/browser checks plus seed check.

## Recommendation

Plan Phase 29 in four executable waves:

1. Role and visibility foundation: replace the active role enum, update auth/scope helpers, and add focused visibility tests.
2. Team/invite/scope management: update user/team/invite endpoints and tests for manager-only leadership assignment and scoped member management.
3. Cross-surface enforcement: apply shared visibility helpers across project/task/timeline/milestone/update/board/schedule/knowledge/performance surfaces.
4. Frontend and seed verification: update role-aware navigation/team UI, demo seed data, Playwright coverage, and final regression verification.
