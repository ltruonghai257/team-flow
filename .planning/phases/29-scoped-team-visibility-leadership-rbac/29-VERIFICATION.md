---
phase: 29-scoped-team-visibility-leadership-rbac
verified: 2026-04-29T16:55:10Z
status: gaps_found
score: 4/7 must-haves verified
overrides_applied: 0
gaps:
  - truth: "VIS-02/VIS-03: Supervisors and assistant managers can see their full allowed scope plus peer leaders"
    status: partial
    reason: "Shared visibility helpers can return multiple allowed sub-team IDs, but get_sub_team collapses no-header leader requests to one SubTeam. User/project/timeline/updates/board list routes then pass that single selected team back into visible_sub_team_ids, narrowing default leader views instead of showing the full allowed scope."
    artifacts:
      - path: "backend/app/utils/auth.py"
        issue: "get_sub_team calls resolve_visible_sub_team, which returns the first allowed team for non-manager no-header requests."
      - path: "backend/app/services/visibility.py"
        issue: "visible_sub_team_ids supports multiple leader sub-team IDs, but resolve_visible_sub_team returns only allowed_ids[0]."
      - path: "backend/app/routers/users.py"
        issue: "list_users passes sub_team.id when get_sub_team returned a default team, causing helper-level full-scope behavior to be bypassed."
      - path: "backend/app/routers/timeline.py"
        issue: "Timeline has the same single-sub-team narrowing for leader default views."
      - path: "backend/app/routers/updates.py"
        issue: "Updates list uses only sub_team.id from get_sub_team instead of all allowed leader sub-teams."
      - path: "backend/app/services/weekly_board.py"
        issue: "Board payload filters by a single SubTeam from get_sub_team instead of all allowed leader sub-teams."
    missing:
      - "Represent no-header leader scope as all allowed IDs, not a single default SubTeam, or update list surfaces to call visible_sub_team_ids(current_user, requested_sub_team_id=None) directly."
      - "Add tests where one supervisor/assistant manager has more than one allowed sub-team and verify users/projects/timeline/updates/board include all allowed data."
  - truth: "VIS-05: Team, timeline, milestones, updates, board, and schedule views enforce the same visibility rules backend and frontend"
    status: partial
    reason: "Core backend route wiring exists, but the frontend role regression command fails and board/updates default leader views inherit the single-sub-team narrowing gap."
    artifacts:
      - path: "frontend/tests/navigation-groups.spec.ts"
        issue: "Required Playwright regression failed: manager Performance navigation link was not found."
      - path: "frontend/src/lib/navigation/sidebar.ts"
        issue: "Code appears to include manager in Performance roles, so the failing test needs diagnosis rather than accepting the summary PASS claim."
      - path: "backend/app/routers/updates.py"
        issue: "List scoping is dependent on get_sub_team's single-team resolution."
      - path: "backend/app/services/weekly_board.py"
        issue: "Board payload scoping is dependent on get_sub_team's single-team resolution."
    missing:
      - "Fix or diagnose the manager navigation regression so `bun x playwright test tests/navigation-groups.spec.ts tests/team-visibility.spec.ts --workers=1` passes."
      - "Apply full allowed-scope filtering to updates and board leader views."
  - truth: "VIS-07: Existing admin/supervisor/member data and active code paths are migrated or mapped cleanly into manager/supervisor/assistant_manager/member"
    status: failed
    reason: "The enum and PostgreSQL migration exist, but active code and tests still reference the removed admin role. Some paths would now raise AttributeError because UserRole.admin no longer exists."
    artifacts:
      - path: "backend/app/routers/statuses.py"
        issue: "Executable code checks current_user.role == UserRole.admin and still returns 'Supervisor or admin access required'."
      - path: "backend/app/scripts/create_admin.py"
        issue: "Script still creates/promotes UserRole.admin, which no longer exists."
      - path: "backend/app/utils/auth.py"
        issue: "require_admin and require_supervisor_or_admin aliases remain as compatibility names despite the plan requiring admin removal from active code paths."
      - path: "backend/app/auth.py"
        issue: "Compatibility delegate still exports require_admin and require_supervisor_or_admin."
      - path: "backend/tests/test_sprints.py"
        issue: "Still constructs UserRole.admin and fails under the new enum."
      - path: "backend/tests/test_dashboard.py"
        issue: "Still expects an admin_user fixture and fails collection/setup."
    missing:
      - "Replace status-route admin logic and messages with manager/leader semantics."
      - "Rename or remove create_admin.py, or convert it to create/promote a manager."
      - "Remove active admin-named auth aliases or document an accepted override."
      - "Update stale sprint/dashboard tests to manager terminology and expected behavior."
