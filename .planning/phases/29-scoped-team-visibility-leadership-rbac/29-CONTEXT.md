# Phase 29: Scoped Team Visibility & Leadership RBAC - Context

**Gathered:** 2026-04-29
**Status:** Ready for planning

<domain>
## Phase Boundary

Enforce TeamFlow's new leadership visibility model across people-aware product surfaces. Members, supervisors, assistant managers, and managers must each see the right people and scoped data across team, timeline, milestones, updates, board, schedule, and navigation. This phase includes cleaning up the unreleased role model and demo seed data. It does not include workflow-rule graph work, route redesign, matrix reporting, external identity sync, or production-version compatibility.

</domain>

<decisions>
## Implementation Decisions

### Role Model
- **D-01:** Use exactly four active roles: `manager`, `supervisor`, `assistant_manager`, and `member`.
- **D-02:** Remove `admin` from the active role model and replace its product meaning with `manager`.
- **D-03:** Because the application has not been released, Phase 29 should not preserve old role compatibility paths or historical version migration behavior.
- **D-04:** Remove obsolete role assumptions safely wherever they appear in backend auth, schemas, frontend auth stores, navigation visibility, tests, and demo data.

### Manager Visibility And Powers
- **D-05:** `manager` is the top role.
- **D-06:** Managers can see all teams, users, leadership groups, and scoped work data across the organization.
- **D-07:** Managers keep the admin-like powers needed for user, team, invite, role, scope, and privileged surface management.

### Supervisor And Assistant Manager Scope
- **D-08:** Supervisors see members and work data inside their assigned scope plus peer leaders in the same parent/team scope.
- **D-09:** Assistant managers use the same visibility model as supervisors in Phase 29.
- **D-10:** Phase 29 may keep assistant-manager management powers equal to or narrower than supervisor powers if implementation needs a distinction, but visibility should not split yet.
- **D-11:** Peer leaders means other `supervisor` and `assistant_manager` users in the same parent/team scope.
- **D-12:** Members remain limited to users and team data inside their own sub-team.

### Team And Invite Management
- **D-13:** Only managers can assign leadership roles: `manager`, `supervisor`, and `assistant_manager`.
- **D-14:** Supervisors and assistant managers may invite or manage `member` users only inside their allowed scope.
- **D-15:** Invite and team-management flows should encode the role and scope data needed by the new model, without building matrix management or many-to-many reporting lines.

### Cross-Surface Enforcement
- **D-16:** Enforce the same visibility rules on the backend query layer for users, teams, projects, tasks, timeline, milestones, updates, weekly board, schedule, knowledge sessions, notifications, and performance data.
- **D-17:** Frontend navigation and page-level UI should reflect the same allowed scope, but backend filtering is the source of truth.
- **D-18:** Out-of-scope records should be filtered out or return 404/403 as appropriate; do not show disabled data rows that reveal hidden team/user existence.
- **D-19:** Navigation items with no allowed access should be removed entirely, continuing the Phase 26 pattern.

### Seed Data And Reset Path
- **D-20:** Phase 29 should update `backend/app/scripts/seed_demo.py` to represent the new role/scope model.
- **D-21:** The intended reset path is to rerun `python -m app.scripts.seed_demo` from `backend/`; previous demo data does not need to be preserved.
- **D-22:** Schema changes may still use Alembic where required, but planning should avoid elaborate production backfills, old-version compatibility branches, or dual-role support.

### Folded Todos
- **D-23:** Do not fold `Status transition graph / workflow rules (YouTrack-style)` into Phase 29. Keep it deferred for Phase 30/status workflow hardening.

### the agent's Discretion
- Exact helper names, service extraction boundaries, predicate naming, 403 vs 404 choice per endpoint, and UI copy are left to planning and implementation.
- The planner may decide whether to introduce a shared backend visibility service first, but cross-surface consistency is mandatory.

</decisions>

<specifics>
## Specific Ideas

- The user explicitly clarified: "No version (previous should not be run, remove safely)." Treat this as permission to remove unreleased compatibility paths and cleanly replace old role assumptions.
- The app is still pre-release, so current demo-state correctness is more important than preserving old demo rows.
- `assistant_manager` exists as a real role now so future phases can narrow powers without changing visibility semantics again.

