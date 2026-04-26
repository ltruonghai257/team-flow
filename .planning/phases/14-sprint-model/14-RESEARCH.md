# Phase 14: Sprint Model - Research

**Researched:** 2026-04-26
**Domain:** Project Management / Time-boxed Iterations
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **D-01:** The "Backlog" (unassigned tasks) should be displayed as a fixed column on the far-left of the Kanban board, allowing tasks to be easily dragged out of it.
- **D-02:** When closing a sprint, a modal should list incomplete tasks, allowing the user to select the destination (e.g., Backlog or next sprint) on a per-task basis before finalizing the close.
- **D-03:** Sprint dates are enforced loosely: the UI should warn the user if sprint dates overlap or exceed the milestone dates, but it allows creation anyway.
- **D-04:** Sprint and Milestone assignments on a task are independent fields. They can mismatch if the user chooses to do so.

### the agent's Discretion
- Exact UI design of the sprint close modal (e.g., layout of the task list and destination dropdowns).
- Visual styling of the overlap/exceed warnings for sprint dates during creation/editing.
- How to ensure the Backlog column integrates smoothly without breaking horizontal scrolling or layout on smaller screens.

### Deferred Ideas (OUT OF SCOPE)
None — discussion stayed within Phase 14 scope.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| SPRINT-01 | Sprints as time-boxed iterations within milestone | `Sprint` SQLAlchemy model with `name`, `start_date`, `end_date`, `milestone_id`, `status`. New CRUD router for Sprints. Sprint Close frontend flow. |
| SPRINT-02 | Milestones belong to one project | `Milestone` model update to require `project_id`. Alembic migration to assign existing milestones to a default project. Milestone schemas updated. |
| SPRINT-03 | Task create/edit includes sprint selector | `Task` model gets nullable `sprint_id` FK. Task create/update API schemas updated. Frontend task form gets sprint dropdown. |
| SPRINT-04 | Sprint board filters tasks by sprint | `KanbanBoard.svelte` gets "Backlog" column. Dragging to backlog updates `sprint_id` to null via `onSprintChange` callback. Sprints filtered at the API level via `sprint_id` query param. |
</phase_requirements>

## Summary

The Sprint Model phase introduces time-boxed iterations ("Sprints") to the TeamFlow platform. A `Sprint` belongs to a `Milestone` (which itself is updated to strictly belong to a `Project`). Sprints provide the framework for Kanban board filtering and task assignment. 

The primary technical challenges involve executing a zero-data-loss Alembic migration for existing Milestones (associating them with a default project), extending the task drag-and-drop system to handle the "Backlog" pseudo-column (modifying `sprint_id` rather than `status`), and constructing a multi-task update operation when closing a sprint to reassign incomplete tasks.

**Primary recommendation:** Implement the Backlog column in `KanbanBoard.svelte` as a special droppable zone that fires a distinct event to nullify a task's `sprint_id` while preserving its `status` (or resetting it to `todo`, depending on product preferences). 

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Sprint Data Management | API / Backend | Database | `Sprint` CRUD, `Task` sprint updates, and milestone associations require strong relational integrity. |
| Data Migration (Milestones) | Database | API / Backend | Alembic must backfill `project_id` on existing Milestones before enforcing the non-null constraint. |
| Board Sprint Filtering | Frontend Server | API / Backend | The frontend fetches tasks scoped by `sprint_id` (or unassigned for the project backlog) and renders them into columns. |
| Sprint Date Warnings | Browser / Client | — | Overlapping date checks are non-blocking warnings and should be computed synchronously in the client UI during form interaction. |
| Sprint Close Bulk Update | API / Backend | Browser / Client | The client submits a bulk reassignment payload (`task_id` -> `new_sprint_id` or null) and the backend executes it in a single transaction. |

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| FastAPI | >=0.115.0 | Backend API routing and validation | Existing standard for the backend stack. |
| SQLAlchemy | >=2.0.36 | ORM and Database querying | Maintains relational logic between Sprints, Milestones, Projects, and Tasks. |
| Alembic | >=1.14.0 | Database migrations | Standard for applying schema changes like adding `Sprint` and altering `Milestone`. |
| SvelteKit | 5.x | Frontend UI and components | Required framework for all UI interactions (Kanban, modals). |
| svelte-dnd-action | ^0.9.x | Drag and drop for Kanban | Used currently in `KanbanBoard.svelte`; must be extended for Backlog column. |

