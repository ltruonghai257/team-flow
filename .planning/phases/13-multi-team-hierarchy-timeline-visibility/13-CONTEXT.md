# Phase 13: Multi-Team Hierarchy + Timeline Visibility - Context

**Gathered:** 2026-04-24
**Status:** Ready for planning

<domain>
## Phase Boundary

Introduce a `SubTeam` model so the app is organized into sub-teams. Every user, project, and task is scoped to a sub-team. The timeline shows only what each role is permitted to see: members see only projects where they have at least one assigned task; supervisors see all projects in their sub-team; admins see all projects across all sub-teams and can switch between them.

This phase does not introduce sprint behavior, custom Kanban statuses, KPI dashboard changes, or reminder logic. Those belong to later Milestone 2 phases.

</domain>

<decisions>
## Implementation Decisions

### Default Sub-Team Migration
- **D-01:** All existing users and projects migrate into a single default sub-team named "Default Team" with no supervisor pre-assigned.
- **D-02:** The existing admin remains an admin and is also added to the default sub-team as a member.
- **D-03:** After migration, the admin must manually create additional sub-teams, assign supervisors, and move users/projects before the hierarchy is useful.
- **D-04:** A supervisor column on the sub-team is nullable during migration; the admin assigns supervisors via the UI afterward.

### Sub-Team Management UI
- **D-05:** Extend the existing `/team` page to include sub-team management, not a new dedicated settings page.
- **D-06:** Add a "Sub-Teams" tab or section to `/team` where the admin can create, rename, and reassign supervisors to sub-teams.
- **D-07:** Supervisors see their own sub-team's member list on `/team`; admins see all sub-teams with a switcher or tabs.
- **D-08:** Sub-team creation and supervisor reassignment happen inline on the same page where members and invites are managed.

### Global Sub-Team Context Switcher
- **D-09:** Introduce a global sub-team context switcher (sidebar or top nav) that filters the entire app for the admin.
- **D-10:** When the admin selects a sub-team, all pages (dashboard, timeline, performance, projects) scope to that sub-team automatically.
- **D-11:** Supervisors have no switcher — their entire session is implicitly scoped to their assigned sub-team.
- **D-12:** Members have no switcher — their data is implicitly scoped by their sub-team membership.

### Project Creation Permissions
- **D-13:** Supervisors can create projects only for their own sub-team; no sub-team selector appears on the project creation form.
- **D-14:** Admins create projects for whichever sub-team is currently active in their global switcher; no per-form dropdown.
- **D-15:** Backend enforces that a supervisor's `POST /api/projects` is rejected if they try to create a project outside their sub-team.

### Invite Flow with Sub-Teams
- **D-16:** New invites are scoped to the inviter's currently active sub-team (supervisor: their own; admin: the one selected in the global switcher).
- **D-17:** No sub-team selector on the invite form; the global context or implicit supervisor scope determines the target sub-team.
- **D-18:** When a user accepts an invite, they are automatically assigned to the sub-team attached to that invite.

### API Scoping Enforcement
- **D-19:** Every data-fetching endpoint (tasks, projects, milestones, timeline, performance, dashboard, users) must filter by the requesting user's sub-team server-side.
- **D-20:** Admin endpoints bypass sub-team filtering and instead respect the global switcher context (passed as a header or query param, or stored in session).
- **D-21:** Direct API access attempts to cross-team data must return 403, not 404, to avoid leaking existence.

### Timeline Visibility
- **D-22:** Members see only projects on `/timeline` where they have at least one assigned task (server-side filter).
- **D-23:** Supervisors see all projects belonging to their sub-team on `/timeline`.
- **D-24:** Admins see all projects from all sub-teams; a sub-team filter (driven by the global switcher) can narrow the view.

### Claude's Discretion
- Exact placement and styling of the global sub-team switcher in the nav/sidebar.
- Whether the admin's global switcher state is stored in localStorage, URL param, or backend session.
- Exact migration implementation for `sub_team_id` columns and the default sub-team creation.
- How the timeline handles a member with zero assigned tasks (empty state copy and design).

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Roadmap and Requirements
- `.planning/ROADMAP.md` — Phase 13 goal, success criteria, sequencing, and dependencies.
- `.planning/REQUIREMENTS.md` — `TEAM-01` through `TEAM-05` and `VIS-01` through `VIS-03` acceptance criteria.
- `.planning/PROJECT.md` — Milestone 2 product framing, active requirements, and key decisions.
- `.planning/STATE.md` — Architecture decisions: SubTeam not Organization, dual-write strategy, unscoped query watch-out list.

