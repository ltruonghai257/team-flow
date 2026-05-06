# Phase 30: Phase 18 Status-Transition Follow-Up Hardening - Context

**Gathered:** 2026-05-06
**Status:** Ready for planning

<domain>
## Phase Boundary

Harden and verify the Phase 18 status-transition workflow after Phase 29's role model refactor. Scope covers: fixing the confirmed `UserRole.admin` RBAC break in status-set write scope, broadening the regression audit to all status/transition code paths that touch roles or sub-team scope, running the 4 pending Phase 18 UAT scenarios (with Playwright automation for the two behavioral ones), and fixing any bugs found inline.

This phase does not add new transition features, redesign the transition editor, or change transition enforcement semantics — only hardens what Phase 18 shipped.

</domain>

<decisions>
## Implementation Decisions

### RBAC Fix — Status-Set Write Scope
- **D-01:** Replace `UserRole.admin` with `UserRole.manager` in `_require_status_write_scope` in `backend/app/routers/statuses.py:144`. `UserRole.admin` no longer exists after Phase 29; this is an `AttributeError` at runtime.
- **D-02:** Remove the sub-team context requirement for `manager`. Under the new model, manager has org-wide visibility and can edit any sub-team's default statuses freely — the old admin sub-team guard is unnecessary friction.
- **D-03:** `assistant_manager` gets the same write access as `supervisor` for transition rules — consistent with Phase 29 D-09 (assistant managers follow the same visibility model as supervisors). The write scope guard should allow `manager`, `supervisor`, and `assistant_manager`; only `member` is blocked.
- **D-04:** Update the error message in `_require_status_write_scope` from "Supervisor or admin access required" to reflect the new role set.

### Regression Audit Scope
- **D-05:** Perform a broader audit — not just the confirmed `UserRole.admin` break. Systematically check `statuses.py`, `tasks.py` transition enforcement path, test fixtures in `test_status_sets.py` and `test_tasks.py`, and any frontend role guards touching the transition editor for Phase 29 side effects.
- **D-06:** If the audit finds other Phase 29 role reference breaks (e.g., hardcoded `admin` in test fixtures or frontend visibility guards), fix them inline in Phase 30.

### UAT Verification
- **D-07:** Automate the two behavioral UAT scenarios using Playwright: Kanban drag enforcement (only allowed columns accept drop) and blocked-move recovery (board reverts + toast appears). These are regression-risky and should not remain manual-only.
- **D-08:** Keep matrix visual draft state and status manager URL shareability as manual verification scenarios. Document pass/fail results in the updated `18-UAT.md`.
- **D-09:** If any UAT scenario reveals a broken behavior, Phase 30 fixes it inline. This phase owns all bugs found during verification — the transition feature should be complete before the milestone closes.

### Claude's Discretion
- Exact Playwright test structure and fixture strategy for the two automated scenarios.
- Exact wording for the updated `_require_status_write_scope` error message.
- Whether to consolidate any fragile test fixtures discovered during the audit or leave them as found (provided tests pass).

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase 18 Implementation (source of truth for what was built)
- `.planning/phases/18-status-transition-graph/18-CONTEXT.md` — All Phase 18 enforcement decisions (D-01 through D-23): strict allowlist, 422 structured errors, free movement without rules, archived transitions dormant, project overrides as independent snapshots.
- `.planning/phases/18-status-transition-graph/18-SUMMARY.md` — What was built across all 4 plans: model, API, UI, enforcement.
- `.planning/phases/18-status-transition-graph/18-UAT.md` — 4 pending UAT scenarios to verify (or re-verify after fixes).

### Phase 29 Role Model Changes
- `.planning/phases/29-scoped-team-visibility-leadership-rbac/29-CONTEXT.md` — New role model decisions: manager replaces admin, four active roles, assistant_manager follows supervisor visibility (D-09), sub-team context enforcement.