**Version verification:** All backend versions verified from `backend/requirements.txt` and Svelte version verified via npm view.

## Architecture Patterns

### System Architecture Diagram
```text
[Browser UI]
  │
  ├─> (Sprint Form) ──> Warns on date overlap (Local logic)
  │
  ├─> (Kanban Board)
  │    ├─> Dropped in Status Col ──> PATCH /api/tasks/{id} { status: new_status }
  │    └─> Dropped in Backlog ─────> PATCH /api/tasks/{id} { sprint_id: null }
  │
  └─> (Sprint Close Modal)
       └─> Submits mapping ───────> POST /api/sprints/{id}/close { task_mapping: [...] }
                                           │
[FastAPI Backend]                          │
  ├─> GET /api/tasks?sprint_id=X           │ (Bulk updates tasks)
  └─> Updates Sprint status ───────────────┘
```

### Recommended Project Structure
```
backend/app/routers/
├── sprints.py        # New: CRUD endpoints for sprints, bulk task updates
```

### Pattern 1: Bulk Update for Sprint Close
**What:** Instead of looping over 20 tasks and making 20 `PATCH /api/tasks/{id}` requests when closing a sprint, send a single structured request.
**When to use:** When closing a sprint and moving incomplete tasks to various destinations (Backlog or next sprint).
**Example:**
```python
# backend/app/routers/sprints.py
class SprintClosePayload(BaseModel):
    task_mapping: Dict[int, Optional[int]] # task_id -> new_sprint_id (None for Backlog)

@router.post("/{sprint_id}/close")
async def close_sprint(sprint_id: int, payload: SprintClosePayload, db: AsyncSession = Depends(get_db)):
    # 1. Verify sprint exists
    # 2. Update sprint status to closed
    # 3. Bulk update tasks in payload.task_mapping
```

### Anti-Patterns to Avoid
- **Implicit Status Changes on Backlog Drop:** If a task in `in_progress` is moved to the Backlog, it should logically revert to `todo`, or the UI needs a way to handle `in_progress` tasks in the Backlog. The safest anti-pattern to avoid is leaving a task `in_progress` while unassigned to a sprint, unless the team's workflow specifically allows it.
- **N+1 Queries on Kanban Load:** Fetching tasks and then doing individual lookups for Sprints or Milestones. Ensure `selectinload` or appropriate joins are used if Sprint data is needed on the Task card.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Drag-and-drop Backlog | Custom pointer events | `svelte-dnd-action` | Already implemented for statuses. Just add a new `dndzone` that triggers a `sprint_id` update instead of a `status` update. |
| Date Overlap Logic | Complex backend validation | Client-side `Date` checks | Requirements state it's a non-blocking warning. Pure UI logic is sufficient and faster. |

## Runtime State Inventory

| Category | Items Found | Action Required |
|----------|-------------|------------------|
| Stored data | `Milestone` records without `project_id` | Data Migration: Alembic script must assign orphaned Milestones to a default project before applying `NOT NULL` constraint. |
| Live service config | None — verified | No external services hold milestone or sprint data. |
| OS-registered state | None — verified | No OS tasks depend on milestone schemas. |
| Secrets/env vars | None — verified | No new secrets required for sprints. |
| Build artifacts | Database Schema | Redeploy backend and run Alembic migrations. |

## Common Pitfalls

### Pitfall 1: Data Migration Constraint Violations
**What goes wrong:** Applying `nullable=False` to `Milestone.project_id` crashes the database migration if existing milestones exist without a project.
**Why it happens:** Alembic tries to apply the constraint before backfilling data.
**How to avoid:** Use a multi-step migration: 1. Add column `project_id` as `nullable=True`. 2. Execute an `UPDATE` statement to set a valid `project_id` (e.g., fetching a default project or creating one). 3. Alter the column to `nullable=False`.