</specifics>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase Scope And Requirements
- `.planning/ROADMAP.md` — Phase 29 goal, dependency on Phase 28, success criteria, and fixed scope boundary.
- `.planning/REQUIREMENTS.md` — VIS-01 through VIS-07 requirements and v2.3 out-of-scope constraints.
- `.planning/PROJECT.md` — Product context, leadership-role target users, and v2.3 scoped visibility intent.
- `.planning/STATE.md` — Watch-outs, deferred todo context, and current milestone state.
- `.planning/phases/26-navigation-information-architecture/26-CONTEXT.md` — Navigation visibility pattern: hidden items are removed, parent groups with no children are hidden, and Phase 29 supplies deeper scope rules.
- `.planning/phases/27-timeline-gantt-clarity/27-CONTEXT.md` — Timeline must apply the same scoped visibility while preserving milestone/task context.
- `.planning/phases/28-milestone-planning-decisions/28-CONTEXT.md` — Milestone command view and decision/task rollups must obey Phase 29 visibility.

### Current Role And Scope Implementation
- `backend/app/models/enums.py` — Current `UserRole` enum only has `admin`, `supervisor`, and `member`; Phase 29 replaces this active role set.
- `backend/app/models/users.py` — Current `User`, `SubTeam`, and `TeamInvite` role/scope fields.
- `backend/app/utils/auth.py` — Current auth dependencies, supervisor/admin guards, and `get_sub_team` scope injection.
- `frontend/src/lib/stores/auth.ts` — Current frontend user role type and derived role helpers.
- `backend/app/scripts/seed_demo.py` — Demo reset path and seed data that must be updated for the new role/scope model.

### Cross-Surface Enforcement Targets
- `backend/app/routers/users.py` — User list/get/update endpoints and current sub-team filtering.
- `backend/app/routers/sub_teams.py` — Team management and reminder settings scope behavior.
- `backend/app/routers/invites.py` — Invite creation, direct add, and role assignment behavior.
- `backend/app/routers/projects.py` — Project list/create/update/delete scope behavior used by downstream work surfaces.
- `backend/app/routers/tasks.py` — Task filtering and access behavior for assigned work.
- `backend/app/routers/timeline.py` — Timeline project/milestone/task scope filtering.
- `backend/app/routers/milestones.py` — Milestone list/detail/write endpoints that currently need scoped access.
- `backend/app/routers/updates.py` — Standup template and post scope behavior.
- `backend/app/routers/board.py` — Weekly board sub-team scope behavior.
- `backend/app/routers/schedules.py` — Schedule visibility and write behavior.
- `backend/app/routers/knowledge_sessions.py` — Knowledge-session scope behavior and presenter validation.
- `backend/app/services/knowledge_sessions.py` — Existing scoped query helpers that can inform shared visibility logic.
- `backend/app/routers/performance.py` — Privileged performance data scope behavior.
- `frontend/src/routes/+layout.svelte` — Grouped navigation visibility integration point from Phase 26.

### Deferred Todo Reference
- `.planning/todos/pending/2026-04-26-status-transition-graph-workflow.md` — Reviewed and explicitly deferred; do not implement in Phase 29.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `backend/app/utils/auth.py` already centralizes current-user loading, role guards, and sub-team context injection; Phase 29 should evolve or wrap this rather than scattering role checks.
- `backend/app/services/knowledge_sessions.py` already contains scoped query helper patterns that can inspire a shared visibility service.
- `frontend/src/lib/stores/auth.ts` already exposes derived role helpers used by layout/navigation visibility.
- `backend/app/scripts/seed_demo.py` already clears and reseeds all demo tables, making it the right place to model manager/supervisor/assistant-manager/member examples.

### Established Patterns
- Backend API routes use FastAPI dependencies with `get_current_user`, `get_sub_team`, and explicit SQLAlchemy filters.
- Schema changes go through Alembic when the database shape changes, but this phase does not need release-compatible data backfills.
- Frontend role-aware visibility currently comes from the auth store and layout-level navigation filtering.
- Navigation hides disallowed items entirely rather than rendering disabled entries.

### Integration Points
- Role enum changes touch backend models/schemas, frontend user typing, invite forms, auth guards, route predicates, and tests.
- Scope enforcement should be applied consistently in routers that return people, projects, tasks, milestones, timeline data, standup posts, weekly board content, schedule/knowledge-session data, notifications, and performance metrics.
- Demo seed data should include at least one manager, supervisor, assistant manager, and member arrangement so the visibility model is easy to verify after reseeding.

</code_context>

<deferred>
## Deferred Ideas

- Status-transition graph / YouTrack-style workflow rule management remains deferred to Phase 30/status workflow hardening.
- Matrix management, many-to-many reporting lines, per-user visibility exceptions, external identity sync, and public org directory behavior remain out of scope.
- Narrower assistant-manager management powers may be revisited later if product use shows a real distinction is needed.

</deferred>

---

*Phase: 29-scoped-team-visibility-leadership-rbac*
*Context gathered: 2026-04-29*
