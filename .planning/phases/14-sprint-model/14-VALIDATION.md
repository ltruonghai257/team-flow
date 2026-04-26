---
phase: "14"
slug: "sprint-model"
status: "validated"
nyquist_compliant: true
wave_0_complete: true
created: "2026-04-26"
updated: "2026-04-26T08:00:00.000Z"
---

# Phase 14: Sprint Model - Validation

**Validates:** 2026-04-26
**Status:** All Requirements Covered

## Validation Map

| Requirement ID | Behavior to Verify | Test Type | Automated Command | File Path | Status |
|----------------|--------------------|-----------|-------------------|-----------|--------|
| SPRINT-01 | CRUD for Sprints (name, start_date, end_date, milestone_id, status); Supervisor/Admin authorization; Sprint list view | Unit (Backend) | `pytest backend/tests/test_sprints.py -v -k "crud"` | `backend/tests/test_sprints.py` | covered |
| SPRINT-01 | Closing a sprint moves incomplete tasks to backlog or next sprint via bulk update | Unit (Backend) | `pytest backend/tests/test_sprints.py -v -k "close"` | `backend/tests/test_sprints.py` | covered |
| SPRINT-02 | Milestone required to have `project_id`; API enforces project selection | Unit (Backend) | `pytest backend/tests/test_projects.py -v -k "milestone"` | `backend/tests/test_projects.py` | covered |
| SPRINT-03 | Task create/edit accepts and persists `sprint_id` | Unit (Backend) | `pytest backend/tests/test_tasks.py -v -k "sprint"` | `backend/tests/test_tasks.py` | covered |
| SPRINT-04 | Sprint board endpoint filters tasks by selected `sprint_id`; unassigned tasks queryable | Unit (Backend) | `pytest backend/tests/test_tasks.py -v -k "filter_sprint"` | `backend/tests/test_tasks.py` | covered |
| SPRINT-03, 04| Frontend Kanban Board filters tasks by Sprint and handles drag-to-backlog nullifying `sprint_id` | Playwright E2E | `npx playwright test sprint_board.spec.ts` | `frontend/tests/sprint_board.spec.ts` | covered |

## Security Audit 2026-04-26
| Metric | Count |
|--------|-------|
| Gaps found | 6 |
| Resolved | 6 |
| Escalated | 0 |

## Nyquist Gap Analysis
*All requirements have automated verification coverage.*

### Coverage Criteria
1. **SPRINT-01:**
   - ✅ Verified that `Sprint` cannot be created by a member (403 Forbidden) - `test_create_sprint_as_member_forbidden`
   - ✅ Verified sprint close logic handles partial mappings - `test_close_sprint_partial_mapping`
2. **SPRINT-02:**
   - ✅ Verified milestone requires project_id - `test_milestone_requires_project_id`
3. **SPRINT-03:**
   - ✅ Verified `sprint_id` is nullable - `test_task_sprint_id_persistence`
   - ✅ Verified removing task from sprint sets sprint_id to None - `test_task_sprint_id_persistence`
4. **SPRINT-04:**
   - ✅ Verified task filtering by sprint_id - `test_task_sprint_filtering`
   - ✅ Verified backlog (unassigned) query - `test_task_sprint_filtering`
