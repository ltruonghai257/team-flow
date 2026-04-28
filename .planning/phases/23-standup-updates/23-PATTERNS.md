# Phase 23: Standup Updates - Pattern Map

**Mapped:** 2026-04-28
**Files analyzed:** 12 (10 new, 2 modified)
**Analogs found:** 12 / 12

---

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `backend/app/models/updates.py` | model | CRUD | `backend/app/models/notifications.py` | exact |
| `backend/app/schemas/updates.py` | model (schema) | request-response | `backend/app/schemas/work.py` | exact |
| `backend/app/routers/updates.py` | router/controller | CRUD + request-response | `backend/app/routers/schedules.py` | exact |
| `backend/alembic/versions/…_add_standup_tables.py` | migration | batch | `backend/alembic/versions/c2d3e4f5a6b7_add_sprint_release_reminders.py` | exact |
| `frontend/src/lib/apis/updates.ts` | utility (API module) | request-response | `frontend/src/lib/apis/tasks.ts` | exact |
| `frontend/src/lib/stores/updates.ts` | store | event-driven | `frontend/src/lib/stores/notifications.ts` | role-match |
| `frontend/src/routes/updates/+page.svelte` | component (route page) | request-response | `frontend/src/routes/schedule/+page.svelte` | exact |
| `frontend/src/lib/components/updates/StandupForm.svelte` | component | request-response | `frontend/src/routes/schedule/+page.svelte` (form section) | role-match |
| `frontend/src/lib/components/updates/StandupCard.svelte` | component | request-response | `frontend/src/routes/schedule/+page.svelte` (list item section) | role-match |
| `frontend/src/lib/components/updates/SnapshotPanel.svelte` | component | transform | `frontend/src/routes/schedule/+page.svelte` (event list section) | partial |
| `backend/app/models/__init__.py` | config | — | self | exact |
| `frontend/src/routes/+layout.svelte` | config | — | self | exact |

---

## Pattern Assignments

### `backend/app/models/updates.py` (model, CRUD)

**Analog:** `backend/app/models/notifications.py`

**Imports pattern** (lines 1-11):
```python
from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.database import Base
```
Add for this file:
```python
from sqlalchemy.dialects.postgresql import JSONB
```

**Core model pattern — column definitions** (notifications.py lines 14-30):
```python
class EventNotification(Base):
    __tablename__ = "event_notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    event_type = Column(Enum(NotificationEventType), nullable=False)
    ...
    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None)
    )
```

**updated_at pattern with onupdate** (notifications.py lines 43-47):
```python
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
        onupdate=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
    )
```

**Settings/config table analog (single-row)** (notifications.py SubTeamReminderSettings lines 33-52):
```python
class SubTeamReminderSettings(Base):
    __tablename__ = "sub_team_reminder_settings"

    id = Column(Integer, primary_key=True, index=True)
    sub_team_id = Column(
        Integer, ForeignKey("sub_teams.id"), nullable=False, unique=True, index=True
    )
    lead_time_days = Column(Integer, nullable=False, default=2)
    sprint_reminders_enabled = Column(Boolean, nullable=False, default=True)
    ...
    sub_team = relationship("SubTeam", foreign_keys=[sub_team_id])
```

**Apply to `StandupPost`, `StandupTemplate`, `StandupSettings`:**
- `StandupPost`: `id`, `author_id` (FK users), `sub_team_id` (FK sub_teams), `field_values` (JSONB), `task_snapshot` (JSONB), `created_at`, `updated_at`
- `StandupTemplate`: `id`, `sub_team_id` (FK sub_teams, unique), `fields` (JSONB — ordered list of strings), `created_at`, `updated_at`
- `StandupSettings`: `id`, `default_fields` (JSONB — list of 6 field name strings), `updated_at` — single-row global settings table; seed in migration

---

### `backend/app/schemas/updates.py` (schema, request-response)

**Analog:** `backend/app/schemas/work.py`

**Imports pattern** (work.py lines 1-13):
```python
from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, field_validator

from app.models.enums import (...)
```
For updates schemas, no enum imports needed — JSONB fields map to `dict`/`list`.