deferred: []
---

# Phase 29: Scoped Team Visibility & Leadership RBAC Verification Report

**Phase Goal:** Enforce the new visibility model so members, supervisors, assistant managers, and managers each see the right people and data  
**Verified:** 2026-04-29T16:55:10Z  
**Status:** gaps_found  
**Re-verification:** No - initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|---|---|---|
| 1 | VIS-01: Members can only see users and team data inside their own sub-team | VERIFIED | `visible_user_filter()` limits members to `User.sub_team_id == current_user.sub_team_id`; projects/tasks/timeline use `scoped_sub_team_filter`; schedule routes are self-owned only. Focused backend suite passed. |
| 2 | VIS-02: Supervisors see scoped members plus peer leaders | FAILED | Helper-level behavior exists, but route-level no-header data flow collapses leaders to one SubTeam via `get_sub_team`/`resolve_visible_sub_team`, then list surfaces re-filter to that one team. Multi-team leader scope is not verified. |
| 3 | VIS-03: Assistant managers follow supervisor peer-visibility model | FAILED | Same root cause as VIS-02; tests cover a single assistant-manager sub-team, not a multi-team allowed scope. |
| 4 | VIS-04: Managers can see all teams, members, and leadership groups | VERIFIED | `is_manager()` returns unrestricted filters; manager user list and selected/all sub-team tests exist; manager backend scoping passes focused tests. |
| 5 | VIS-05: Team, timeline, milestones, updates, board, and schedule views enforce the same rules | FAILED | Backend wiring exists for many surfaces, but board/updates inherit the single-team leader narrowing; frontend required Playwright command failed for manager Performance navigation. |
| 6 | VIS-06: Invite and team-management flows support leadership role/scope data | VERIFIED | `can_assign_role()` is used by invite/direct-add flows; manager-only leadership assignment and scoped leader member management tests pass in `tests/test_visibility.py`/`tests/test_sub_teams.py`. |
| 7 | VIS-07: Existing admin/supervisor/member data is migrated or mapped safely without active admin paths | FAILED | Migration maps PostgreSQL `admin` to `manager`, but active `UserRole.admin` references remain in `statuses.py`, `create_admin.py`, stale tests, and admin-named auth aliases. |

**Score:** 4/7 truths verified

### Required Artifacts

| Artifact | Expected | Status | Details |
|---|---|---|---|
| `backend/app/models/enums.py` | Four active roles | VERIFIED | Defines exactly `manager`, `supervisor`, `assistant_manager`, `member`; no enum `admin`. |
| `backend/app/services/visibility.py` | Shared backend visibility source of truth | PARTIAL | Substantive helper layer exists; route-level data flow misuses it for default leader views by collapsing to one SubTeam. |
| `backend/app/utils/auth.py` | Manager/leader guards and scope dependency | PARTIAL | Manager/leader guards exist, but admin compatibility aliases remain and `get_sub_team` causes full-scope leader narrowing. |
| `backend/app/routers/users.py` | Scoped user list/detail/update | PARTIAL | Uses visibility helpers, but list default leader scope can narrow to one team. |
| `backend/app/routers/invites.py` | Scoped invite/direct-add behavior | VERIFIED | Uses `can_assign_role`, `visible_sub_team_ids`, and `scoped_sub_team_filter`. Plan artifact check flagged missing literal `assistant_manager`, but behavior delegates through enum/helper. |
| `backend/app/routers/sub_teams.py` | Scoped team management | VERIFIED | Manager-only mutation and scoped leader listing are wired through visibility helpers. |
| `backend/app/routers/timeline.py` | Scoped timeline payloads | PARTIAL | Uses helper filters, but default leader scope can narrow to one team. |
| `backend/app/routers/milestones.py` | Scoped milestone access | VERIFIED | Uses visible sub-team/project filters for list/detail/write paths. |
| `backend/app/routers/tasks.py` | Scoped task access | VERIFIED | Direct-ID and list paths use visible project/assignee checks. |
| `backend/app/routers/updates.py` | Scoped updates | PARTIAL | Uses `get_sub_team` single-team filtering; does not directly apply all allowed leader IDs. |
| `backend/app/routers/board.py` / `backend/app/services/weekly_board.py` | Scoped weekly board | PARTIAL | Board payload filters by one SubTeam object rather than all allowed leader IDs. |
| `backend/app/routers/schedules.py` | Schedule visibility | VERIFIED | Personal ownership only; no other-user schedule leakage found. |
| `frontend/src/lib/stores/auth.ts` | Frontend role helpers | VERIFIED | Role union and manager/leader stores use new roles. |
| `frontend/src/lib/navigation/sidebar.ts` | Role-aware navigation | PARTIAL | Code includes manager/leader roles, but required Playwright manager navigation test failed. |
| `frontend/src/routes/team/+page.svelte` | Role-aware team UI | VERIFIED | Manager-only leadership options and leader member-management affordances are present; team UI Playwright tests passed. |
| `backend/app/scripts/seed_demo.py` | Demo data for all four roles | VERIFIED | Seeds manager, supervisors, assistant manager, and members across two sub-teams. |

