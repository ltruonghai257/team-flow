# Phase 30: Research — Phase 18 Status-Transition Follow-Up Hardening

**Phase:** 30  
**Date:** 2026-05-06

---

## 1. RBAC Bug: `UserRole.admin` in `_require_status_write_scope`

### Current State

`backend/app/routers/statuses.py:141–148`:

```python
def _require_status_write_scope(current_user: User, sub_team: Optional[SubTeam]) -> None:
    if current_user.role == UserRole.member:
        raise HTTPException(status_code=403, detail="Supervisor or admin access required")
    if current_user.role == UserRole.admin and sub_team is None:
        raise HTTPException(
            status_code=400,
            detail="Select a sub-team before editing default statuses",
        )
```

`UserRole.admin` was removed in Phase 29. `backend/app/models/enums.py` now only has `manager`, `supervisor`, `assistant_manager`, `member`. Any call to this function evaluates `UserRole.admin` → `AttributeError` at runtime.

### Fix Strategy

`backend/app/services/visibility.py` (Phase 29) provides:

```python
LEADERSHIP_ROLES = (UserRole.supervisor, UserRole.assistant_manager)

def is_manager(user: User) -> bool:
    return user.role == UserRole.manager

def is_leader(user: User) -> bool:
    return user.role in LEADERSHIP_ROLES
```

**Correct replacement logic per CONTEXT.md D-01 through D-04:**

```python
def _require_status_write_scope(current_user: User, sub_team: Optional[SubTeam]) -> None:
    if is_member(current_user):
        raise HTTPException(status_code=403, detail="Manager, supervisor, or assistant manager access required")
```

