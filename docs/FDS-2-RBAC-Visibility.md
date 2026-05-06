# Functional Design Specification: Role-Based Access Control & Visibility System

**Version:** 1.0
**Date:** 2026-05-07
**Status:** Draft

## 1. Overview

This specification details the Role-Based Access Control (RBAC) and visibility system in TeamFlow, which ensures users only see and interact with resources appropriate to their role and organizational scope.

### 1.1 Purpose

Implement a flexible visibility model that:
- Enforces role-based access to resources
- Scopes data visibility by organizational hierarchy
- Prevents unauthorized access to sensitive information
- Supports multiple leadership levels (manager, supervisor, assistant_manager)
- Enables supervisors to manage their teams without seeing other teams

### 1.2 Scope

- Role definitions and permissions
- Visibility rules for all resources
- Sub-team hierarchy and supervision
- Access control enforcement in API routes
- Frontend visibility guards

### 1.3 Roles

| Role | Description | Visibility Scope |
|------|-------------|------------------|
| **Manager** | Organization-wide leadership | All users, all projects, all data |
| **Supervisor** | Team leader for one or more sub-teams | Own sub-team + supervised sub-teams |
| **Assistant Manager** | Shared supervision | Same as supervisor |
| **Member** | Individual contributor | Own sub-team only |

## 2. Visibility Rules

### 2.1 Core Principles

1. **Principle of Least Privilege:** Users see only what they need
2. **Organizational Hierarchy:** Visibility follows reporting lines
3. **Role-Based:** Different roles see different data shapes
4. **Enforced at API Level:** All routes validate visibility

### 2.2 Resource Visibility Matrix

| Resource | Manager | Supervisor | Assistant Manager | Member |
|----------|---------|------------|-------------------|--------|
| **Users** | All | Own team + supervised teams | Own team + supervised teams | Own sub-team only |
| **Tasks** | All | Tasks in visible sub-teams | Tasks in visible sub-teams | Own tasks only |
| **Projects** | All | Projects in visible sub-teams | Projects in visible sub-teams | Projects in own sub-team |
| **Milestones** | All | Milestones in visible projects | Milestones in visible projects | Milestones in visible projects |
| **Performance** | All | Users in visible sub-teams | Users in visible sub-teams | Self only |
| **Updates** | All | Updates from visible sub-teams | Updates from visible sub-teams | Updates from own sub-team |
| **Schedule** | All | Own schedule + team members | Own schedule + team members | Own schedule only |
| **Knowledge Sessions** | All | Sessions in visible scope | Sessions in visible scope | Sessions in visible scope |

### 2.3 Sub-Team Visibility Rules

**Manager:**
- Can see all sub-teams
- Can switch between sub-teams via query parameter
- Default: sees all sub-teams

**Supervisor/Assistant Manager:**
- Sees own sub_team_id
- Sees sub-teams they supervise (SubTeam.supervisor_id == user.id)
- Cannot see sub-teams outside their supervision chain

**Member:**
- Sees only their own sub_team_id
- Cannot switch sub-teams
- Blocked from accessing other sub-teams

## 3. Data Model

### 3.1 User Model

```python
class User:
    id: int (PK)
    email: str (unique)
    username: str (unique)
    full_name: str
    hashed_password: str
    role: UserRole (enum: manager, supervisor, assistant_manager, member)
    sub_team_id: int (FK to SubTeam, nullable for managers)
    is_active: bool
    created_at: datetime
    updated_at: datetime
```

### 3.2 SubTeam Model

```python
class SubTeam:
    id: int (PK)
    name: str
    supervisor_id: int (FK to User)
    created_at: datetime
    updated_at: datetime
```

**Relationship:**
- A supervisor can supervise multiple sub-teams
- A user belongs to exactly one sub_team_id (except managers)

## 4. Visibility Service

### 4.1 Service Location

`backend/app/services/visibility.py`

### 4.2 Key Functions

#### `visible_sub_team_ids(session, current_user, requested_sub_team_id)`

Returns the list of sub-team IDs the user can see.