**Create/Update/Out triad pattern** (work.py lines 27-49):
```python
class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    color: str = "#6366f1"
    sub_team_id: Optional[int] = None


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    ...


class ProjectOut(BaseModel):
    id: int
    name: str
    ...
    model_config = {"from_attributes": True}
```

**Key constraint for StandupPostUpdate:** Include ONLY `field_values: dict` — exclude `task_snapshot`, `author_id`, `sub_team_id` from the update schema to prevent mass-assignment attacks (STATE.md security note).

**Key constraint for StandupPostOut:** Include `id`, `author_id`, `sub_team_id`, `field_values`, `task_snapshot`, `created_at`, `updated_at`, and a nested author name field (join needed or denormalized via router). Use `model_config = {"from_attributes": True}` on all Out schemas.

---

### `backend/app/routers/updates.py` (router, CRUD + request-response)

**Analog:** `backend/app/routers/schedules.py`

**Imports pattern** (schedules.py lines 1-12):
```python
from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.utils.auth import get_current_user
from app.db.database import get_db
from app.models import Schedule, User
from app.schemas import ScheduleCreate, ScheduleOut, ScheduleUpdate
```
Add for updates router:
```python
from app.utils.auth import get_current_user, get_sub_team, require_supervisor
from app.models import User
from app.models.updates import StandupPost, StandupTemplate, StandupSettings
from app.schemas.updates import (
    StandupPostCreate, StandupPostOut, StandupPostUpdate,
    TemplateOut, TemplateUpdate,
)
```

**Router declaration** (schedules.py line 13):
```python
router = APIRouter(prefix="/api/schedules", tags=["schedules"])
```
Apply as:
```python
router = APIRouter(prefix="/api/updates", tags=["updates"])
```

**List endpoint with query params + sub-team scoping** (schedules.py lines 16-30):
```python
@router.get("/", response_model=List[ScheduleOut])
async def list_schedules(
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = select(Schedule).where(Schedule.user_id == current_user.id)
    if start:
        query = query.where(Schedule.start_time >= start)
    ...
    result = await db.execute(query)
    return result.scalars().all()
```
Adapt with `author_id`, `date`, `cursor` query params and `sub_team = Depends(get_sub_team)`. Cursor pagination: `query.where(StandupPost.id < cursor).order_by(StandupPost.id.desc()).limit(limit + 1)`.

**Create endpoint** (schedules.py lines 33-43):
```python
@router.post("/", response_model=ScheduleOut, status_code=201)
async def create_schedule(
    payload: ScheduleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    schedule = Schedule(**payload.model_dump(), user_id=current_user.id)
    db.add(schedule)
    await db.flush()
    await db.refresh(schedule)
    return schedule
```
Adapt: build `task_snapshot` server-side before `db.add(post)` using `select(Task).where(Task.assignee_id == current_user.id)`.

**PATCH endpoint with ownership check** (schedules.py lines 59-74):
```python
@router.patch("/{schedule_id}", response_model=ScheduleOut)
async def update_schedule(
    schedule_id: int,
    payload: ScheduleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Schedule).where(Schedule.id == schedule_id, Schedule.user_id == current_user.id))
    schedule = result.scalar_one_or_none()
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(schedule, field, value)
    await db.flush()
    await db.refresh(schedule)
    return schedule
```
Adapt: split ownership check explicitly since `updates` checks `post.author_id != current_user.id` (not embedded in WHERE, because admin may also fetch — raise 403 explicitly as per RESEARCH.md Pattern 5).

**DELETE endpoint** (schedules.py lines 77-88):
```python
@router.delete("/{schedule_id}", status_code=204)
async def delete_schedule(
    schedule_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Schedule).where(Schedule.id == schedule_id, ...))
    schedule = result.scalar_one_or_none()
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    await db.delete(schedule)
    await db.flush()
```

**Auth guard for supervisor-only template PUT:**
```python
from app.utils.auth import require_supervisor

@router.put("/template", response_model=TemplateOut)
async def update_template(
    payload: TemplateUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_supervisor),
    sub_team = Depends(get_sub_team),
):
```
`require_supervisor` is at `backend/app/utils/auth.py` lines 67-73.

