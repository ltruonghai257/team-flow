# TeamFlow Coding Guidelines

This document outlines the coding standards and conventions for TeamFlow backend (FastAPI/Python) and frontend (SvelteKit/TypeScript).

## Python Backend Guidelines

### Code Style

- **PEP 8 Compliance:** Follow PEP 8 style guide
- **Line Length:** Maximum 100 characters
- **Imports:** Group imports in this order:
  1. Standard library
  2. Third-party
  3. Local application imports
- **Type Hints:** Use type hints for all function signatures

```python
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import User

async def get_user(
    db: AsyncSession,
    user_id: int,
    include_deleted: bool = False
) -> Optional[User]:
    """Retrieve a user by ID."""
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()
```

### FastAPI Conventions

#### Route Definition

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select

router = APIRouter(prefix="/api/tasks", tags=["tasks"])

@router.get("/", response_model=List[TaskOut])
async def list_tasks(
    project_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all tasks with optional filtering."""
    query = select(Task).where(Task.assignee_id == current_user.id)
    if project_id:
        query = query.where(Task.project_id == project_id)
    result = await db.execute(query)
    return result.scalars().all()
```

#### Pydantic Schemas

- Use Pydantic v2 syntax
- Separate input and output schemas
- Use `response_model` for route validation

```python
from pydantic import BaseModel, Field

class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    priority: TaskPriority = TaskPriority.medium
    status: TaskStatus = TaskStatus.todo

class TaskOut(BaseModel):
    id: int
    title: str
    status: TaskStatus
    assignee: Optional[UserOut] = None
    
    class Config:
        from_attributes = True
```

### SQLAlchemy Models

```python
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.db.database import Base

class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    status = Column(String(50), default="todo")
    assignee_id = Column(Integer, ForeignKey("users.id"))
    
    assignee = relationship("User", back_populates="tasks")
```

### Error Handling

```python
from fastapi import HTTPException, status

async def get_task(task_id: int, db: AsyncSession) -> Task:
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    return task
```

### Async/Await Patterns

- Always use `async`/`await` for database operations
- Use `AsyncSession` for database sessions
- Commit after writes, flush to get generated IDs

```python
async def create_task(task_data: TaskCreate, db: AsyncSession) -> Task:
    task = Task(**task_data.model_dump())
    db.add(task)
    await db.flush()  # Get generated ID without committing
    await db.refresh(task, ["assignee"])
    return task
```

### Testing

```python
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

@pytest.mark.asyncio
async def test_create_task(
    async_client: AsyncClient,
    db: AsyncSession,
    test_user: User
):
    payload = {
        "title": "Test Task",
        "status": "todo"
    }
    response = await async_client.post(
        "/api/tasks/",
        json=payload,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Task"
```

## TypeScript/SvelteKit Frontend Guidelines

### Code Style

- **TypeScript Strict Mode:** Always use strict mode
- **Svelte Formatting:** Use `svelte-check` for type checking
- **Component Naming:** PascalCase for components, kebab-case for files

### Svelte Component Structure

```svelte
<script lang="ts">
  import { onMount } from 'svelte';
  import type { Task } from '$lib/types';
  
  // Props
  export let task: Task;
  export let onEdit: (id: number) => void;
  
  // State
  let isEditing = false;
  
  // Lifecycle
  onMount(() => {
    console.log('Task component mounted');
  });
  
  // Actions
  function handleEdit() {
    onEdit(task.id);
  }
</script>

<div class="task-card">
  <h2>{task.title}</h2>
  <p>{task.description}</p>
  <button on:click={handleEdit}>Edit</button>
</div>

<style>
  .task-card {
    padding: 1rem;
    border: 1px solid #e5e7eb;
    border-radius: 0.5rem;
  }
</style>
```

### API Client Pattern

```typescript
// lib/api/tasks.ts
import type { Task, TaskCreate, TaskUpdate } from '$lib/types';

export const tasksApi = {
  async list(filters?: TaskFilters): Promise<Task[]> {
    const response = await fetch(`/api/tasks${filters ? '?' + new URLSearchParams(filters) : ''}`);
    if (!response.ok) throw new Error('Failed to fetch tasks');
    return response.json();
  },
  
  async create(data: TaskCreate): Promise<Task> {
    const response = await fetch('/api/tasks', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    if (!response.ok) throw new Error('Failed to create task');
    return response.json();
  },
  
  async update(id: number, data: TaskUpdate): Promise<Task> {
    const response = await fetch(`/api/tasks/${id}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    if (!response.ok) throw new Error('Failed to update task');
    return response.json();
  }
};
```

### Stores Pattern

```typescript
// lib/stores/auth.ts
import { writable, derived } from 'svelte/store';
import type { User } from '$lib/types';

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
}

function createAuthStore() {
  const { subscribe, set, update } = writable<AuthState>({
    user: null,
    token: null,
    isAuthenticated: false
  });
  
  return {
    subscribe,
    setUser: (user: User, token: string) => set({ user, token, isAuthenticated: true }),
    logout: () => set({ user: null, token: null, isAuthenticated: false })
  };
}

export const auth = createAuthStore();
export const isAuthenticated = derived(auth, ($auth) => $auth.isAuthenticated);
```

### Type Definitions

```typescript
// lib/types.ts
export interface Task {
  id: number;
  title: string;
  description: string | null;
  status: TaskStatus;
  priority: TaskPriority;
  assignee_id: number | null;
  created_at: string;
  updated_at: string;
}

export enum TaskStatus {
  Todo = 'todo',
  InProgress = 'in_progress',
  Review = 'review',
  Done = 'done',
  Blocked = 'blocked'
}

export enum TaskPriority {
  Low = 'low',
  Medium = 'medium',
  High = 'high',
  Critical = 'critical'
}
```

### TailwindCSS Usage

- Use utility classes for styling
- Avoid custom CSS when possible
- Use `@apply` for repeated patterns

```svelte
<div class="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
  <h2 class="text-xl font-semibold text-gray-900">{title}</h2>
  <p class="text-gray-600 mt-2">{description}</p>
</div>
```

## General Guidelines

### Naming Conventions

**Python:**
- Variables/Functions: `snake_case`
- Classes: `PascalCase`
- Constants: `UPPER_SNAKE_CASE`
- Private: `_leading_underscore`

**TypeScript/Svelte:**
- Variables/Functions: `camelCase`
- Classes/Interfaces/Types: `PascalCase`
- Constants: `UPPER_SNAKE_CASE`
- Files: `kebab-case`

### Git Commit Messages

Use conventional commit format:

```
feat: add task filtering by status
fix: resolve dashboard loading issue
docs: update API documentation
refactor: simplify auth middleware
test: add unit tests for task service
chore: update dependencies
```

### File Organization

**Backend:**
```
backend/
├── app/
│   ├── models/         # SQLAlchemy models
│   ├── schemas/        # Pydantic schemas
│   ├── routers/        # FastAPI route modules
│   ├── services/       # Business logic
│   ├── core/           # Config, security, utilities
│   └── db/             # Database configuration
└── tests/              # Test files
```

**Frontend:**
```
frontend/
├── src/
│   ├── routes/         # SvelteKit routes
│   ├── lib/
│   │   ├── api/        # API client functions
│   │   ├── stores/     # Svelte stores
│   │   ├── types/      # TypeScript types
│   │   └── utils/      # Utility functions
│   └── components/     # Reusable Svelte components
```

### Security Best Practices

- Never commit API keys or secrets
- Use environment variables for sensitive data
- Validate all input on both client and server
- Use parameterized queries to prevent SQL injection
- Implement rate limiting on public endpoints
- Use JWT for authentication with proper expiration
- Sanitize user input before rendering

### Performance Considerations

- Use database indexes on frequently queried columns
- Implement pagination for large datasets
- Cache expensive operations
- Use async/await for I/O operations
- Optimize bundle size in frontend
- Use lazy loading for components

### Documentation

- Document all public API endpoints
- Add docstrings to Python functions
- Comment complex logic
- Keep README.md up to date
- Document environment variables

## Code Review Checklist

- [ ] Code follows style guidelines
- [ ] Type hints are present (Python/TypeScript)
- [ ] Error handling is appropriate
- [ ] Tests are included
- [ ] No hardcoded secrets
- [ ] Database migrations included (if schema change)
- [ ] Documentation updated
- [ ] No console.log or print statements left in production code
