# Phase 29: Scoped Team Visibility & Leadership RBAC - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-29
**Phase:** 29-scoped-team-visibility-leadership-rbac
**Areas discussed:** Role model mapping, leadership scope shape, cross-surface enforcement, team and invite management behavior, migration/reset handling, deferred workflow todo

---

## Gray Area Selection

| Option | Description | Selected |
|--------|-------------|----------|
| Role model mapping | Decide whether `manager` replaces/maps from current `admin`, whether `assistant_manager` becomes a real enum role, and how existing users migrate. | ✓ |
| Leadership scope shape | Decide how supervisors and assistant managers see same-level peer leaders: same parent scope, assigned sub-teams, or another simple rule. | ✓ |
| Cross-surface enforcement | Decide the strictness and UX for team, timeline, milestones, updates, board, schedule, and navigation when data is out of scope. | ✓ |
| Team and invite management behavior | Decide who can assign roles/scopes, whether leaders can create/manage sub-teams, and how invites encode the new scope data. | ✓ |
| Migration defaults and safety | Decide how existing `admin`, `supervisor`, `member`, `sub_team_id`, and `SubTeam.supervisor_id` records should be backfilled without orphaning users or sub-teams. | |
| Fold the pending workflow todo? | Decide whether any part of the status-transition graph todo belongs here. | ✓ |

**User's choice:** Discuss all except migration defaults/versioned migration handling.
**Notes:** User clarified that the application has not been released and migration should stay clean: update `seed_demo.py` and rerun demo seed data rather than preserving old release/version behavior.

---

## Role Model Mapping

| Option | Description | Selected |
|--------|-------------|----------|
| Four-role model | Use `manager`, `supervisor`, `assistant_manager`, and `member`; old `admin` is removed/replaced by `manager`. | ✓ |
| Keep admin alongside manager | Preserve `admin` as a separate technical role while adding user-facing `manager`. | |
| Minimal current-role mapping | Keep current `admin` / `supervisor` / `member` and approximate assistant managers later. | |

**User's choice:** Accepted the recommendation.
**Notes:** `assistant_manager` should be real now so future plans can narrow permissions without another visibility-model rewrite.

---

## Leadership Scope Shape

| Option | Description | Selected |
|--------|-------------|----------|
| Same parent/team scope | Supervisors and assistant managers see their scoped members plus peer leaders in the same parent/team scope. | ✓ |
| Own sub-team only | Supervisors and assistant managers only see their direct sub-team. | |
| Manager-only peer visibility | Only managers see peer leaders across teams. | |

**User's choice:** Accepted the recommendation.
**Notes:** Members remain sub-team-only. Assistant managers share supervisor visibility in Phase 29.

---

## Cross-Surface Enforcement

| Option | Description | Selected |
|--------|-------------|----------|
| Backend source of truth | Apply shared backend visibility filtering everywhere; frontend navigation mirrors it. | ✓ |
| Frontend-first filtering | Hide UI affordances first, backend checks only at obvious privileged endpoints. | |
| Surface-by-surface rules | Let each page keep its own local visibility rules. | |

**User's choice:** Accepted the recommendation.
**Notes:** Hidden records should not leak through disabled UI rows. Navigation follows the Phase 26 pattern: remove inaccessible items entirely.

---

## Team And Invite Management

| Option | Description | Selected |
|--------|-------------|----------|
| Manager assigns leadership | Only managers assign `manager`, `supervisor`, and `assistant_manager`; supervisors/assistant managers manage members only in scope. | ✓ |
| Supervisors assign assistant managers | Supervisors can promote assistant managers inside their scope. | |
| All leaders assign any scoped role | Any leader can assign roles inside their scope. | |

**User's choice:** Accepted the recommendation.
**Notes:** Invite and team-management flows need enough role/scope data for the new model, without adding matrix reporting or many-to-many scope exceptions.

---

## Migration And Demo Reset Handling

| Option | Description | Selected |
|--------|-------------|----------|
| Clean unreleased reset | Remove old role assumptions safely, update current code/schema/seed data, and rerun `seed_demo.py`. | ✓ |
| Version-compatible backfill | Preserve old role compatibility and build production-style migration/backfill paths. | |
| Dual-role bridge | Temporarily support both old and new role names through compatibility layers. | |

**User's choice:** Clean unreleased reset.
**Notes:** User specifically clarified: "No version (previous should not be run, remove safely)." The planner should not invent release migration ceremony.

---

## Deferred Workflow Todo

| Option | Description | Selected |
|--------|-------------|----------|
| Fully defer | Keep the status-transition graph / workflow rules todo out of Phase 29 and leave it for Phase 30/status hardening. | ✓ |
| Fold narrow risk signal | Use only status/workflow state as an input to visibility decisions. | |
| Fold the todo into Phase 29 | Implement workflow-rule graph behavior while changing RBAC. | |

**User's choice:** Accepted the recommendation to fully defer.
**Notes:** Phase 29 is already cross-cutting RBAC work; adding workflow-rule UI would be scope creep.

---

## the agent's Discretion

- Exact helper names, service boundaries, predicate names, and endpoint-by-endpoint 403/404 decisions are left to planning and implementation.
- The planner may decide how much shared visibility-service extraction is needed before touching individual routers.

## Deferred Ideas

- Status-transition graph / YouTrack-style workflow rule management remains deferred to Phase 30/status workflow hardening.
- Matrix management, many-to-many reporting lines, per-user visibility exceptions, external identity sync, and public org directory behavior remain out of scope.
- Narrower assistant-manager management powers may be revisited later if product use shows a real distinction is needed.