---

### `backend/alembic/versions/…_add_standup_tables.py` (migration, batch)

**Analog:** `backend/alembic/versions/c2d3e4f5a6b7_add_sprint_release_reminders.py`

**File header pattern** (lines 1-17):
```python
"""add standup tables

Revision ID: <generated>
Revises: <last_head>
Create Date: ...

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "<generated>"
down_revision: Union[str, Sequence[str], None] = "<last_head>"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None
```

**JSONB import needed (not in analog — add explicitly):**
```python
from sqlalchemy.dialects.postgresql import JSONB
```

**op.create_table with FKs and indexes** (lines 52-91 of analog):
```python
op.create_table(
    "sub_team_reminder_settings",
    sa.Column("id", sa.Integer(), nullable=False),
    sa.Column("sub_team_id", sa.Integer(), nullable=False),
    ...
    sa.ForeignKeyConstraint(["sub_team_id"], ["sub_teams.id"]),
    sa.PrimaryKeyConstraint("id"),
    sa.UniqueConstraint("sub_team_id"),
)
op.create_index(
    op.f("ix_sub_team_reminder_settings_id"),
    "sub_team_reminder_settings",
    ["id"],
    unique=False,
)
```

**PostgreSQL-dialect guard (from analog lines 39-50):**
```python
def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        # dialect-specific operations here if needed
        pass
    op.create_table(...)
```
No new Enum types are needed for standup tables, so the `ALTER TYPE` block from the analog is not needed. The JSONB columns just use `JSONB()` directly.

**Data seed for StandupSettings (add after create_table):**
```python
    # Seed global default template settings row
    op.execute(
        sa.text(
            "INSERT INTO standup_settings (default_fields, updated_at) "
            "VALUES (:fields, NOW()) "
            "ON CONFLICT DO NOTHING"
        ).bindparams(
            fields='["Pending Tasks","Future Tasks","Blockers","Need Help From","Critical Timeline","Release Date"]'
        )
    )
```

**downgrade pattern** (analog lines 145-175): drop indexes then drop tables in reverse dependency order.

---

### `frontend/src/lib/apis/updates.ts` (utility/API module, request-response)

**Analog:** `frontend/src/lib/apis/tasks.ts`

**Full file pattern** (tasks.ts lines 1-30):
```typescript
import { request } from './request';

export const tasks = {
    list: (params?: Record<string, string | boolean | number>) => {
        const qs = params
            ? '?' +
              new URLSearchParams(params as Record<string, string>).toString()
            : '';
        return request(`/tasks/${qs}`);
    },
    get: (id: number) => request(`/tasks/${id}`),
    create: (data: object) =>
        request('/tasks/', { method: 'POST', body: JSON.stringify(data) }),
    update: (id: number, data: object) =>
        request(`/tasks/${id}`, {
            method: 'PATCH',
            body: JSON.stringify(data),
        }),
    delete: (id: number) => request(`/tasks/${id}`, { method: 'DELETE' }),
};
```

**Adapt for updates — additional template methods and nullable param filtering:**
```typescript
import { request } from './request';

export const updates = {
    getTemplate: () => request('/updates/template'),
    putTemplate: (data: object) =>
        request('/updates/template', { method: 'PUT', body: JSON.stringify(data) }),
    list: (params?: Record<string, string | number | null>) => {
        const filtered = Object.fromEntries(
            Object.entries(params ?? {}).filter(([, v]) => v != null)
        ) as Record<string, string>;
        const qs = Object.keys(filtered).length
            ? '?' + new URLSearchParams(filtered).toString()
            : '';
        return request(`/updates/${qs}`);
    },
    create: (data: object) =>
        request('/updates/', { method: 'POST', body: JSON.stringify(data) }),
    update: (id: number, data: object) =>
        request(`/updates/${id}`, { method: 'PATCH', body: JSON.stringify(data) }),
    delete: (id: number) =>
        request(`/updates/${id}`, { method: 'DELETE' }),
};
```
Note: nullable param filtering differs from `tasks.ts` — needed because `cursor`, `author_id`, `date` may be `null` when not set.