**Logic:**
```python
if is_manager(current_user):
    if requested_sub_team_id:
        # Validate sub-team exists
        return [requested_sub_team_id]
    return None  # Manager sees all

if is_member(current_user):
    if current_user.sub_team_id is None:
        return []
    if requested_sub_team_id and requested_sub_team_id != current_user.sub_team_id:
        raise HTTPException(403, "Invalid sub-team")
    return [current_user.sub_team_id]

if is_leader(current_user):
    allowed_ids = await leader_sub_team_ids(session, current_user)
    if requested_sub_team_id and requested_sub_team_id not in allowed_ids:
        raise HTTPException(403, "Invalid sub-team")
    return allowed_ids
```

#### `visible_user_filter(current_user, allowed_sub_team_ids)`

Returns SQLAlchemy filter expression for user queries.

**Logic:**
```python
if is_manager(current_user):
    return true()  # See all users

if is_member(current_user):
    if current_user.sub_team_id is None:
        return false()
    return User.sub_team_id == current_user.sub_team_id

if is_leader(current_user):
    ids = allowed_sub_team_ids or []
    if not ids:
        return false()
    return (User.sub_team_id.in_(ids)) & (
        (User.role == UserRole.member) | 
        (User.role.in_(LEADERSHIP_ROLES))
    )
```

#### `require_visible_user(session, current_user, target_user)`

Validates that current_user can see target_user.

**Raises:** HTTPException(403) if target_user is outside visible scope.

## 5. API Route Enforcement

### 5.1 Pattern for Protected Routes

```python
from app.services.visibility import (
    visible_sub_team_ids,
    scoped_sub_team_filter,
    require_visible_user
)

@router.get("/api/tasks/")
async def list_tasks(
    db: AsyncSession,
    current_user: User = Depends(get_current_user)
):
    # Get visible sub-team IDs
    allowed_ids = await visible_sub_team_ids(db, current_user)
    
    # Build query with visibility filter
    query = select(Task).join(Project).where(
        scoped_sub_team_filter(Project.sub_team_id, current_user, allowed_ids)
    )
    
    result = await db.execute(query)
    return result.scalars().all()
```

### 5.2 Sub-Team Parameter Handling

Routes that accept a `sub_team_id` query parameter must validate it:

```python
@router.get("/api/users/")
async def list_users(
    sub_team_id: Optional[int] = None,
    db: AsyncSession,
    current_user: User = Depends(get_current_user)
):
    # This function validates sub_team_id is in allowed scope
    allowed_ids = await visible_sub_team_ids(
        db, current_user, requested_sub_team_id=sub_team_id
    )
    
    query = select(User).where(
        visible_user_filter(current_user, allowed_ids)
    )
    result = await db.execute(query)
    return result.scalars().all()
```

### 5.3 Assignee Validation

When assigning a task to a user:

```python
async def _require_visible_assignee(
    db: AsyncSession,
    current_user: User,
    assignee_id: Optional[int]
):
    if assignee_id is None:
        return
    
    result = await db.execute(select(User).where(User.id == assignee_id))
    assignee = result.scalar_one_or_none()
    if not assignee:
        raise HTTPException(404, "Assignee not found")
    
    # Validate visibility
    await require_visible_user(db, current_user, assignee)
```

## 6. Frontend Visibility Guards

### 6.1 Store-Based Guards

```typescript
// lib/stores/auth.ts
import { derived } from 'svelte/store';
import { auth } from './auth';

export const isManager = derived(auth, ($auth) => 
  $auth.user?.role === 'manager'
);

export const isSupervisor = derived(auth, ($auth) => 
  $auth.user?.role === 'supervisor'
);

export const isMember = derived(auth, ($auth) => 
  $auth.user?.role === 'member'
);
```

### 6.2 Route Guards

```svelte
<!-- routes/+layout.svelte -->
<script>
import { onMount } from 'svelte';
import { auth } from '$lib/stores/auth';
import { page } from '$app/stores';

onMount(() => {
  $page.subscribe(() => {
    // Check if user has access to current route
    const requiredRole = $page.data.requiredRole;
    if (requiredRole && !hasRole($auth.user, requiredRole)) {
      window.location.href = '/unauthorized';
    }
  });
});
</script>
```

### 6.3 Component Conditional Rendering

```svelte
{#if $isManager || $isSupervisor}
  <TeamHealthPanel />
{/if}

{#if $isManager}
  <OrganizationWideMetrics />
{/if}
```

## 7. Role Permissions

### 7.1 Manager Permissions

- View all users, tasks, projects, milestones
- Assign tasks to any user
- Create projects in any sub-team
- View performance metrics for all users
- Manage team membership
- Override visibility restrictions (not implemented)