### Existing Models and Auth
- `backend/app/models.py` — User, Project, Task, Milestone, TeamInvite models and relationships (no SubTeam yet).
- `backend/app/auth.py` — `get_current_user`, `require_supervisor`, `require_admin`, `require_supervisor_or_admin` dependencies.
- `backend/app/schemas.py` — Pydantic schemas for User, Project, Task, Milestone, and invite flows.

### Unscoped Routers (must gain sub_team_id predicates)
- `backend/app/routers/timeline.py` — Returns all projects with milestones and tasks; currently unscoped.
- `backend/app/routers/dashboard.py` — Aggregate counts across all tasks/users; currently unscoped.
- `backend/app/routers/performance.py` — Team metrics and user detail queries; currently unscoped.
- `backend/app/routers/users.py` — Lists all active users; currently unscoped.
- `backend/app/routers/projects.py` — Lists all projects; currently unscoped.
- `backend/app/routers/tasks.py` — Task CRUD and AI parsing; scope must be added.
- `backend/app/routers/invites.py` — Invite create/accept/list; needs sub-team attachment.

### Frontend Pages to Modify
- `frontend/src/routes/team/+page.svelte` — Existing team management page; extend with sub-team tabs/sections.
- `frontend/src/routes/timeline/+page.svelte` — Timeline view; scope by role.
- `frontend/src/routes/performance/+page.svelte` — Performance dashboard; scope by role.
- `frontend/src/routes/+page.svelte` — Dashboard; scope by role.
- `frontend/src/routes/+layout.svelte` — Main layout; global sub-team switcher lives here.

### Migration
- `backend/alembic/` — Alembic migration directory for adding `sub_team_id` columns and default sub-team creation.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `backend/app/auth.py`: existing role-based dependency functions can be extended to also inject sub-team context.
- `frontend/src/routes/team/+page.svelte`: already has member list, invite sending, and role management; sub-team management can extend this page.
- `frontend/src/routes/timeline/+page.svelte`: already fetches and renders project/milestone/task tree; only the data fetch endpoint needs scoping.
- `backend/app/routers/invites.py`: invite create/accept flow already exists; needs `sub_team_id` attachment on create and user assignment on accept.

### Established Patterns
- FastAPI dependency injection for auth (`Depends(get_current_user)`); sub-team scoping should be added as a dependency or filter helper.
- All list endpoints currently use `select(Model)` without `.where()` filtering; every one needs a sub-team predicate.
- JWT cookie auth stores only `user_id`; sub-team membership is resolved from the database on each request (no token change needed).
- Frontend API client (`frontend/src/lib/api.ts`) already sends cookies automatically; no auth mechanism change needed.

### Integration Points
- New `SubTeam` model must have FK relationships to `User` (supervisor_id, nullable), `Project` (sub_team_id), and `User` (members via sub_team_id).
- The global sub-team switcher must communicate the admin's selected sub-team to the backend — via a custom header (e.g., `X-SubTeam-ID`) or query param on relevant endpoints.
- All existing pages that fetch scoped data must be updated to pass the switcher value (for admin) or rely on implicit backend scoping (for supervisor/member).
- Milestones belong to projects, which belong to sub-teams — milestone scoping is inherited through the project FK.

</code_context>

<specifics>
## Specific Ideas

- The global sub-team switcher for admins should feel like a workspace/workspace selector — prominent but not disruptive.
- Supervisor experience should remain unchanged except that they no longer see cross-team data; the UI should not gain new controls.
- Member timeline should feel personal — "Your projects" rather than "All projects".
- Admin should be able to quickly switch sub-teams and see the dashboard, timeline, and performance update instantly.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within Phase 13 scope.

</deferred>

---

*Phase: 13-multi-team-hierarchy-timeline-visibility*
*Context gathered: 2026-04-24*