### Pitfall 2: Sprint and Status DND Conflicts
**What goes wrong:** Dragging a task into the Backlog column fires a status update to undefined, or dragging a task from Backlog to a status column fails to assign it to the active sprint.
**Why it happens:** The `KanbanBoard` assumes all columns represent `status`.
**How to avoid:** Distinctly handle the Backlog column. `KanbanBoard` must dispatch two types of events or a unified event: `onTaskMove(taskId, newStatus, newSprintId)`.

## Code Examples

### Alembic Multi-Step Migration (Milestone project_id)
```python
def upgrade():
    # 1. Add nullable column
    op.add_column('milestones', sa.Column('project_id', sa.Integer(), nullable=True))
    
    # 2. Backfill data
    bind = op.get_bind()
    # Find or create a default project (simplified logic)
    bind.execute(sa.text("""
        UPDATE milestones SET project_id = (SELECT id FROM projects LIMIT 1) 
        WHERE project_id IS NULL
    """))
    
    # 3. Create ForeignKey and make NOT NULL
    op.create_foreign_key('fk_milestones_project_id', 'milestones', 'projects', ['project_id'], ['id'])
    op.alter_column('milestones', 'project_id', nullable=False)
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Milestones as top-level | Milestones scoped to Projects | This Phase (14) | Stricter hierarchy, better filtering. |
| All tasks on board | Tasks filtered by Sprint / Backlog | This Phase (14) | Requires users to actively plan sprints. |

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | [ASSUMED] The Kanban board will fetch ALL tasks for a project to render the Backlog and Sprint columns simultaneously. | Architecture Patterns | If there are thousands of backlog tasks, the board will be slow. We may need to limit the Backlog fetch to recent/top tasks. |
| A2 | [ASSUMED] Moving a task to the Backlog resets its `status` to `todo`. | Anti-Patterns | If left in `review` but moved to Backlog, the Kanban board might not know which column to render it in (if Backlog is a single column, ignoring status). |

## Environment Availability

Step 2.6: SKIPPED (no external dependencies identified beyond existing Python/Node stack)

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest (Backend), Playwright (Frontend) |
| Config file | `backend/pytest.ini`, `frontend/playwright.config.ts` |
| Quick run command | `pytest -v` |
| Full suite command | `pytest -v && npx playwright test` |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| SPRINT-01 | CRUD for Sprints | unit | `pytest tests/test_sprints.py` | ❌ Wave 0 |
| SPRINT-02 | Milestone belongs to Project | unit | `pytest tests/test_milestones.py` | ✅ Wave 0 (needs update) |
| SPRINT-03 | Task sprint selector | unit | `pytest tests/test_tasks.py` | ✅ Wave 0 (needs update) |
| SPRINT-04 | Board filters by sprint | e2e | `npx playwright test --grep "Sprint Board"` | ❌ Wave 0 |

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | yes | FastAPI `get_current_user` dependency |
| V3 Session Management | yes | Access tokens per existing auth setup |
| V4 Access Control | yes | Enforce sub_team scoping server-side for Sprint operations |
| V5 Input Validation | yes | Pydantic schemas for Sprint and bulk updates |
| V6 Cryptography | no | — |

### Known Threat Patterns for FastAPI

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Cross-team access to Sprints | Information Disclosure | `get_sub_team` context applied to all read/write queries |
| Unbounded bulk update list | Denial of Service | Impose `max_length` in Pydantic schema for `task_mapping` |

## Sources

### Primary (HIGH confidence)
- Codebase Context (`backend/app/models.py`, `backend/app/routers/tasks.py`) - Verified models and current routing implementations.
- `.planning/REQUIREMENTS.md` - Strict acceptance criteria for Phase 14.
- `.planning/phases/14-sprint-model/14-CONTEXT.md` - User constraints and locked decisions.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Directly extracted from project dependencies.
- Architecture: HIGH - Follows existing FastAPI and SvelteKit patterns in the codebase.
- Pitfalls: HIGH - Database migration constraints are a known pattern in Alembic.

**Research date:** 2026-04-26
**Valid until:** 2026-05-26