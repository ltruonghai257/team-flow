---
phase: "14"
slug: "sprint-model"
status: "validation-planned"
nyquist_compliant: true
wave_0_complete: false
created: "2026-04-26"
---

# Phase 14: Sprint Model - Validation

**Validates:** 2026-04-26
**Status:** Map Complete

## Validation Map

| Requirement ID | Behavior to Verify | Test Type | Automated Command | File Path | Status |
|----------------|--------------------|-----------|-------------------|-----------|--------|
| SPRINT-01 | CRUD for Sprints (name, start_date, end_date, milestone_id, status); Supervisor/Admin authorization; Sprint list view | Unit (Backend) | `pytest backend/tests/test_sprints.py -v -k "crud"` | `backend/tests/test_sprints.py` | planned |
| SPRINT-01 | Closing a sprint moves incomplete tasks to backlog or next sprint via bulk update | Unit (Backend) | `pytest backend/tests/test_sprints.py -v -k "close"` | `backend/tests/test_sprints.py` | planned |
| SPRINT-02 | Milestone required to have `project_id`; API enforces project selection | Unit (Backend) | `pytest backend/tests/test_projects.py -v -k "milestone"` | `backend/tests/test_projects.py` | planned |
| SPRINT-03 | Task create/edit accepts and persists `sprint_id` | Unit (Backend) | `pytest backend/tests/test_tasks.py -v -k "sprint"` | `backend/tests/test_tasks.py` | planned |
| SPRINT-04 | Sprint board endpoint filters tasks by selected `sprint_id`; unassigned tasks queryable | Unit (Backend) | `pytest backend/tests/test_tasks.py -v -k "filter_sprint"` | `backend/tests/test_tasks.py` | planned |
| SPRINT-03, 04| Frontend Kanban Board filters tasks by Sprint and handles drag-to-backlog nullifying `sprint_id` | Playwright E2E | `npx playwright test --grep "Sprint Board"` | `frontend/tests/sprint_board.spec.ts` | planned |

## Nyquist Gap Analysis
*To be evaluated post-implementation to ensure requirements are met without missing coverage.*

### Coverage Criteria
1. **SPRINT-01:**
   - Must verify that `Sprint` cannot be created by a member (403 Forbidden).
   - Must verify sprint close logic handles partial mappings (some tasks moved to another sprint, others to backlog/None).
2. **SPRINT-02:**
   - Existing milestones missing `project_id` must be assigned correctly during Alembic migration. Test framework should verify schema constraints.
3. **SPRINT-03:**
   - Verify `sprint_id` is an optional (nullable) field, distinct from `milestone_id`.
   - Verify that removing a task from a sprint (setting `sprint_id=None`) does not affect its status unless specified.
4. **SPRINT-04:**
   - API endpoints fetching the board tasks must respect the `sprint_id` filter (returning only matching tasks + unassigned ones for the backlog if implemented via same request).
   - Verify task drag-and-drop actions correctly patch `sprint_id` or `status` independently.