**request() helper** (`frontend/src/lib/apis/request.ts` lines 1-61): The `request()` function automatically injects `X-SubTeam-ID` header from `subTeamStore`. No changes needed to `request.ts`.

---

### `frontend/src/lib/stores/updates.ts` (store, event-driven)

**Analog:** `frontend/src/lib/stores/notifications.ts`

**Store structure pattern** (notifications.ts lines 17-30):
```typescript
type State = {
    items: NotificationItem[];
    loading: boolean;
};

function createStore() {
    const { subscribe, set, update } = writable<State>({ items: [], loading: false });
    ...
    return { subscribe, start, stop, refresh, dismiss, dismissAll };
}

export const notificationStore = createStore();
```

**Auth store writable + derived pattern** (`frontend/src/lib/stores/auth.ts` lines 1-64):
```typescript
import { writable, derived } from 'svelte/store';

function createAuthStore() {
    const { subscribe, set, update } = writable<AuthState>({
        user: null,
        loading: true
    });
    return { subscribe, async login(...) {...}, async loadMe() {...}, async logout() {...} };
}

export const authStore = createAuthStore();
export const currentUser = derived(authStore, ($a) => $a.user);
export const isSupervisor = derived(authStore, ($a) => $a.user?.role === 'admin' || $a.user?.role === 'supervisor');
```

**Adapt for updates store** — simpler than notifications (no polling, no callback):
```typescript
import { writable } from 'svelte/store';

interface UpdatesState {
    posts: StandupPost[];
    nextCursor: number | null;
    loading: boolean;
    filterAuthorId: number | null;
    filterDate: string | null;
}

export const updatesStore = writable<UpdatesState>({
    posts: [],
    nextCursor: null,
    loading: false,
    filterAuthorId: null,
    filterDate: null,
});
```
A plain `writable` (not a factory function) is sufficient here — no methods needed on the store itself. The page component calls the API and calls `updatesStore.update(...)` directly, matching the simpler pattern from `auth.ts`'s base `writable` rather than the `createStore()` factory from `notifications.ts`.

---

### `frontend/src/routes/updates/+page.svelte` (route page, request-response)

**Analog:** `frontend/src/routes/schedule/+page.svelte`

**Script block structure** (schedule/+page.svelte lines 1-203):
```svelte
<script lang="ts">
    import { onMount } from 'svelte';
    import { schedules as schedulesApi, tasks as tasksApi } from '$lib/apis';
    import { toast } from 'svelte-sonner';
    import { Plus, Pencil, Trash2, X, Calendar } from 'lucide-svelte';
    import { format } from 'date-fns';

    let scheduleList: any[] = [];
    let loading = true;

    onMount(loadAll);

    async function loadAll() {
        loading = true;
        try {
            const [schedules, taskList] = await Promise.all([...]);
            scheduleList = schedules;
        } finally {
            loading = false;
        }
    }
</script>
```

**svelte:head pattern** (schedule/+page.svelte line 205):
```svelte
<svelte:head><title>Schedule · TeamFlow</title></svelte:head>
```
Apply as:
```svelte
<svelte:head><title>Updates · TeamFlow</title></svelte:head>
```

**Page container with loading spinner** (schedule/+page.svelte lines 207-227):
```svelte
<div class="p-4 md:p-6 max-w-6xl mx-auto">
    <div class="flex items-center justify-between mb-6">
        <div>
            <h1 class="text-2xl font-bold text-white">Scheduler</h1>
            <p class="text-gray-400 text-sm mt-1">Upcoming events and task deadlines</p>
        </div>
        <button on:click={() => openCreate()} class="btn-primary">
            <Plus size={16} /> New Event
        </button>
    </div>

    {#if loading}
        <div class="flex items-center justify-center py-20">
            <div class="w-6 h-6 border-2 border-primary-500 border-t-transparent rounded-full animate-spin"></div>
        </div>
    {:else}
        ...
    {/if}
</div>
```
Apply: `max-w-4xl mx-auto` (not `max-w-6xl`), remove CTA button (form is collapsible on same page per D-07).

