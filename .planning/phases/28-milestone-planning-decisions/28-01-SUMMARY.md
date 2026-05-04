---
phase: 28-milestone-planning-decisions
plan: 01
subsystem: backend
tags:
  - milestone-decisions
  - persistence
  - alembic
  - crud
completed: 2026-04-29
---

# Phase 28 Plan 01 Summary

Add structured milestone decision persistence before the command-view UI builds on it.

## Key Changes

- Added `MilestoneDecisionStatus` with the exact values `proposed`, `approved`, `rejected`, and `superseded`.
- Added the `MilestoneDecision` ORM model and exported it through `app.models`.
- Added the `milestone_decisions` Alembic migration with milestone and optional task foreign keys.
- Added milestone-scoped decision CRUD endpoints and same-project task-link validation.
- Added backend regression coverage for decision status storage, scoped create/update/delete routes, and task-link rejection.

## Verification

- `cd backend && rtk uv run pytest tests/test_milestones.py -q` passed.

## Notes

- The create endpoint accepts an omitted `milestone_id` body field and still enforces the request-path milestone scope.
- Task links are accepted when the task belongs to the same milestone project context and rejected for cross-project links.