### Key Link Verification

| From | To | Via | Status | Details |
|---|---|---|---|---|
| `backend/app/utils/auth.py` | `backend/app/services/visibility.py` | guard dependencies call shared helpers | VERIFIED | `verify.key-links` passed. |
| `backend/app/routers/invites.py` | `backend/app/services/visibility.py` | role assignment and invite scope checks | VERIFIED | `can_assign_role`, `visible_sub_team_ids`, `scoped_sub_team_filter` imported and used. |
| `backend/app/routers/users.py` | `backend/app/services/visibility.py` | visible user lookup/list/update | VERIFIED | Helper imports and calls found. |
| `backend/app/routers/projects.py` | `backend/app/services/visibility.py` | visible project/sub-team filters | VERIFIED | `verify.key-links` passed. |
| `backend/app/routers/timeline.py` | `backend/app/services/visibility.py` | visible project filtering | VERIFIED | Helper imports and calls found. |
| `backend/app/services/weekly_board.py` | `backend/app/services/visibility.py` | board payload scope resolution | FAILED | Plan key-link passed only by pattern, but `weekly_board.py` does not import visibility helpers and receives a single `SubTeam` from the router. |
| `frontend/src/routes/+layout.svelte` | `frontend/src/lib/navigation/sidebar.ts` | `filterNavigationGroups` | VERIFIED | `verify.key-links` passed. |
| `frontend/src/routes/team/+page.svelte` | `frontend/src/lib/stores/auth.ts` | role-aware management controls | VERIFIED | Imports `isManager` / `isManagerOrLeader`. |
| `backend/app/scripts/seed_demo.py` | `backend/app/models/enums.py` | seeded `UserRole` values | VERIFIED | Uses `UserRole.assistant_manager` and other active roles. |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
|---|---|---|---|---|
| `backend/app/services/visibility.py` | allowed sub-team IDs | DB query on `SubTeam.supervisor_id` plus `user.sub_team_id` | Yes | FLOWING |
| `backend/app/utils/auth.py` | `sub_team` dependency | `resolve_visible_sub_team()` | Partially | HOLLOW for no-header leaders: full allowed IDs are collapsed to first allowed SubTeam. |
| `backend/app/routers/users.py` | user list | `visible_users_query(... requested_sub_team_id=sub_team.id ...)` | Partially | HOLLOW for multi-scope leader default views. |
| `backend/app/routers/timeline.py` | project timeline list | `visible_sub_team_ids(... requested_sub_team_id=sub_team.id ...)` | Partially | HOLLOW for multi-scope leader default views. |
| `backend/app/routers/updates.py` | standup post list | `StandupPost.sub_team_id == sub_team.id` | Partially | STATIC single-team filter for leaders, not all allowed IDs. |
| `backend/app/services/weekly_board.py` | weekly board posts/summaries | `WeeklyPost.sub_team_id == sub_team.id` | Partially | STATIC single-team filter for leaders, not all allowed IDs. |
| `frontend/src/routes/team/+page.svelte` | users, invites, sub-teams | API calls from `$lib/apis` | Yes | FLOWING; tests use mocked API responses. |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|---|---|---|---|
| Focused Phase 29 backend RBAC regressions | `cd backend && rtk uv run pytest tests/test_visibility.py tests/test_board.py tests/test_sub_teams.py -q` | `31 passed, 1 warning` | PASS |
| Adjacent admin cleanup regression check | `cd backend && rtk uv run pytest tests/test_sprints.py tests/test_dashboard.py -q` | `8 failed, 1 error`; failures include `UserRole.admin` AttributeError and missing `admin_user` fixture | FAIL |
| Frontend type check | `cd frontend && bun run check` | `0 errors, 9 warnings` | PASS |
| Required Phase 29 Playwright regressions | `cd frontend && bun x playwright test tests/navigation-groups.spec.ts tests/team-visibility.spec.ts --workers=1` | `1 failed, 14 passed`; manager Performance link not visible | FAIL |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|---|---|---|---|---|
| VIS-01 | 29-01, 29-03, 29-04 | Members can only see own sub-team users/team data | SATISFIED | Member helper tests, route filters, personal schedule ownership. |
| VIS-02 | 29-01, 29-02, 29-03 | Supervisors see allowed scoped members plus peer leaders | BLOCKED | Helper tests pass for one sub-team, but no-header route data flow narrows multi-scope leaders to one team. |
| VIS-03 | 29-01, 29-02, 29-03 | Assistant managers follow supervisor visibility | BLOCKED | Same data-flow gap as VIS-02. |
| VIS-04 | 29-01, 29-02, 29-03, 29-04 | Managers see all teams/users | SATISFIED | Backend manager filters return unrestricted data; manager tests pass. Frontend manager nav has separate VIS-05/UI regression failure. |
| VIS-05 | 29-03, 29-04 | Required views enforce same visibility rules | BLOCKED | Updates/board default leader views narrow incorrectly; Playwright manager navigation regression fails. |
| VIS-06 | 29-02, 29-04 | Invite/team flows assign or represent leadership scopes | SATISFIED | Manager-only leadership assignment and scoped leader member management are implemented and tested. |
| VIS-07 | 29-01, 29-02, 29-04 | Existing role data safely migrated/mapped | BLOCKED | Migration exists, but active admin references remain in route/script/test/auth alias paths. |

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|---|---:|---|---|---|
| `backend/app/routers/statuses.py` | 144 | `UserRole.admin` | BLOCKER | Active route can crash now that enum has no admin member. |
| `backend/app/scripts/create_admin.py` | 38, 47 | `UserRole.admin` | BLOCKER | Admin creation/reset path is broken and contradicts VIS-07. |
| `backend/app/utils/auth.py` | 104-105 | admin-named compatibility aliases | WARNING | Keeps old admin API surface alive despite plan requiring no active admin path. |
| `backend/app/auth.py` | 10-11 | exports admin-named aliases | WARNING | Extends old naming through compatibility delegate. |
| `backend/tests/test_sprints.py` | multiple | stale `UserRole.admin` tests | BLOCKER | Broader backend suite fails under the new enum. |
| `backend/tests/test_dashboard.py` | 4 | missing `admin_user` fixture | BLOCKER | Broader backend suite no longer collects/runs cleanly. |
| `frontend/tests/mobile/status-management-roles.spec.ts` | multiple | stale admin role fixtures | WARNING | Frontend mobile role tests still encode old role model. |

### Human Verification Required

None. Automated evidence is sufficient to block the phase.

### Gaps Summary

The Phase 29 implementation has a substantive backend visibility service, many routes are wired to it, invite/team role assignment mostly works, and the new enum/migration foundation exists. The phase goal is still not achieved because three must-have truths fail:

1. Multi-scope leaders are not actually shown their full allowed scope by default on several list surfaces.
2. VIS-05 frontend/backend consistency is not clean; the required manager navigation Playwright test currently fails.
3. Admin cleanup is incomplete in active route/script/test surfaces, including executable `UserRole.admin` references that now break.

Structured gaps are included in frontmatter for `$gsd-plan-phase --gaps`.

---

_Verified: 2026-04-29T16:55:10Z_  
_Verifier: the agent (gsd-verifier)_
