# Phase 13: Multi-Team Hierarchy + Timeline Visibility - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-24
**Phase:** 13-multi-team-hierarchy-timeline-visibility
**Areas discussed:** Default Sub-Team Migration, Sub-Team Management UI, Global Sub-Team Context Switcher, Project Creation Permissions, Invite Flow with Sub-Teams, API Scoping Enforcement, Timeline Visibility

---

## Default Sub-Team Migration

| Option | Description | Selected |
|--------|-------------|----------|
| A — Admin becomes default supervisor | Existing admin assigned as supervisor of default sub-team; all users/projects collapse into it | |
| B — Existing supervisors each get a sub-team | Each supervisor gets their own sub-team; members/projects follow | |
| C — One flat default, no supervisor | All users and projects go into "Default Team"; admin must manually create sub-teams and assign supervisors afterward | ✓ |

**User's choice:** C
**Notes:** Cleanest migration. Admin does manual setup post-migration. Existing supervisors remain as users in the default sub-team until reassigned.

---

## Sub-Team Management UI

| Option | Description | Selected |
|--------|-------------|----------|
| A — Extend existing `/team` page | Add sub-team tabs/sections to the existing team management page | ✓ |
| B — New `/settings/teams` page | Dedicated page for sub-team CRUD; separates from member/invite management | |
| C — Inline in admin dashboard | Global switcher + modal/drawer for sub-team creation from the dashboard | |

**User's choice:** A
**Notes:** Supervisor sees their sub-team's members; admin sees all sub-teams with a switcher/tabs. Keeps all team management in one place.

---

## Global Sub-Team Context Switcher

| Option | Description | Selected |
|--------|-------------|----------|
| A — Global switcher in layout | Admin has a persistent sub-team selector (sidebar or top nav) that scopes all pages | ✓ (implied by B in Project Creation) |
| B — Per-form dropdowns | Admin selects sub-team on each form (invite, project create, etc.) | |

**User's choice:** A (implied — selected B for Project Creation, which requires a global switcher)
**Notes:** Admin's selected sub-team drives project creation, invites, and data views. Supervisor and members have no switcher — implicit scope.

---

## Project Creation Permissions

| Option | Description | Selected |
|--------|-------------|----------|
| A — Admin creates for any sub-team via form dropdown | Admin sees a sub-team selector on the project creation form | |
| B — Admin restricted to global switcher context | Admin's project creation is scoped to their currently active sub-team; no per-form dropdown | ✓ |
| C — Admin sees all projects, form has sub-team dropdown | Most flexible; projects page shows all sub-teams, form has dropdown | |

**User's choice:** B
**Notes:** Consistent with global switcher approach. Supervisor implicitly scoped to their own sub-team. Backend rejects cross-team project creation.

---

## Invite Flow with Sub-Teams

| Option | Description | Selected |
|--------|-------------|----------|
| A — Invite scoped to inviter's active sub-team | Supervisor invites go to their sub-team; admin invites go to their global-switcher sub-team | ✓ |
| B — Explicit sub-team selector on invite form | Admin can override the global switcher for this invite only | |
| C — Unscoped invite, user picks on acceptance | User selects sub-team when accepting the invite | |

**User's choice:** A
**Notes:** Consistent with global switcher. No extra UI on the invite form. New user joins the sub-team attached to the invite automatically.

---

## API Scoping Enforcement

This area was not presented as an explicit question but is a hard requirement from REQUIREMENTS.md (`TEAM-04`). It is recorded here as a locked constraint, not a user-selected option.

- All data-fetching endpoints must filter by the requesting user's sub-team.
- Admin endpoints use the global switcher context instead of their own sub-team membership.
- Cross-team access attempts return 403.

---

## Timeline Visibility

This area was not presented as an explicit question but is a hard requirement from REQUIREMENTS.md (`VIS-01`, `VIS-02`, `VIS-03`). It is recorded here as a locked constraint, not a user-selected option.

- Members: only projects with at least one assigned task.
- Supervisors: all projects in their sub-team.
- Admins: all projects; filterable by global switcher.

---

## Claude's Discretion

The following implementation details are left to the planner/implementer:
- Exact placement and styling of the global sub-team switcher.
- Whether admin switcher state is stored in localStorage, URL param, or backend session.
- Exact Alembic migration strategy for adding columns and creating the default sub-team.
- Empty state design for members with zero assigned tasks on the timeline.

---

## Deferred Ideas

None — discussion stayed within Phase 13 scope.

