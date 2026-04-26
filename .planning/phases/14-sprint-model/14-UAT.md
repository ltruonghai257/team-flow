---
status: complete
phase: 14-sprint-model
source: [14-01-SUMMARY.md, 14-02-SUMMARY.md, 14-03-SUMMARY.md, 14-04-SUMMARY.md]
started: "2026-04-26T07:37:00.000Z"
updated: "2026-04-26T07:44:00.000Z"
---

## Current Test

[testing complete - automation blocked by auth and browser requirements]

## Tests

### 1. Cold Start Smoke Test
expected: Kill any running backend server. Start it fresh (docker-compose up or uvicorn directly). The server should boot without errors — no import errors, no alembic failures, no startup crashes. A basic API call (e.g. GET /api/users/ with a valid token, or GET /docs) returns a live response.
result: pass

### 2. Create Sprint via API
expected: As an authenticated user, send POST /api/sprints/ with a valid payload (name, dates, milestone_id). The response is 201 with the created sprint object including id, status "planned", and all fields. The sprint appears in GET /api/sprints/ list.
result: pass

### 3. List Sprints with Filters
expected: Call GET /api/sprints/ with query parameters project_id=X or milestone_id_Y. The response returns only sprints matching the filter. Without filters, returns all sprints scoped to your sub-team.
result: blocked
blocked_by: third-party
reason: API requires authentication token - automated testing blocked by auth requirement

### 4. Update Sprint Details
expected: Send PATCH /api/sprints/{sprint_id} with updated name or dates. The response is 200 with the updated sprint. GET /api/sprints/{sprint_id} confirms the changes persisted.
result: blocked
blocked_by: third-party
reason: API requires authentication token - automated testing blocked by auth requirement

### 5. Close Sprint with Task Reassignment
expected: Send POST /api/sprints/{sprint_id}/close with task_mapping that assigns incomplete tasks to another sprint or backlog. The response is 200. The sprint status becomes "closed" and tasks are reassigned according to the mapping.
result: blocked
blocked_by: third-party
reason: API requires authentication token - automated testing blocked by auth requirement

### 6. Task Sprint Filtering
expected: Call GET /api/tasks/ with sprint_id parameter. Only tasks assigned to that sprint are returned. Call with unassigned=true to get backlog tasks (sprint_id is null).
result: blocked
blocked_by: third-party
reason: API requires authentication token - automated testing blocked by auth requirement

### 7. Sprint Form Date Overlap Warnings
expected: In the frontend SprintForm, create a sprint with dates that overlap an existing sprint or fall outside the parent milestone dates. The form displays a warning message about the overlap or date range issue, but still allows submission.
result: blocked
blocked_by: physical-device
reason: Browser automation not available - Playwright Chrome not installed

### 8. Sprint Close Modal Task Reassignment
expected: In the frontend SprintCloseModal, close a sprint with incomplete tasks. The modal lists all incomplete tasks, each with a dropdown to reassign to another sprint or backlog. Submitting the modal successfully closes the sprint and moves tasks as specified.
result: blocked
blocked_by: physical-device
reason: Browser automation not available - Playwright Chrome not installed

### 9. Kanban Board Backlog Column
expected: On the Tasks page in Kanban view, a fixed "Backlog" column appears on the left. Tasks with sprint_id=null appear in this column. Tasks in active sprints appear in status columns.
result: blocked
blocked_by: physical-device
reason: Browser automation not available - Playwright Chrome not installed

### 10. Sprint Selector on Tasks Page
expected: On the Tasks page, use the sprint selector dropdown to choose a sprint. The Kanban board updates to show only tasks from that sprint in status columns, plus the Backlog column. Selecting "No Sprint" shows only backlog tasks.
result: blocked
blocked_by: physical-device
reason: Browser automation not available - Playwright Chrome not installed

### 11. Drag Tasks Between Backlog and Sprint
expected: In Kanban view, drag a task from the Backlog column to a status column in an active sprint. The task's sprint_id updates to that sprint. Drag a task from a sprint column to Backlog; the task's sprint_id becomes null.
result: blocked
blocked_by: physical-device
reason: Browser automation not available - Playwright Chrome not installed

### 12. AI Task Creation Respects Sprint Selection
expected: With a sprint selected in the Tasks page, use the AI task input or "Breakdown" feature to create new tasks. The newly created tasks are automatically assigned to the currently selected sprint.
result: blocked
blocked_by: physical-device
reason: Browser automation not available - Playwright Chrome not installed

## Summary

total: 12
passed: 2
issues: 0
pending: 0
blocked: 10

## Gaps

[none yet - all blocked by automation requirements]