### 7.2 Supervisor Permissions

- View users in own sub-team + supervised sub-teams
- Assign tasks to visible users
- Create projects in visible sub-teams
- View performance metrics for visible users
- Cannot see other supervisors' teams

### 7.3 Assistant Manager Permissions

- Same as supervisor
- Can share supervision responsibilities

### 7.4 Member Permissions

- View own tasks only
- Create tasks (assigned to self or visible users)
- View projects in own sub-team
- View own performance metrics
- Cannot see other members' workload or performance

## 8. Implementation Examples

### 8.1 Task Assignment

**Scenario:** Supervisor tries to assign task to user in different sub-team

```python
# API call
POST /api/tasks/
{
  "title": "New Task",
  "assignee_id": 123  # User in different sub-team
}

# Validation
await _require_visible_assignee(db, current_user, 123)

# Result
HTTP 403 Forbidden
{
  "detail": "User outside visible scope"
}
```

### 8.2 Project Creation

**Scenario:** Supervisor creates project

```python
# API call
POST /api/projects/
{
  "name": "New Project",
  "sub_team_id": 456  # Must be in visible sub-teams
}

# Validation
allowed_ids = await visible_sub_team_ids(db, current_user, 456)
# If 456 not in allowed_ids:
#   HTTP 403 Forbidden
```

### 8.3 Performance View

**Scenario:** Member views performance page

```python
# API call
GET /api/performance/

# Backend logic
if is_member(current_user):
    # Return only self metrics
    return metrics.filter(user_id == current_user.id)

if is_supervisor(current_user):
    allowed_ids = await leader_sub_team_ids(session, current_user)
    # Return metrics for users in allowed sub-teams
    return metrics.filter(user.sub_team_id.in_(allowed_ids))
```

## 9. Testing

### 9.1 Backend Tests

```python
# tests/test_visibility.py

async def test_member_cannot_see_other_sub_team(db, member_user):
    # Member in sub-team A tries to access sub-team B
    with pytest.raises(HTTPException) as exc:
        await visible_sub_team_ids(db, member_user, requested_sub_team_id=team_b_id)
    assert exc.value.status_code == 403

async def test_supervisor_can_see_supervised_teams(db, supervisor_user):
    # Supervisor sees own team + supervised teams
    allowed_ids = await visible_sub_team_ids(db, supervisor_user)
    assert supervisor_user.sub_team_id in allowed_ids
    assert supervised_team_id in allowed_ids

async def test_manager_sees_all(db, manager_user):
    # Manager can request any sub-team
    allowed_ids = await visible_sub_team_ids(db, manager_user, requested_sub_team_id=any_id)
    assert allowed_ids == [any_id]
```

### 9.2 Frontend Tests

```typescript
// tests/visibility.spec.ts

test('member cannot see team health panel', async ({ page }) => {
  await loginAsMember(page);
  await page.goto('/');
  
  const teamHealth = page.locator('[data-testid="team-health-section"]');
  await expect(teamHealth).not.toBeVisible();
});

test('supervisor sees team health panel', async ({ page }) => {
  await loginAsSupervisor(page);
  await page.goto('/');
  
  const teamHealth = page.locator('[data-testid="team-health-section"]');
  await expect(teamHealth).toBeVisible();
});
```

## 10. Security Considerations

### 10.1 Attack Vectors

**Sub-Team Enumeration:**
- Prevent by validating sub_team_id against allowed list
- Return 403 instead of 404 for invalid sub-teams

**Privilege Escalation:**
- JWT token must include role
- Backend must validate role on every protected route
- Never trust client-side role checks

**Cross-Team Data Access:**
- All queries must include visibility filters
- Never use raw IDs without validation
- Assignee validation on task creation/update

### 10.2 Audit Logging

**Future Enhancement:**
- Log all access control decisions
- Track failed visibility checks
- Alert on suspicious patterns

## 11. Future Enhancements

### 11.1 Planned Features

- **Role Assignment:** Managers can assign supervisor roles
- **Temporary Visibility:** Grant temporary access to other teams
- **Custom Roles:** Define custom role permissions
- **Resource-Level ACLs:** Fine-grained permissions per project
- **Audit Logs:** Track all access control events

### 11.2 Technical Debt

- Add comprehensive visibility test coverage
- Implement audit logging
- Add rate limiting for visibility checks
- Optimize visibility queries for large organizations
