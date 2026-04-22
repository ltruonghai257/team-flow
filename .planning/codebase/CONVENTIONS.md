# Conventions

*Mapped: 2026-04-22*

## Backend (Python)

### Code Style
- Python 3.13, standard PEP 8 — no formatter config found (no `pyproject.toml`, no `ruff.toml`)
- Type hints used throughout; `Optional[T]` style (not `T | None`) — pre-3.10 style preserved
- `from __future__ import annotations` used in `scheduler_jobs.py` only

### Naming
- Modules: `snake_case` (e.g. `scheduler_jobs.py`, `task.py`)
- Classes: `PascalCase` (e.g. `TaskStatus`, `ConnectionManager`)
- Functions/variables: `snake_case`
- Pydantic schemas: `{Domain}Create`, `{Domain}Update`, `{Domain}Out` triplet pattern
- Enum values: lowercase strings matching the concept (e.g. `TaskStatus.todo = "todo"`)

### Router Pattern
Each router file follows this structure:
```python
router = APIRouter(prefix="/api/{domain}", tags=["{domain}"])

@router.get("/", response_model=List[{Domain}Out])
async def list_{domain}s(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    ...

@router.post("/", response_model={Domain}Out, status_code=201)
async def create_{domain}(payload: {Domain}Create, db: AsyncSession = Depends(get_db), ...):
    ...

@router.patch("/{id}", response_model={Domain}Out)
async def update_{domain}(id: int, payload: {Domain}Update, ...):
    update_data = payload.model_dump(exclude_unset=True)  # only update provided fields
    ...

@router.delete("/{id}", status_code=204)
async def delete_{domain}(...):
    ...
```

### Error Handling
- `HTTPException` with appropriate status codes (400, 401, 404, 422, 502)
- 404: "X not found" pattern: `result.scalar_one_or_none()` → `if not X: raise HTTPException(404, ...)`
- 502: wraps external service errors (LiteLLM): `except Exception as e: raise HTTPException(502, ...)`
- DB session: automatic rollback on exception via `get_db()` generator

### Database Patterns
- `await db.flush()` after writes (not `commit()`) — session committed by `get_db()` at end of request
- `selectinload()` for eager-loading relationships (e.g. `Task.assignee`)
- All queries use `select(Model).where(...)` style (SQLAlchemy 2.x)
- `payload.model_dump(exclude_unset=True)` for partial updates (PATCH semantics)

### Datetime Handling
- Store naive UTC datetimes in DB (`datetime.utcnow()`)
- `_to_naive_utc()` validator in schemas strips tzinfo from incoming tz-aware datetimes
- Validator applied via `field_validator(..., mode="after")` pattern

### AI Response Handling
- LiteLLM responses: `response.choices[0].message.content`
- JSON extraction: tries `re.search(r"```(?:json)?\s*(\{.*?\})\s*```", ...)` before falling back to bare `{...}` extraction
- `_coerce_ai_parse()` pattern: normalize raw dict, drop invalid enum values gracefully

## Frontend (TypeScript / Svelte)

### Code Style
- TypeScript strict mode (`tsconfig.json`)
- Svelte 5 syntax — uses `$:` reactive declarations, Svelte stores
- No ESLint/Prettier config found — code style is consistent but not enforced by tooling

### Naming
- Component files: `PascalCase.svelte` (e.g. `KanbanBoard.svelte`, `NotificationBell.svelte`)
- Module files: `camelCase.ts` (e.g. `api.ts`, `websocket.ts`)
- Store exports: `camelCase` + `Store` suffix (e.g. `authStore`, `notificationStore`)
- Derived stores: descriptive names (e.g. `currentUser`, `isLoggedIn`)

### API Client Pattern (`frontend/src/lib/api.ts`)
```typescript
const BASE = '/api';

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
    // always: credentials: 'include', Content-Type: application/json
}

export const {domain} = {
    list: () => request('/domain/'),
    get: (id: number) => request(`/domain/${id}`),
    create: (data: object) => request('/domain/', { method: 'POST', body: JSON.stringify(data) }),
    update: (id: number, data: object) => request(`/domain/${id}`, { method: 'PATCH', body: JSON.stringify(data) }),
    delete: (id: number) => request(`/domain/${id}`, { method: 'DELETE' })
};
```

### Store Pattern
```typescript
function createXStore() {
    const { subscribe, set, update } = writable<XState>({...});
    return {
        subscribe,
        async action() { ... }
    };
}
export const xStore = createXStore();
export const derivedValue = derived(xStore, ($s) => $s.field);
```

### Component Conventions
- Auth guard in `+layout.svelte` via `onMount` + reactive `$:` statements
- Icon imports from `lucide-svelte` (tree-shaken per-component)
- Toast notifications via `svelte-sonner` `toast.info()`
- Dark theme: `bg-gray-950` / `bg-gray-900` base, `text-gray-400` secondary, `primary-600` accent
- TailwindCSS utility classes inline (no separate CSS modules)

### WebSocket Messaging
All WS messages are JSON objects with a `type` discriminator field:
```typescript
chatWS.send({ type: 'channel_message', channel_id: 1, content: '...' });
chatWS.send({ type: 'heartbeat' });
```
