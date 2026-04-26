# Phase 14: Sprint Model - Pattern Map

**Mapped:** 2026-04-26
**Files analyzed:** 8
**Analogs found:** 7 / 8

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `backend/app/models.py` | model | CRUD | `backend/app/models.py` | exact |
| `backend/app/schemas.py` | config | request-response | `backend/app/schemas.py` | exact |
| `backend/app/routers/sprints.py` | controller | request-response | `backend/app/routers/milestones.py` | exact |
| `backend/app/routers/tasks.py` | controller | request-response | `backend/app/routers/tasks.py` | exact |
| `backend/alembic/versions/xxx.py` | migration | transform | `backend/alembic/versions/f836fa8d42c6...py` | exact |
| `frontend/src/lib/components/tasks/KanbanBoard.svelte` | component | user-interaction | `frontend/src/lib/components/tasks/KanbanBoard.svelte` | exact |
| `frontend/src/routes/tasks/+page.svelte` | route | request-response | `frontend/src/routes/tasks/+page.svelte` | exact |
| `frontend/src/lib/components/sprints/SprintCloseModal.svelte` | component | user-interaction | N/A | None |

## Pattern Assignments

### `backend/app/routers/sprints.py` (controller, request-response)

**Analog:** `backend/app/routers/milestones.py`

**Imports pattern** (lines 1-10):
```python
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user
from app.database import get_db
from app.models import Milestone, User
from app.schemas import MilestoneCreate, MilestoneOut, MilestoneUpdate
```

**Auth pattern** (lines 14-19):
```python
@router.get("/", response_model=List[MilestoneOut])
async def list_milestones(
    project_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
```

**Core CRUD pattern** (lines 26-34):
```python
@router.post("/", response_model=MilestoneOut, status_code=201)
async def create_milestone(
    payload: MilestoneCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    milestone = Milestone(**payload.model_dump())
    db.add(milestone)
    await db.flush()
    await db.refresh(milestone)
    return milestone
```

**Error handling pattern** (lines 41-45):
```python
    result = await db.execute(select(Milestone).where(Milestone.id == milestone_id))
    milestone = result.scalar_one_or_none()
    if not milestone:
        raise HTTPException(status_code=404, detail="Milestone not found")
```

---

### `backend/app/models.py` (model, CRUD)

**Analog:** `backend/app/models.py` (Milestone model)

**Core pattern** (lines 142-154):
```python
class Milestone(Base):
    __tablename__ = "milestones"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(Enum(MilestoneStatus), default=MilestoneStatus.planned)
    start_date = Column(DateTime, nullable=True)
    due_date = Column(DateTime, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None)
    )

    project = relationship("Project", back_populates="milestones")
    tasks = relationship("Task", back_populates="milestone")
```

---

### `backend/app/schemas.py` (config, request-response)

**Analog:** `backend/app/schemas.py` (Milestone schemas)

**Validation pattern** (lines 110-120):
```python
class MilestoneCreate(BaseModel):
    title: str
    description: Optional[str] = None
    status: MilestoneStatus = MilestoneStatus.planned
    start_date: Optional[datetime] = None
    due_date: datetime
    project_id: int

    _normalize_dates = field_validator("start_date", "due_date", mode="after")(
        _to_naive_utc
    )
```

---

### `backend/app/routers/tasks.py` (controller, request-response)

**Analog:** `backend/app/routers/tasks.py` (Filtering logic)

**Core Pattern (Query Parameter Filtering)** (lines 119-122):
```python
    if project_id:
        query = query.where(Task.project_id == project_id)
    if milestone_id:
        query = query.where(Task.milestone_id == milestone_id)
```

**Core Pattern (Patch Updates)** (lines 154-170):
```python
    update_data = payload.model_dump(exclude_unset=True)
    # ... business logic logic ...
    for field, value in update_data.items():
        setattr(task, field, value)
    task.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)
    await db.flush()
    await db.refresh(task, ["assignee"])
    return task
```

---

### `frontend/src/lib/components/tasks/KanbanBoard.svelte` (component, event-driven)

**Analog:** `frontend/src/lib/components/tasks/KanbanBoard.svelte`

**DND Setup Pattern** (lines 18-21):
```typescript
	async function handleConsider(e: CustomEvent, colIndex: number) {
		grouped[colIndex].items = e.detail.items;
		grouped = grouped;
	}
```

**DND Drop Pattern** (lines 29-37):
```typescript
		const info = e.detail.info;
		if (info.trigger === TRIGGERS.DROPPED_INTO_ZONE && info.source === SOURCES.POINTER) {
			const draggedId = info.id;
			const moved = newItems.find((t: any) => String(t.id) === String(draggedId));
			if (moved && moved.status !== targetStatus) {
				try {
					await onStatusChange(moved.id, targetStatus);
				} catch {
					// parent handler should revert by reassigning `tasks`
				}
			}
		}
```

## Shared Patterns

### Centralized Authentication and Multi-tenancy
**Source:** `backend/app/routers/tasks.py`
**Apply to:** Sprints router queries
```python
    # Apply sub-team filter (admin may have None = all teams)
    if sub_team:
        query = query.join(Project, Task.project_id == Project.id).where(
            Project.sub_team_id == sub_team.id
        )
```

### Date Normalization
**Source:** `backend/app/schemas.py`
**Apply to:** Sprint Create/Update Schemas
```python
    _normalize_dates = field_validator("start_date", "end_date", mode="after")(
        _to_naive_utc
    )
```

## No Analog Found

Files with no close match in the codebase:

| File | Role | Data Flow | Reason |
|------|------|-----------|--------|
| `frontend/src/lib/components/sprints/SprintCloseModal.svelte` | component | user-interaction | Modals are currently rendered inline (e.g. in `tasks/+page.svelte`); no separate standalone modal component exists to copy from. Planner should adapt the inline modal pattern into a separate component. |

## Metadata

**Analog search scope:** `backend/app/routers/*.py`, `backend/app/*.py`, `frontend/src/lib/components/**/*.svelte`, `frontend/src/routes/tasks/+page.svelte`
**Files scanned:** ~10
**Pattern extraction date:** 2026-04-26