### Status and Transition Code
- `backend/app/routers/statuses.py` — `_require_status_write_scope` (line 141–148) is the primary fix target. Contains all transition CRUD endpoints.
- `backend/app/routers/tasks.py` — `_enforce_status_transition` and `_require_status_write_scope` call sites; also sub-team resolution path.
- `backend/app/models/enums.py` — Current `UserRole` enum: `manager`, `supervisor`, `assistant_manager`, `member`. No `admin`.
- `backend/app/services/visibility.py` — New Phase 29 visibility service; `is_manager`, `is_leader`, `LEADERSHIP_ROLES` helpers to use instead of direct role comparisons.
- `backend/tests/test_status_sets.py` — Transition API and enforcement tests; may contain hardcoded `admin` fixture references.
- `backend/tests/test_tasks.py` — Task update enforcement tests.

### Frontend Transition Components
- `frontend/src/lib/components/statuses/StatusTransitionEditor.svelte` — Matrix editor.
- `frontend/src/lib/components/statuses/StatusTransitionPreview.svelte` — Read-only graph preview.
- `frontend/src/lib/components/tasks/KanbanBoard.svelte` — Drag-drop enforcement and client-side blocked-move handling.
- `frontend/src/routes/tasks/+page.svelte` — Transition-aware task board; status dropdown filtering and blocked-transition toast handling.

### Roadmap and Milestone
- `.planning/ROADMAP.md` — Phase 30 goal and dependency on Phase 29.
- `.planning/PROJECT.md` — Product context and current milestone intent.

</canonical_refs>

<code_context>
## Existing Code Insights

### Confirmed Bug
- `backend/app/routers/statuses.py:144` — `UserRole.admin` reference in `_require_status_write_scope`. `UserRole.admin` was removed by Phase 29. This will raise `AttributeError` at runtime when the condition is evaluated.

### Reusable Assets
- `backend/app/services/visibility.py` — `is_manager`, `is_leader`, `is_member`, `LEADERSHIP_ROLES` helpers introduced in Phase 29. The RBAC fix should use `is_manager` / `is_leader` rather than direct role comparisons to stay consistent with the rest of Phase 29's code.
- `backend/tests/conftest.py` — Async FastAPI test harness introduced in Phase 18; fixtures create status sets, custom statuses, and tasks for transition testing.
- `frontend/tests/` — Playwright test infrastructure already exists in the repo; Phase 30 Playwright tests should follow the existing test file structure.

### Established Patterns
- Status-set writes are scoped through `_require_status_write_scope`; all transition CRUD endpoints go through this guard.
- Backend 422 structured errors for blocked transitions use `BlockedStatusTransitionDetail` schema.
- Frontend uses `svelte-sonner` toasts for blocked-move feedback and `lucide-svelte` icons for column hints.
- Phase 29 used `is_manager()` / `is_leader()` / `is_member()` helpers from `services/visibility.py` consistently across all updated routers.

### Integration Points
- The RBAC fix in `statuses.py` needs to stay aligned with how other routers (users, invites, teams) resolved the same admin→manager migration in Phase 29.
- Playwright tests for Kanban enforcement need a test status set with transition rules — check if the existing Playwright helpers in `frontend/tests/helpers/` can create one, or whether a seed fixture is needed.

</code_context>

<specifics>
## Specific Ideas

- Use `is_leader(current_user)` from `services/visibility.py` to express "supervisor or assistant_manager" in the updated `_require_status_write_scope`, matching the Phase 29 pattern used in other routers.
- The sub-team guard for manager should be dropped entirely (not just relaxed) — manager's org-wide visibility makes the "select a sub-team first" check meaningless.
- The two Playwright scenarios to automate: (1) configure a linear transition graph, drag a task to a blocked column — column should reject; (2) attempt a blocked move via the edit dropdown, verify the board reverts and a toast appears.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 30-phase-18-status-transition-follow-up-hardening*
*Context gathered: 2026-05-06*
