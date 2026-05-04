# Phase 12 - Research: Task Types

**Researched:** 2026-04-24
**Status:** Ready for planning

## Research Goal

Determine the smallest safe implementation path for adding fixed task types (`feature`, `bug`, `task`, `improvement`) across backend persistence, task APIs, task UI, and AI task creation flows.

## Findings

### Backend Type Model

- The backend already models fixed values with Python `enum.Enum` classes in `backend/app/models.py`.
- `TaskStatus` and `TaskPriority` are SQLAlchemy `Enum(...)` columns and are mirrored by Pydantic schemas in `backend/app/schemas.py`.
- Task type should follow the same pattern:
  - Add `TaskType(str, enum.Enum)` with values `feature`, `bug`, `task`, `improvement`.
  - Add `type = Column(Enum(TaskType), default=TaskType.task, nullable=False)` to `Task`.
  - Add `type` to `TaskCreate`, `TaskUpdate`, `TaskOut`, `AiParseResponse`, and `AiBreakdownSubtask`.

### Migration Path

- The project uses Alembic, with existing migrations in `backend/alembic/versions/`.
- Phase 12 changes the database schema and must include an Alembic migration.
- Existing tasks must be backfilled to `task` with no null values.
- Safe migration shape:
  - Create PostgreSQL enum `tasktype`.
  - Add `tasks.type` with `server_default='task'` and `nullable=False`.
  - Existing rows receive `task` via the server default.
  - Downgrade drops the column and enum.

### API Filtering

- `GET /api/tasks/` currently supports single-value filters for project, milestone, assignee, status, and `my_tasks`.
- Multi-select type filtering can fit the existing API by accepting repeated query params or a comma-separated string. The execution plan should pick one concrete approach.
- For frontend simplicity and inspectable URLs, use comma-separated `types=feature,bug`.
- Backend should parse and validate each value against `TaskType`; invalid values should return `422` through FastAPI validation if typed as `list[TaskType]`, or be ignored/rejected explicitly if implemented as a string. The simpler reliable path is `types: Optional[str]` plus explicit validation into `TaskType` values.

### Frontend Task Surfaces

- The task page already has:
  - A compact filter row in `frontend/src/routes/tasks/+page.svelte`.
  - A create/edit modal with `status` and `priority` selectors.
  - List, Kanban, and Agile task displays.
- Type UI should reuse existing `.badge`, `.input`, dark surfaces, and `lucide-svelte` icons.
- Put type metadata in `frontend/src/lib/utils.ts` next to `statusColors`, `statusLabels`, and `priorityColors`.
- The UI contract requires icon plus short label:
  - `feature` -> `Feature`
  - `bug` -> `Bug`
  - `task` -> `Task`
  - `improvement` -> `Improve`

### AI Flow

- NLP parse and JSON parse both use `AiParseResponse`, so adding `type` there lets AI populate the visible form selector.
- AI breakdown uses `AiBreakdownSubtask` and `SubtaskCard.svelte`; add type to each subtask draft so the user confirms it before `Create All`.
- Prompts should request only fixed type values. Coercion should drop invalid type values and default to `task`.

## Validation Architecture

### Automated Checks

- Backend import check:
  - `cd backend && python -c "from app.models import TaskType; from app.schemas import TaskCreate, TaskOut, AiParseResponse; print('task type imports OK')"`
- Backend router import check:
  - `cd backend && python -c "from app.routers.tasks import router; print('tasks router OK')"`
- Alembic migration presence check:
  - `rg -n "tasktype|tasks.*type|TaskType" backend/alembic/versions backend/app/models.py backend/app/schemas.py backend/app/routers/tasks.py`
- Frontend type check:
  - `cd frontend && bun run check`

### Manual Checks

- Create task form shows a `Type` selector beside `Status` and `Priority`.
- Editing an existing task shows the current type and can save changes.
- List, Kanban, and Agile views show icon plus label type badges.
- Selecting multiple type chips filters visible tasks across all three views.
- AI parse/breakdown can suggest type but the user can review and change it before creating.

## Planning Recommendation

Use one executable plan with four waves:

1. Backend enum, migration, schemas, API filtering, and AI coercion.
2. Shared frontend task-type metadata and display badges across task surfaces.
3. Form, AI parse, AI breakdown, and multi-select type filter UI.
4. Verification, migration/import checks, and documentation summary.

Keep the implementation surgical. Do not introduce custom task type management or new KPI work in this phase.
