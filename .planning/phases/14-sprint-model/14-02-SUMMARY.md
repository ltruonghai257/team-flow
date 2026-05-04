---
phase: "14-sprint-model"
plan: 2
subsystem: "backend"
tags: ["sprints", "api", "tasks"]
requires: ["14-01"]
provides: ["Sprint API", "Task Sprint Filtering"]
affects: ["backend/app/main.py", "backend/app/routers/tasks.py"]
tech-stack: ["FastAPI", "SQLAlchemy", "Pydantic"]
key-files:
  - "backend/app/routers/sprints.py"
  - "backend/app/routers/tasks.py"
  - "backend/app/main.py"
  - "backend/app/schemas.py"
decisions:
  - "Patterned sprints router after milestones.py but added sub-team scoping via get_sub_team dependency"
  - "Implemented bulk task reassignment in close_sprint endpoint using SQLAlchemy update() for efficiency"
metrics:
  duration: "30m"
  completed_date: "2025-02-23T11:45:00Z"
---

# Phase 14 Plan 2: Sprint API Implementation Summary

Implemented the backend API endpoints and validation schemas for the Sprint Model. This allows the frontend to manage sprints and filter tasks by sprint.

## Substantive Changes

### Backend

- **New Sprints Router**: Created `backend/app/routers/sprints.py` providing:
    - `GET /api/sprints/`: List sprints with `project_id` and `milestone_id` filters, scoped to the user's active sub-team.
    - `POST /api/sprints/`: Create new sprints (verifies milestone existence).
    - `GET /api/sprints/{sprint_id}`: Retrieve single sprint.
    - `PATCH /api/sprints/{sprint_id}`: Update sprint details.
    - `DELETE /api/sprints/{sprint_id}`: Remove sprint.
    - `POST /api/sprints/{sprint_id}/close`: Closes a sprint and reassigns its tasks to new sprints or the backlog in bulk.
- **Main App Update**: Registered the new sprints router in `backend/app/main.py`.
- **Task Router Enhancements**: Updated `GET /api/tasks/` to support:
    - `sprint_id`: Filter tasks by a specific sprint.
    - `unassigned`: Boolean filter to find tasks not assigned to any sprint (backlog).
- **Schemas**: (Completed in Task 1) Added `SprintCreate`, `SprintUpdate`, `SprintOut`, and `SprintClosePayload` schemas, and updated Task schemas to include `sprint_id`.

## Deviations from Plan

None - plan executed exactly as written.

## Known Stubs

None.

## Threat Flags

| Flag | File | Description |
|------|------|-------------|
| threat_flag: endpoint_access | backend/app/routers/sprints.py | New CRUD endpoints for Sprints introduced at the API trust boundary. Scoped to `get_sub_team` to mitigate unauthorized access. |
| threat_flag: bulk_update | backend/app/routers/sprints.py | `close_sprint` performs bulk updates on Task table based on user-provided mapping. |

## Self-Check: PASSED
- Created files exist: `backend/app/routers/sprints.py`
- Commits exist: `2c26016`, `f92aa42` (and previous `4265fa6`)
- Sub-team scoping verified in `sprints.py`
