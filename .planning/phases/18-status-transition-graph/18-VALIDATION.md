---
phase: 18
slug: status-transition-graph
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-04-26
---

# Phase 18 - Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest for backend; SvelteKit/Bun check for frontend |
| **Config file** | `backend/pytest.ini` if present; `frontend/package.json` |
| **Quick run command** | `rtk pytest backend/tests/test_status_sets.py backend/tests/test_tasks.py` |
| **Full suite command** | `rtk pytest backend/tests && cd frontend && rtk bun run check` |
| **Estimated runtime** | ~90 seconds |

---

## Sampling Rate

- **After every task commit:** Run `rtk pytest backend/tests/test_status_sets.py backend/tests/test_tasks.py` for backend changes, or `cd frontend && rtk bun run check` for frontend-only changes.
- **After every plan wave:** Run `rtk pytest backend/tests && cd frontend && rtk bun run check`.
- **Before `$gsd-verify-work`:** Full suite must be green or blocked checks must be documented with reason and next action.
- **Max feedback latency:** 120 seconds.

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 18-01-01 | 01 | 1 | TRANS-01 | T-18-01 | Duplicate/self-transition constraints reject invalid graph edges | unit/integration | `rtk pytest backend/tests/test_status_sets.py` | exists | pending |
| 18-01-02 | 01 | 1 | TRANS-02 | T-18-02 | Transition writes require supervisor/admin and same-set endpoints | integration | `rtk pytest backend/tests/test_status_sets.py` | exists | pending |
| 18-02-01 | 02 | 2 | TRANS-03 | T-18-03 | Backend blocks disallowed status moves with structured HTTP 422 | integration | `rtk pytest backend/tests/test_tasks.py` | exists | pending |
| 18-02-02 | 02 | 2 | TRANS-03 | T-18-04 | Empty transition graph preserves free movement | regression | `rtk pytest backend/tests/test_tasks.py` | exists | pending |
| 18-03-01 | 03 | 3 | TRANS-02 | T-18-02 | Project overrides copy matching transition edges and revert removes override rules | integration | `rtk pytest backend/tests/test_status_sets.py` | exists | pending |
| 18-04-01 | 04 | 4 | TRANS-02, TRANS-03 | T-18-03 | Frontend treats backend enforcement as authoritative and handles 422 feedback | static/manual | `cd frontend && rtk bun run check` | exists | pending |

---

## Wave 0 Requirements

- [ ] Add or extend fixtures in `backend/tests/conftest.py` only if current fixtures cannot create status sets, custom statuses, and tasks.
- [ ] Add transition API tests to `backend/tests/test_status_sets.py`.
- [ ] Add transition enforcement tests to `backend/tests/test_tasks.py`.
- [ ] Use existing frontend check infrastructure; do not add a new frontend test dependency just for this phase.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Transition matrix and graph preview are understandable | TRANS-02 | Existing repo appears to rely on Svelte check rather than browser component tests | Open the status manager, create a linear flow, verify matrix cells and preview update without layout overlap |
| Kanban blocked-move UX is clear | TRANS-03 | Drag/drop feedback is hard to validate without browser E2E infrastructure | Configure a restricted graph, drag a task to a blocked column, verify drop is prevented or reverted with a direct toast |
| Empty graph remains backward-compatible | TRANS-03 | Automated backend tests cover API behavior; manual confirms UI does not show restrictions | Remove all transitions and verify drag/drop and edit dropdown allow normal movement |

---

## Validation Sign-Off

- [ ] All tasks have automated verify commands or a documented manual-only reason.
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify.
- [ ] Wave 0 covers transition model/API/enforcement test setup.
- [ ] No watch-mode flags.
- [ ] Feedback latency under 120 seconds.
- [ ] `nyquist_compliant: true` set in frontmatter after plans bind tasks to this strategy.

**Approval:** pending
