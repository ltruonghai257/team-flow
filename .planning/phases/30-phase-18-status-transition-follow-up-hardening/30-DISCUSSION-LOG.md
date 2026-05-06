# Phase 30: Phase 18 Status-Transition Follow-Up Hardening - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-05-06
**Phase:** 30-phase-18-status-transition-follow-up-hardening
**Areas discussed:** RBAC Fix + Scoping Rules, UAT Verification Strategy, Regression Scope

---

## RBAC Fix + Scoping Rules

| Option | Description | Selected |
|--------|-------------|----------|
| Require sub-team context (same as old admin rule) | Manager must have sub-team selected to edit default statuses | |
| Free access — manager can edit any sub-team's statuses | Manager has org-wide visibility; sub-team check is unnecessary friction | ✓ |

**User's choice:** Free access — manager can edit any sub-team's statuses

---

| Option | Description | Selected |
|--------|-------------|----------|
| Same write access as supervisor | assistant_manager can create and edit transition rules inside scope | ✓ |
| Read-only for assistant_manager | Only manager and supervisor can write transition rules | |

**User's choice:** Same write access as supervisor

**Notes:** Consistent with Phase 29 D-09 — assistant managers follow the same model as supervisors.

---

## UAT Verification Strategy

| Option | Description | Selected |
|--------|-------------|----------|
| Manual test run — document pass/fail in UAT.md | Run scenarios in browser, record results. No new automated tests. | |
| Add Playwright E2E tests for all 4 | Automate all four scenarios for full regression coverage | |
| Playwright for 2 + manual for 2 | Automate behavioral ones (Kanban drag + blocked-move recovery); manual for matrix visual state + URL shareability | ✓ |

**User's choice:** Playwright for 2 + manual for 2

---

| Option | Description | Selected |
|--------|-------------|----------|
| Fix inline — Phase 30 owns all bugs found during verification | If UAT uncovers broken behavior, Phase 30 fixes it | ✓ |
| Log and defer — Phase 30 only verifies, fixes go to new phase | Verification phase only; bugs become new issues | |

**User's choice:** Fix inline

---

## Regression Scope

| Option | Description | Selected |
|--------|-------------|----------|
| Targeted — fix known UserRole.admin bug + run existing tests green | Fix confirmed RBAC break only; don't audit further unless tests reveal more | |
| Broader — audit all status/transition code paths that touch roles or sub-team scope | Systematically check statuses.py, tasks.py, test fixtures, frontend role guards | ✓ |

**User's choice:** Broader audit

---

## Claude's Discretion

- Exact Playwright test structure and fixture strategy
- Exact wording for updated `_require_status_write_scope` error message
- Whether to consolidate fragile test fixtures discovered during audit

## Deferred Ideas

None.