Rationale:
- **D-02**: Drop the sub-team guard for manager entirely — manager has org-wide visibility, the `sub_team is None` check is moot.
- **D-03**: `assistant_manager` gets the same write access as `supervisor` — all non-member leadership roles can write.
- All callers of `_require_status_write_scope` pass `(current_user, sub_team)` — the signature stays the same; the `sub_team` parameter becomes unused but removing it requires touching 8 call sites unnecessarily. Add a `_` comment or just leave unused (minor, at planner's discretion).

### Import Change

`statuses.py` needs `is_member` imported from `app.services.visibility`:

```python
from app.services.visibility import is_member
```

`UserRole` is already imported in `statuses.py` (still needed for other uses); check if the import becomes unused after fix — if so, remove.

---

## 2. Regression Audit Scope

### Backend Code Paths to Audit

| File | Check | Status |
|------|-------|--------|
| `backend/app/routers/statuses.py` | `UserRole.admin` at line 144 | ❌ Confirmed bug |
| `backend/app/routers/tasks.py` | `admin` role references | ✓ Clean — grep returns 0 matches |
| `backend/app/models/enums.py` | `admin` in `UserRole` enum | ✓ Already removed by Phase 29 |
| `backend/app/services/visibility.py` | `admin` references | ✓ Clean — uses `manager` throughout |
| `backend/tests/test_status_sets.py` | `UserRole.admin` in fixtures | ✓ Clean — only `supervisor`/`member` fixtures |
| `backend/tests/test_tasks.py` | `UserRole.admin` in fixtures | ✓ Clean — only `member` fixtures |

**Only one confirmed break**: `statuses.py:144`.

### Frontend Code Paths to Audit

| File | Check | Status |
|------|-------|--------|
| `frontend/src/lib/stores/auth.ts` | `admin` role string | ✓ Clean — uses `manager`/`supervisor`/`assistant_manager`/`member` |
| `frontend/src/lib/components/statuses/StatusTransitionEditor.svelte` | `admin`/`supervisor` role guards | ✓ Clean — no role checks inside (uses `canManage` prop) |
| `frontend/src/lib/components/statuses/StatusSetManager.svelte` | `canManage` prop wire | ✓ Clean — prop-based, no role hardcoding |
| `frontend/src/routes/tasks/+page.svelte` | `isManagerOrLeader` derived store | ✓ Already updated: `$isManagerOrLeader` passed as `canManage` |
| `frontend/src/lib/components/tasks/KanbanBoard.svelte` | `isColumnDropDisabled`, toast path | ✓ Clean — logic is column-slug-based, no role hardcoding |

**Frontend audit conclusion:** No admin-role breaks found. `isManagerOrLeader` store already covers `manager | supervisor | assistant_manager`.

---

## 3. UAT Coverage Analysis

### 4 Pending Phase 18 UAT Scenarios (from `18-UAT.md`)

| # | Scenario | Current State | Action |
|---|----------|---------------|--------|
| 1 | Transition matrix updates immediately | ✓ Covered by `status_transition.spec.ts` — "Transition rules tab shows matrix with draft and save states" | Manual verify pass/fail, update UAT.md |
| 2 | **Kanban drag respects transition rules** | ✗ Not automated — "Kanban view loads and shows status columns" test only checks column visibility | **Add Playwright test** |
| 3 | Status manager route is shareable | ✓ Covered by `status_transition.spec.ts` — "Status manager route is shareable via URL params" | Manual verify pass/fail, update UAT.md |
| 4 | **Blocked moves recover correctly** | ✗ Not automated — toast + board revert path untested | **Add Playwright test** |

### Playwright Test Strategy for UAT #2 and #4

**Infrastructure available:**
- `frontend/tests/helpers/auth.ts` — `loginAs(page)` using supervisor credentials from env vars
- `frontend/tests/status_transition.spec.ts` — existing spec file; new tests should be added here
- No existing helper to create a test status set with transitions via API — will need to use `page.request` (Playwright's `APIRequestContext`) to POST to `/api/status-sets/{id}/transitions` after logging in

**Test approach for UAT #2 (Kanban drag enforcement):**
1. Login as supervisor (who has transition write access)
2. Navigate to `/tasks`, switch to Kanban view
3. Load the effective status set — check if a "linear" transition set exists (todo→review only, not todo→done)
4. If no constrained transition set: use `page.request.post` to configure a linear flow on the current status set
5. Drag a task card from "To Do" column to "Done" (blocked target)
6. Assert the card did not move (remains in "To Do") or that the column shows disabled state

**Constraint:** Playwright drag-and-drop on `svelte-dnd-action` is notoriously difficult to test deterministically. The existing test in `status_transition.spec.ts` skips drag testing entirely. For robustness, use `page.evaluate` to fire the dnd `consider`/`finalize` events, or test via the edit dropdown path instead (route in a separate test).

**Test approach for UAT #4 (Blocked-move recovery):**
1. Login as supervisor
2. Configure a constrained transition set (e.g., only todo→review allowed)  
3. Attempt to move a task to a blocked status via the **edit task modal** status dropdown (more reliable than drag)
4. Submit the change
5. Assert: `toast.error` message appears containing "Cannot move from" OR a generic blocked transition message
6. Assert: Task status in the list reverts to the original value

**Implementation note:** The `page.request` API in Playwright can call backend endpoints directly using the authenticated session (cookies from `loginAs`). This is more stable than UI-based status set setup.

---

## 4. Validation Architecture

### Dimensions Covered

| Dimension | Coverage |
|-----------|----------|
| RBAC correctness | Backend test: `test_transition_replace_validates_auth_pairs_and_empty_payload` extended to include `assistant_manager` write access and `manager` write without sub-team |
| Transition enforcement | Existing `test_tasks.py` tests; no new enforcement logic being changed |
| UAT #2 automation | New Playwright test: Kanban drop target disabled for blocked columns |
| UAT #4 automation | New Playwright test: blocked move via edit modal → toast + revert |
| UAT #1, #3 verification | Manual pass/fail documented in `18-UAT.md` update |
| Regression: no free-movement break | Existing backend tests already cover empty-transition path |

---

## 5. Implementation Order

**Wave 1 — Backend RBAC fix + regression audit + backend test update (no frontend deps):**
- Fix `_require_status_write_scope` in `statuses.py`
- Add `is_member` import from `services.visibility`, remove unused `UserRole` if applicable
- Update `test_transition_replace_validates_auth_pairs_and_empty_payload` to cover `manager` and `assistant_manager` write access
- Run `pytest backend/tests/test_status_sets.py backend/tests/test_tasks.py` — must all pass

**Wave 2 — Playwright UAT automation + UAT doc update:**
- Add UAT #2 and #4 tests to `status_transition.spec.ts`
- Update `18-UAT.md` with pass/fail results for all 4 scenarios
- Run `playwright test status_transition.spec.ts` — new tests must pass or be clearly documented as environment-dependent skips

---

## RESEARCH COMPLETE
