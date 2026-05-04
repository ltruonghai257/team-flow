---
phase: 14-sprint-model
reviewed: 2026-04-26T07:25:57Z
fixed: 2026-04-26T07:30:00Z
depth: standard
findings_in_scope: critical_warning
fixed: 2
skipped: 0
iteration: 1
status: all_fixed
---

# Phase 14: Code Review Fix Report

**Reviewed:** 2026-04-26T07:25:57Z
**Fixed:** 2026-04-26T07:30:00Z
**Depth:** standard
**Fix Scope:** critical_warning
**Status:** all_fixed

## Summary

Applied fixes for 2 critical issues in the sprint model migration. All fixes committed atomically.

## Fixes Applied

### CR-01: Unnamed Sprint Foreign Key Cannot Be Reliably Dropped

**File:** `backend/alembic/versions/6ff5de88b5d6_add_sprint_model.py`

**Fix Applied:**
- Changed `op.create_foreign_key(None, ...)` to `op.create_foreign_key('fk_tasks_sprint_id', ...)`
- Changed `op.drop_constraint(None, ...)` to `op.drop_constraint('fk_tasks_sprint_id', ...)`

**Commit:** `fix(14): add named foreign key and enum cleanup to sprint migration`

**Status:** Fixed

---

### CR-02: Downgrade Leaves `sprintstatus` Enum Type Behind

**File:** `backend/alembic/versions/6ff5de88b5d6_add_sprint_model.py`

**Fix Applied:**
- Added `sprintstatus = sa.Enum('planned', 'active', 'closed', name='sprintstatus')` at module level
- Modified upgrade to call `sprintstatus.create(bind, checkfirst=True)` before table creation
- Changed column definition to use `sprintstatus` enum object instead of inline enum
- Modified downgrade to call `sprintstatus.drop(op.get_bind(), checkfirst=True)` after dropping table

**Commit:** `fix(14): add named foreign key and enum cleanup to sprint migration`

**Status:** Fixed

---

## Statistics

- **Findings in scope:** 2 (critical_warning)
- **Fixed:** 2
- **Skipped:** 0
- **Status:** all_fixed

---

_Fixed: 2026-04-26T07:30:00Z_
_Fixer: the agent (gsd-code-fixer)_
_Iteration: 1_