**isSupervisor store import** (layout.svelte line 6):
```svelte
import { authStore, isLoggedIn, isSupervisor } from '$lib/stores/auth';
```
Use `$isSupervisor` to conditionally render the template editor section (UPD-03).

**currentUser import for ownership check:**
```svelte
import { currentUser } from '$lib/stores/auth';
```
Use `$currentUser?.id === post.author_id` to gate Edit/Delete buttons.

---

### `frontend/src/lib/components/updates/StandupForm.svelte` (component, request-response)

**Analog:** `frontend/src/routes/schedule/+page.svelte` (form section, lines 321-388)

**Form pattern with submit handler and toast** (schedule/+page.svelte lines 140-183):
```svelte
async function handleSubmit() {
    const payload = { ...form, ... };
    try {
        let eventId: number;
        if (editingSchedule) {
            const updated: any = await schedulesApi.update(editingSchedule.id, payload);
            toast.success('Event updated');
        } else {
            const created: any = await schedulesApi.create(payload);
            toast.success('Event created');
        }
        showModal = false;
        await loadAll();
    } catch (e: any) {
        toast.error(e.message);
    }
}
```

**Form input/textarea pattern** (schedule/+page.svelte lines 329-384):
```svelte
<form on:submit|preventDefault={handleSubmit} class="p-5 space-y-4">
    <div>
        <label class="label" for="s-title">Title *</label>
        <input id="s-title" bind:value={form.title} class="input" required />
    </div>
    <div>
        <label class="label" for="s-desc">Description</label>
        <textarea id="s-desc" bind:value={form.description} class="input resize-none" rows="2"></textarea>
    </div>
    <div class="flex justify-end gap-3 pt-2">
        <button type="button" on:click={() => (showModal = false)} class="btn-secondary">Cancel</button>
        <button type="submit" class="btn-primary">Create Event</button>
    </div>
</form>
```
Adapt: render one `textarea class="input resize-none h-20"` per template field (from API response), with `label class="label"` for each field name. Submit button is `btn-primary` right-aligned. Add spinner when submitting.

**Collapsible toggle pattern** — no direct codebase analog; use standard Svelte `{#if expanded}` with a toggle button (described in UI-SPEC Section 2). Use `.card` class for the panel wrapper.

---

### `frontend/src/lib/components/updates/StandupCard.svelte` (component, request-response)

**Analog:** `frontend/src/routes/schedule/+page.svelte` (upcoming list section, lines 273-316)

**Card item pattern with edit/delete actions** (schedule/+page.svelte lines 282-313):
```svelte
<div class="p-3 rounded-lg bg-gray-800 border-l-2" style="border-color: {ev.color}">
    <div class="flex items-start justify-between gap-2">
        <div class="flex-1 min-w-0">
            <p class="text-sm font-medium text-gray-200 truncate">{ev.title}</p>
            <p class="text-xs text-gray-500 mt-0.5">{formatDateTime(ev.start_time)}</p>
        </div>
        {#if ev.source === 'schedule'}
            <div class="flex gap-1 flex-shrink-0">
                <button on:click={() => openEdit(ev.raw)} class="p-1 text-gray-500 hover:text-gray-300 rounded transition-colors">
                    <Pencil size={12} />
                </button>
                <button on:click={() => deleteSchedule(ev.id)} class="p-1 text-gray-500 hover:text-red-400 rounded transition-colors">
                    <Trash2 size={12} />
                </button>
            </div>
        {/if}
    </div>
</div>
```
Adapt: use `card` class (not custom `bg-gray-800`). Four local state modes: `read | editing | deleting | submitting`. Use `let mode: 'read' | 'editing' | 'deleting' | 'saving' = 'read'`.

**Inline edit state (RESEARCH.md Pattern 6):**
```svelte
<script lang="ts">
  let editing = false;
  let editValues: Record<string, string> = {};

  function startEdit() {
    editValues = { ...post.field_values };
    editing = true;
  }
  function discardEdit() { editing = false; }
  async function saveEdit() {
    editing = false;
  }
</script>

{#if editing}
  <!-- edit form -->
{:else}
  <!-- read view -->
{/if}
```

