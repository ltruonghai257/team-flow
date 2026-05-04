---
phase: 15
slug: custom-kanban-statuses
status: complete
created: 2026-04-26
---

# Phase 15 — Pattern Map

## Backend Patterns

| New/Changed File | Closest Existing Analog | Pattern To Follow |
|------------------|-------------------------|-------------------|
| `backend/app/models.py` | Existing `Project`, `Task`, `Sprint` models | SQLAlchemy declarative models, enum classes near top, relationships on both sides where useful |
| `backend/alembic/versions/*_add_custom_statuses.py` | `backend/alembic/versions/7b9f1c2d3e4a_add_task_type.py`, `6ff5de88b5d6_add_sprint_model.py` | Explicit Alembic DDL and data backfill; no autogenerate-only migration |
| `backend/app/schemas.py` | Existing `TaskCreate`, `TaskUpdate`, `TaskOut`, `ProjectOut` | Pydantic models grouped by domain; `model_config = {"from_attributes": True}` for response models |
| `backend/app/routers/statuses.py` | `backend/app/routers/projects.py`, `sub_teams.py`, `tasks.py` | FastAPI `APIRouter`, `get_db`, `get_current_user`, `get_sub_team`, `await db.flush()` writes |
| `backend/app/routers/tasks.py` | Existing update/create/list task functions | Preserve legacy request shape while adding `custom_status_id` support and completion transitions |
| `backend/app/main.py` | Existing router includes | Import router module and `app.include_router(statuses.router)` |
| `backend/tests/test_status_sets.py` | `backend/tests/test_projects.py`, `test_sub_teams.py` | Async HTTP tests with auth cookie and DB fixtures |
| `backend/tests/test_tasks.py` | Existing backend test style | API-level task transition tests; assert `completed_at` changes |

## Frontend Patterns

| New/Changed File | Closest Existing Analog | Pattern To Follow |
|------------------|-------------------------|-------------------|
| `frontend/src/lib/api.ts` | Existing `tasks`, `projects`, `sub_teams` client sections | Use shared `request()` so `X-SubTeam-ID` propagation is automatic |
| `frontend/src/lib/components/statuses/*.svelte` | `components/tasks/KanbanBoard.svelte`, page modal markup | Svelte 5, Tailwind utilities, existing dark cards/inputs/buttons |
| `frontend/src/lib/components/tasks/KanbanBoard.svelte` | Existing board with `svelte-dnd-action` | Preserve DnD and horizontal scroll; replace hardcoded columns with status records |
| `frontend/src/routes/tasks/+page.svelte` | Existing task page filters/modal/view switcher | Load status sets with existing page data and pass statuses into board/forms |
| `frontend/src/routes/projects/+page.svelte` | Existing project card expansion for AI summary | Add `Statuses` action and inline panel using current card expansion style |
| `frontend/src/lib/utils.ts` | Existing status fallback maps | Keep legacy fallbacks for transition only; DB statuses drive new UI |

## Non-Negotiable Cross-Phase Patterns

- Preserve `Task.status` enum during this phase; it is still used by AI parsing and legacy UI fallback.
- Add `Task.custom_status_id` and expose status metadata so Phase 16 can join on `CustomStatus.is_done`.
- Respect Phase 13 sub-team scoping through `get_sub_team()` and frontend `X-SubTeam-ID`.
- Do not overwrite unrelated dirty changes in `backend/app/schemas.py`; execution must merge around existing Phase 14 sprint schema changes.
- Keep the existing dark TeamFlow UI language and primitives from `frontend/src/app.css`.