**Toast import** (schedule/+page.svelte line 5):
```svelte
import { toast } from 'svelte-sonner';
```

**date-fns format import** (schedule/+page.svelte line 7):
```svelte
import { format } from 'date-fns';
```
Apply as: `format(new Date(post.created_at), 'EEE MMM d, yyyy · HH:mm')` per UI-SPEC.

**Ownership guard for edit/delete** (UI-SPEC Section 3): `{#if post.author_id === $currentUser?.id}`. Import `currentUser` from `$lib/stores/auth`.

**Inline delete confirmation** (UI-SPEC Section 6 — no codebase analog, follows `btn-danger` pattern from app.css):
```svelte
{#if deleting}
  <div class="flex items-center gap-2">
    <span class="text-xs text-gray-400">Delete this post?</span>
    <button class="btn-danger text-xs px-3 py-2" on:click={confirmDelete}>Yes, delete</button>
    <button class="btn-secondary text-xs px-3 py-2" on:click={() => deleting = false}>Keep post</button>
  </div>
{:else}
  <button class="btn-secondary text-xs px-3 py-2" on:click={() => deleting = true}>Delete post</button>
{/if}
```

---

### `frontend/src/lib/components/updates/SnapshotPanel.svelte` (component, transform)

**Analog:** `frontend/src/routes/schedule/+page.svelte` (event list section, lines 273-316) — partial match on list rendering pattern only

**List rendering pattern** (schedule/+page.svelte lines 280-314):
```svelte
<div class="space-y-2 max-h-[500px] overflow-y-auto">
    {#each allEvents.slice().sort(...) as ev}
        <div class="p-3 rounded-lg bg-gray-800 border-l-2">
            ...
        </div>
    {/each}
</div>
```
Adapt: `{#each tasks as task}` with expand/collapse state `let expanded = false`.

**No direct codebase analog for expand/collapse toggle.** Follow UI-SPEC Section 4 directly:
```svelte
<script lang="ts">
    export let tasks: Array<{id: number; title: string; status: string; priority: string; due_date: string | null}>;
    let expanded = false;
</script>

<button class="flex items-center justify-between w-full text-xs font-semibold text-gray-500 hover:text-gray-300 transition-colors py-2 border-t border-gray-800 mt-3"
    on:click={() => expanded = !expanded}>
    <span>Task snapshot ({tasks.length} tasks)</span>
    {#if expanded}<ChevronUp size={14} />{:else}<ChevronDown size={14} />{/if}
</button>

{#if expanded}
    <div class="mt-2 space-y-2">
        {#each tasks as task}
            ...
        {/each}
    </div>
{/if}
```

**date-fns for due_date display** (schedule/+page.svelte line 7):
```svelte
import { format } from 'date-fns';
```
Apply as: `task.due_date ? format(new Date(task.due_date), 'MMM d') : '—'`

---

### `backend/app/models/__init__.py` (config, modified)

**Self-analog** — add three lines following the established import block pattern (lines 38-46):
```python
from app.models.notifications import (  # noqa: F401
    EventNotification,
    ReminderSettingsProposal,
    SubTeamReminderSettings,
)
```
Add after the `communication` block:
```python
from app.models.updates import (  # noqa: F401
    StandupPost,
    StandupSettings,
    StandupTemplate,
)
```
Must be added BEFORE running `alembic revision --autogenerate` (RESEARCH.md Pitfall 1).

---

### `frontend/src/routes/+layout.svelte` (config, modified)

**Self-analog** — add one entry to the `navItems` array (lines 30-39):
```typescript
const navItems = [
    { href: '/', label: 'Dashboard', icon: LayoutDashboard },
    { href: '/projects', label: 'Projects', icon: FolderOpen },
    { href: '/tasks', label: 'Tasks', icon: CheckSquare },
    { href: '/milestones', label: 'Milestones', icon: Milestone },
    { href: '/timeline', label: 'Timeline', icon: GanttChartSquare },
    { href: '/team', label: 'Team', icon: Users },
    { href: '/schedule', label: 'Scheduler', icon: Calendar },
    { href: '/ai', label: 'AI Assistant', icon: Bot }
];
```
Insert `{ href: '/updates', label: 'Updates', icon: MessageSquare }` after `/tasks` and before `/milestones`, per UI-SPEC Section "Modified Files".

Also add `MessageSquare` to the lucide-svelte import on line 14:
```svelte
import {
    LayoutDashboard,
    CheckSquare,
    ...,
    MessageSquare    // ← add
} from 'lucide-svelte';
```

---

## Shared Patterns

### Authentication (`Depends(get_current_user)`)
**Source:** `backend/app/utils/auth.py` lines 36-64
**Apply to:** All endpoints in `routers/updates.py`
```python
from app.utils.auth import get_current_user
...
current_user: User = Depends(get_current_user)
```

### Supervisor Guard (`Depends(require_supervisor)`)
**Source:** `backend/app/utils/auth.py` lines 67-73
**Apply to:** `PUT /api/updates/template` endpoint only
```python
async def require_supervisor(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role not in (UserRole.admin, UserRole.supervisor):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Supervisor or admin access required",
        )
    return current_user
```

### Sub-Team Scoping (`Depends(get_sub_team)`)
**Source:** `backend/app/utils/auth.py` lines 95-119
**Apply to:** `GET /api/updates/` list endpoint and `GET /api/updates/template` endpoint
```python
sub_team = Depends(get_sub_team)
# sub_team is None when admin has no X-SubTeam-ID → no filter (sees all)
# sub_team.id when member/supervisor/filtered-admin → filter by sub_team_id
```

### Async DB Session (`Depends(get_db)`)
**Source:** `backend/app/db/database.py` (referenced throughout `schedules.py`)
**Apply to:** All endpoints in `routers/updates.py`
```python
from app.db.database import get_db
...
db: AsyncSession = Depends(get_db)
```

### Pydantic `model_config`
**Source:** `backend/app/schemas/work.py` lines 49, 92, 124
**Apply to:** All `Out` schemas in `schemas/updates.py`
```python
model_config = {"from_attributes": True}
```

### Toast Notifications
**Source:** `frontend/src/routes/schedule/+page.svelte` line 5
**Apply to:** `StandupForm.svelte`, `StandupCard.svelte`
```svelte
import { toast } from 'svelte-sonner';
// success: toast.success('Standup posted')
// error:   toast.error('Failed to post update. Try again.')
```

### Error Handling (API responses)
**Source:** `frontend/src/lib/apis/request.ts` lines 42-58
**Apply to:** All `catch (e: any)` blocks in components — `e.message` is already the human-readable detail string after `request.ts` processing.
```typescript
} catch (e: any) {
    toast.error(e.message);
}
```

### Loading Spinner
**Source:** `frontend/src/routes/schedule/+page.svelte` lines 223-226
**Apply to:** `frontend/src/routes/updates/+page.svelte` initial load state
```svelte
<div class="flex items-center justify-center py-20">
    <div class="w-6 h-6 border-2 border-primary-500 border-t-transparent rounded-full animate-spin"></div>
</div>
```

### `db.flush()` + `db.refresh()` pattern
**Source:** `backend/app/routers/schedules.py` lines 41-42, 72-73
**Apply to:** All `db.add()` and `setattr` mutations in `routers/updates.py`
```python
db.add(post)
await db.flush()
await db.refresh(post)
return post
```

### `model_dump(exclude_unset=True)` for PATCH
**Source:** `backend/app/routers/schedules.py` line 70
**Apply to:** PATCH `/api/updates/{id}` endpoint
```python
for field, value in payload.model_dump(exclude_unset=True).items():
    setattr(post, field, value)
```

---

## No Analog Found

All files have analogs. No entries required here.

---

## Metadata

**Analog search scope:** `backend/app/models/`, `backend/app/schemas/`, `backend/app/routers/`, `backend/alembic/versions/`, `frontend/src/lib/apis/`, `frontend/src/lib/stores/`, `frontend/src/routes/`
**Files scanned:** 14 analog files read
**Pattern extraction date:** 2026-04-28
