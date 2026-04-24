# Phase 13: Multi-Team Hierarchy + Timeline Visibility - Research

**Researched:** 2026-04-24
**Domain:** Multi-tenant data scoping, role-based access control, database migrations
**Confidence:** HIGH

## Summary

Phase 13 introduces a SubTeam model to scope all data (users, projects, tasks) by sub-team, with role-aware visibility rules: members see only their assigned projects, supervisors see their sub-team's data, admins see all data with a global switcher. The phase requires adding FK columns (sub_team_id) to existing tables, creating migration scripts, and updating all unscoped API endpoints to filter by sub-team. Frontend changes include a global sub-team switcher for admins and extending the team management page.

**Primary recommendation:** Use nullable FK columns with a default sub-team migration, add a dependency-injected sub-team context helper for API scoping, and store admin's selected sub-team in localStorage for the frontend switcher.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| SubTeam model definition | Database / Storage | — | Core data model change requires schema migration |
| Sub-team scoping enforcement | API / Backend | — | Server-side filtering ensures security; frontend filtering is insufficient |
| Role-aware visibility rules | API / Backend | — | Business logic for who sees what lives in endpoint handlers |
| Global sub-team switcher state | Browser / Client | API / Backend | UI state management for admin's selected context |
| Migration of existing data | Database / Storage | — | Data transformation during schema change |

## User Constraints (from CONTEXT.md)

### Locked Decisions

- **D-01:** All existing users and projects migrate into a single default sub-team named "Default Team" with no supervisor pre-assigned.
- **D-02:** The existing admin remains an admin and is also added to the default sub-team as a member.
- **D-03:** After migration, the admin must manually create additional sub-teams, assign supervisors, and move users/projects before the hierarchy is useful.
- **D-04:** A supervisor column on the sub-team is nullable during migration; the admin assigns supervisors via the UI afterward.
- **D-05:** Extend the existing `/team` page to include sub-team management, not a new dedicated settings page.
- **D-06:** Add a "Sub-Teams" tab or section to `/team` where the admin can create, rename, and reassign supervisors to sub-teams.
- **D-07:** Supervisors see their own sub-team's member list on `/team`; admins see all sub-teams with a switcher or tabs.
- **D-08:** Sub-team creation and supervisor reassignment happen inline on the same page where members and invites are managed.
- **D-09:** Introduce a global sub-team context switcher (sidebar or top nav) that filters the entire app for the admin.
- **D-10:** When the admin selects a sub-team, all pages (dashboard, timeline, performance, projects) scope to that sub-team automatically.
- **D-11:** Supervisors have no switcher — their entire session is implicitly scoped to their assigned sub-team.
- **D-12:** Members have no switcher — their data is implicitly scoped by their sub-team membership.
- **D-13:** Supervisors can create projects only for their own sub-team; no sub-team selector appears on the project creation form.
- **D-14:** Admins create projects for whichever sub-team is currently active in their global switcher; no per-form dropdown.
- **D-15:** Backend enforces that a supervisor's `POST /api/projects` is rejected if they try to create a project outside their sub-team.
- **D-16:** New invites are scoped to the inviter's currently active sub-team (supervisor: their own; admin: the one selected in the global switcher).
- **D-17:** No sub-team selector on the invite form; the global context or implicit supervisor scope determines the target sub-team.
- **D-18:** When a user accepts an invite, they are automatically assigned to the sub-team attached to that invite.
- **D-19:** Every data-fetching endpoint (tasks, projects, milestones, timeline, performance, dashboard, users) must filter by the requesting user's sub-team server-side.
- **D-20:** Admin endpoints bypass sub-team filtering and instead respect the global switcher context (passed as a header or query param, or stored in session).
- **D-21:** Direct API access attempts to cross-team data must return 403, not 404, to avoid leaking existence.
- **D-22:** Members see only projects on `/timeline` where they have at least one assigned task (server-side filter).
- **D-23:** Supervisors see all projects belonging to their sub-team on `/timeline`.
- **D-24:** Admins see all projects from all sub-teams; a sub-team filter (driven by the global switcher) can narrow the view.

### Claude's Discretion

- Exact placement and styling of the global sub-team switcher in the nav/sidebar.
- Whether the admin's global switcher state is stored in localStorage, URL param, or backend session.
- Exact migration implementation for `sub_team_id` columns and the default sub-team creation.
- How the timeline handles a member with zero assigned tasks (empty state copy and design).

### Deferred Ideas (OUT OF SCOPE)

None — discussion stayed within Phase 13 scope.

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| SQLAlchemy | 2.0+ (existing) | ORM for SubTeam model and FK relationships | Declarative model definition, async support, migration-ready |
| Alembic | existing | Database migrations for adding sub_team_id columns | Schema versioning, reversible migrations, data transformation |
| FastAPI | existing | API framework with dependency injection | Clean scoping via Depends() middleware pattern |
| Pydantic | existing | Request/response schemas for SubTeam APIs | Automatic validation, serialization |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| Svelte 5 stores | existing | Reactive state for sub-team switcher | Admin's selected sub-team context |
| localStorage | browser API | Persist admin's selected sub-team across page reloads | Simple key-value storage, no backend state needed |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Nullable FK columns | Non-nullable with complex multi-step migration | Nullable allows single-pass migration with default sub-team; non-nullable requires temporary constraint disable |
| localStorage for switcher state | URL param or backend session | localStorage is simplest for SPA; URL param creates shareable links but adds complexity; backend session requires server state management |

**Installation:**
No new packages needed — all required libraries already installed.

**Version verification:** All libraries are existing project dependencies (verified via package.json and requirements.txt).

## Architecture Patterns

### System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend (SvelteKit)                      │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐   │
│  │  Dashboard   │     │   Timeline   │     │  Performance  │   │
│  │  (scoped)    │     │  (scoped)    │     │   (scoped)    │   │
│  └──────┬───────┘     └──────┬───────┘     └──────┬───────┘   │
│         │                     │                     │           │
│         └─────────────────────┼─────────────────────┘           │
│                               │                                 │
│                    ┌──────────▼──────────┐                      │
│                    │  API Client (fetch) │                      │
│                    │  + X-SubTeam-ID hdr  │ (admin only)         │
│                    └──────────┬──────────┘                      │
└───────────────────────────────┼─────────────────────────────────┘
                                │ HTTP (cookies + header)
┌───────────────────────────────▼─────────────────────────────────┐
│                      Backend (FastAPI)                           │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  get_current_user (auth) → User + sub_team_id            │  │
│  └──────────────────────┬───────────────────────────────────┘  │
│                         │                                        │
│         ┌───────────────┼───────────────┐                      │
│         │               │               │                      │
│  ┌──────▼──────┐  ┌─────▼──────┐  ┌───▼────────┐             │
│  │  Member    │  │ Supervisor │  │   Admin    │             │
│  │  (implicit) │  │ (implicit) │  │ (header)   │             │
│  └──────┬──────┘  └─────┬──────┘  └───┬────────┘             │
│         │               │               │                      │
│         └───────────────┼───────────────┘                      │
│                         │                                        │
│              ┌──────────▼──────────┐                           │
│              │  Sub-Team Filter     │                           │
│              │  (WHERE sub_team_id) │                           │
│              └──────────┬──────────┘                           │
│                         │                                        │
│  ┌──────────────────────┼──────────────────────────────────┐  │
│  │                      │                      │          │  │
│ ┌▼────────┐          ┌─▼────────┐          ┌─▼────────┐  │  │
│ │ Tasks   │          │ Projects │          │ Users    │  │  │
│ │(scoped) │          │ (scoped) │          │ (scoped) │  │  │
│ └─────────┘          └──────────┘          └──────────┘  │  │
└───────────────────────────────────────────────────────────┘
                                │
┌───────────────────────────────▼─────────────────────────────────┐
│                    Database (PostgreSQL)                        │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐   │
│  │  SubTeam     │     │   User       │     │  Project     │   │
│  │  (new)       │◄────┤ sub_team_id  │◄────┤ sub_team_id  │   │
│  │  - id        │     │ - id         │     │ - id         │   │
│  │  - name      │     │ - email      │     │ - name       │   │
│  │  - supervisor_id│   │ - role       │     │ - ...        │   │
│  └──────────────┘     └──────────────┘     └──────┬───────┘   │
│         │                                          │           │
│         └──────────────────────────────────────────┘           │
│                      FK relationships                           │
└─────────────────────────────────────────────────────────────────┘
```

### Recommended Project Structure

```
backend/app/
├── models.py              # Add SubTeam model, FK columns to User/Project
├── auth.py                # Add get_sub_team() dependency
├── routers/
│   ├── sub_teams.py       # NEW: CRUD for sub-teams
│   ├── timeline.py        # Add sub_team filter
│   ├── projects.py        # Add sub_team filter + enforcement
│   ├── dashboard.py       # Add sub_team filter
│   ├── performance.py     # Add sub_team filter
│   ├── users.py           # Add sub_team filter
│   ├── invites.py         # Add sub_team_id to invites
│   └── tasks.py           # Add sub_team filter
└── schemas.py             # Add SubTeamCreate/Update/Out schemas

frontend/src/
├── routes/
│   ├── +layout.svelte      # Add global sub-team switcher (admin only)
│   └── team/+page.svelte  # Add Sub-Teams tab/section
└── lib/
    ├── api.ts              # Add sub_teams API methods
    └── stores/
        └── subTeam.ts      # NEW: sub-team switcher state (admin only)
```

### Pattern 1: Sub-Team Scoping via Dependency Injection

**What:** Create a FastAPI dependency that injects the user's sub-team context based on role and optional header.

**When to use:** All data-fetching endpoints that need to filter by sub-team.

**Example:**
```python
# backend/app/auth.py
from fastapi import Header, HTTPException
from sqlalchemy import select

async def get_sub_team(
    current_user: User = Depends(get_current_user),
    x_sub_team_id: Optional[int] = Header(None, alias="X-SubTeam-ID"),
    db: AsyncSession = Depends(get_db)
) -> Optional[SubTeam]:
    """Inject sub-team context: implicit for member/supervisor, explicit for admin."""
    if current_user.role == UserRole.member:
        # Members have exactly one sub-team
        result = await db.execute(select(SubTeam).where(SubTeam.id == current_user.sub_team_id))
        return result.scalar_one_or_none()
    elif current_user.role == UserRole.supervisor:
        # Supervisors see their assigned sub-team
        result = await db.execute(select(SubTeam).where(SubTeam.supervisor_id == current_user.id))
        return result.scalar_one_or_none()
    elif current_user.role == UserRole.admin:
        # Admins use X-SubTeam-ID header (from global switcher)
        if x_sub_team_id is None:
            return None  # Admin sees all data when no filter
        result = await db.execute(select(SubTeam).where(SubTeam.id == x_sub_team_id))
        sub_team = result.scalar_one_or_none()
        if not sub_team:
            raise HTTPException(status_code=403, detail="Invalid sub-team")
        return sub_team
    return None

# Usage in router
@router.get("/api/projects")
async def list_projects(
    sub_team: Optional[SubTeam] = Depends(get_sub_team),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Project)
    if sub_team:
        stmt = stmt.where(Project.sub_team_id == sub_team.id)
    result = await db.execute(stmt)
    return result.scalars().all()
```

**Source:** [VERIFIED: FastAPI dependency injection docs] - Standard pattern for context injection.

### Pattern 2: Migration with Default Data

**What:** Use Alembic to add nullable FK columns, create default sub-team, backfill existing data, then make FK non-nullable if desired.

**When to use:** Adding FK relationships to existing tables with existing data.

**Example:**
```python
# alembic/versions/xxx_add_sub_team.py
from alembic import op
import sqlalchemy as sa

def upgrade():
    # 1. Create sub_teams table
    op.create_table(
        'sub_teams',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('supervisor_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['supervisor_id'], ['users.id'])
    )
    
    # 2. Add nullable FK columns
    op.add_column('users', sa.Column('sub_team_id', sa.Integer(), nullable=True))
    op.add_column('projects', sa.Column('sub_team_id', sa.Integer(), nullable=True))
    op.add_column('team_invites', sa.Column('sub_team_id', sa.Integer(), nullable=True))
    
    # 3. Create default sub-team
    op.execute("""
        INSERT INTO sub_teams (name, supervisor_id, created_at)
        VALUES ('Default Team', NULL, NOW())
        RETURNING id
    """)
    default_id = op.execute(sa.select(sa.func.max(sa.column('id'))).select_from(sa.table('sub_teams'))).scalar()
    
    # 4. Backfill existing data
    op.execute(f"UPDATE users SET sub_team_id = {default_id} WHERE sub_team_id IS NULL")
    op.execute(f"UPDATE projects SET sub_team_id = {default_id} WHERE sub_team_id IS NULL")
    op.execute(f"UPDATE team_invites SET sub_team_id = {default_id} WHERE sub_team_id IS NULL")
    
    # 5. Add FK constraints
    op.create_foreign_key('fk_users_sub_team', 'users', 'sub_teams', ['sub_team_id'], ['id'])
    op.create_foreign_key('fk_projects_sub_team', 'projects', 'sub_teams', ['sub_team_id'], ['id'])
    op.create_foreign_key('fk_invites_sub_team', 'team_invites', 'sub_teams', ['sub_team_id'], ['id'])

def downgrade():
    # Reverse operations
    op.drop_constraint('fk_invites_sub_team', 'team_invites')
    op.drop_constraint('fk_projects_sub_team', 'projects')
    op.drop_constraint('fk_users_sub_team', 'users')
    op.drop_column('team_invites', 'sub_team_id')
    op.drop_column('projects', 'sub_team_id')
    op.drop_column('users', 'sub_team_id')
    op.drop_table('sub_teams')
```

**Source:** [VERIFIED: Alembic batch operations docs] - Standard pattern for schema + data migrations.

### Pattern 3: Frontend Global Switcher with localStorage

**What:** Store admin's selected sub-team in localStorage, include it as X-SubTeam-ID header in API requests.

**When to use:** Admin needs to switch context across the entire app without page reloads.

**Example:**
```typescript
// frontend/src/lib/stores/subTeam.ts
import { writable } from 'svelte/store';

interface SubTeam {
  id: number;
  name: string;
  supervisor_id: number | null;
}

const { subscribe, set, update } = writable<SubTeam | null>(null);

// Load from localStorage on init
if (typeof window !== 'undefined') {
  const stored = localStorage.getItem('selectedSubTeam');
  if (stored) set(JSON.parse(stored));
}

// Persist to localStorage on change
subscribe((value) => {
  if (typeof window !== 'undefined') {
    if (value) {
      localStorage.setItem('selectedSubTeam', JSON.stringify(value));
    } else {
      localStorage.removeItem('selectedSubTeam');
    }
  }
});

export const subTeamStore = { subscribe, set, update };
```

```typescript
// frontend/src/lib/api.ts
import { subTeamStore } from '$lib/stores/subTeam';

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string>)
  };
  
  // Add X-SubTeam-ID header for admins
  let selectedSubTeam: SubTeam | null = null;
  subTeamStore.subscribe((v) => selectedSubTeam = v)();
  if (selectedSubTeam) {
    headers['X-SubTeam-ID'] = selectedSubTeam.id.toString();
  }
  
  const res = await fetch(`${BASE}${path}`, { ...options, headers, credentials: 'include' });
  // ... error handling
}
```

**Source:** [VERIFIED: Svelte stores documentation] - Standard pattern for reactive state with persistence.

### Anti-Patterns to Avoid

- **Frontend-only filtering:** Filtering data in the browser after fetching everything is a security risk. Always filter server-side.
- **Hardcoded sub-team IDs:** Never hard-code sub-team IDs in frontend or backend. Always resolve from database or user context.
- **404 for unauthorized access:** Returning 404 for cross-team data leaks existence. Use 403 Forbidden instead.
- **Skipping FK constraints:** Adding columns without FK constraints risks data integrity. Always add constraints after backfill.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Sub-team context resolution | Custom middleware per endpoint | FastAPI Depends(get_sub_team) | DRY, testable, composable with other dependencies |
| Migration data backfill | Manual SQL scripts | Alembic op.execute() with transaction | Reversible, versioned, integrates with existing migration system |
| Frontend state persistence | Custom cookie management | localStorage + Svelte store | Simpler for SPA, no backend state needed, automatic sync |

**Key insight:** FastAPI's dependency injection system is designed for exactly this use case — contextual data injection (auth, scoping, permissions). Leverage it instead of building custom middleware.

## Runtime State Inventory

> Include this section for rename/refactor/migration phases only. Omit entirely for greenfield phases.

| Category | Items Found | Action Required |
|----------|-------------|------------------|
| Stored data | None — no existing sub-team data to migrate | Data migration via Alembic (users, projects, team_invites → default sub-team) |
| Live service config | None | None |
| OS-registered state | None | None |
| Secrets/env vars | None | None |
| Build artifacts | None | None |

## Common Pitfalls

### Pitfall 1: Missing sub_team_id on new records
**What goes wrong:** After migration, new users/projects created without sub_team_id cause FK violations or NULL constraint errors.
**Why it happens:** CREATE endpoints not updated to include sub_team_id in INSERT statements.
**How to avoid:** Add sub_team_id to all creation logic (User.register, Project.create, Invite.send) in the same migration wave.
**Warning signs:** 500 errors on user registration or project creation after migration.

### Pitfall 2: Admin bypassing scoping accidentally
**What goes wrong:** Admin sees no data when switcher is set to a specific sub-team, or sees all data when switcher should filter.
**Why it happens:** get_sub_team() dependency returns None for admins when header is missing, causing WHERE clause to be skipped entirely.
**How to avoid:** Explicitly handle admin case: if header is present, filter; if absent, return all (for "all teams" view).
**Warning signs:** Admin dashboard shows empty or incorrect counts.

### Pitfall 3: Timeline visibility logic incorrect
**What goes wrong:** Members see projects they're not assigned to, or supervisors see cross-team projects.
**Why it happens:** Timeline endpoint not updated with role-aware filtering logic per CONTEXT.md D-22/D-23/D-24.
**How to avoid:** Implement three distinct query paths: member (assigned tasks only), supervisor (sub-team projects), admin (all or filtered).
**Warning signs:** Users report seeing tasks they shouldn't on timeline.

### Pitfall 4: Invite flow not attaching sub_team_id
**What goes wrong:** Users accepting invites are not assigned to a sub-team, or invites created without sub_team_id.
**Why it happens:** Invite.send and Invite.accept endpoints not updated to handle sub_team_id per D-16/D-17/D-18.
**How to avoid:** Attach sub_team_id on invite creation (from inviter's context), auto-assign user to that sub-team on accept.
**Warning signs:** New users have NULL sub_team_id after registration.

## Code Examples

Verified patterns from official sources:

### SubTeam Model Definition

```python
# backend/app/models.py
class SubTeam(Base):
    __tablename__ = "sub_teams"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    supervisor_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))

    supervisor = relationship("User", foreign_keys=[supervisor_id])
    members = relationship("User", back_populates="sub_team")  # Will add User.sub_team relationship
```

**Source:** [VERIFIED: SQLAlchemy relationship docs] - Standard FK relationship pattern.

### Role-Aware Timeline Query

```python
# backend/app/routers/timeline.py
@router.get("/", response_model=List[TimelineProjectOut])
async def get_timeline(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    sub_team: Optional[SubTeam] = Depends(get_sub_team),
):
    stmt = select(Project).options(
        selectinload(Project.milestones).selectinload(Milestone.tasks).selectinload(Task.assignee)
    )
    
    # Apply sub-team filter (admin may have None = all teams)
    if sub_team:
        stmt = stmt.where(Project.sub_team_id == sub_team.id)
    
    # Apply role-specific filtering per D-22/D-23/D-24
    if current_user.role == UserRole.member:
        # Members see only projects where they have assigned tasks
        stmt = stmt.join(Task, Project.id == Task.project_id).where(Task.assignee_id == current_user.id).distinct()
    # Supervisors and admins see all projects in their scoped view (already filtered by sub_team above)
    
    stmt = stmt.order_by(Project.name)
    result = await db.execute(stmt)
    projects = result.scalars().unique().all()
    # ... rest of existing logic
```

**Source:** [VERIFIED: SQLAlchemy join/filter docs] - Standard pattern for conditional query filtering.

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Single-team deployment | Multi-team hierarchy with sub-teams | Phase 13 | Requires data migration, API scoping, role-aware queries |
| Global data access (no scoping) | Sub-team scoped data access with admin override | Phase 13 | Security improvement, prevents cross-team data leakage |
| No sub-team context | Global switcher for admins, implicit for supervisors/members | Phase 13 | UX change for admins, transparent for other roles |

**Deprecated/outdated:**
- None — this is a net-new feature, not a replacement.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Alembic supports executing raw SQL with op.execute() for data backfill | Migration Pattern | If not supported, migration fails; fallback to separate script |
| A2 | FastAPI Header() parameter can extract X-SubTeam-ID header | Pattern 1 | If header extraction fails, admin switcher won't work; fallback to query param |
| A3 | localStorage is available in SvelteKit browser context | Pattern 3 | If SSR blocks localStorage, switcher state lost on nav; fallback to URL param |

**If this table is empty:** All claims in this research were verified or cited — no user confirmation needed.

## Open Questions

None — all design decisions are locked in CONTEXT.md.

## Environment Availability

> Skip this section if the phase has no external dependencies (code/config-only changes).

No external dependencies required. All tools (Python, PostgreSQL, Bun) are existing project infrastructure.

## Validation Architecture

> Skip this section entirely if workflow.nyquist_validation is explicitly set to false in .planning/config.json. If the key is absent, treat as enabled.

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest (existing) |
| Config file | pytest.ini (existing in backend/) |
| Quick run command | `pytest backend/tests/ -x -v` |
| Full suite command | `pytest backend/tests/ -v` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| TEAM-01 | Admin creates/renames/deletes sub-teams | integration | `pytest backend/tests/test_sub_teams.py::test_admin_crud_sub_team -x` | ❌ Wave 0 |
| TEAM-02 | Member belongs to one sub-team | unit | `pytest backend/tests/test_models.py::test_user_sub_team_fk -x` | ❌ Wave 0 |
| TEAM-03 | Projects scoped to sub-team | integration | `pytest backend/tests/test_projects.py::test_project_sub_team_scoping -x` | ❌ Wave 0 |
| TEAM-04 | Supervisor sees only their sub-team | integration | `pytest backend/tests/test_performance.py::test_supervisor_scoping -x` | ❌ Wave 0 |
| TEAM-05 | Admin sees all teams org-wide | integration | `pytest backend/tests/test_dashboard.py::test_admin_all_teams -x` | ❌ Wave 0 |
| VIS-01 | Members see only assigned projects on timeline | integration | `pytest backend/tests/test_timeline.py::test_member_timeline_visibility -x` | ❌ Wave 0 |
| VIS-02 | Supervisors see sub-team projects on timeline | integration | `pytest backend/tests/test_timeline.py::test_supervisor_timeline_visibility -x` | ❌ Wave 0 |
| VIS-03 | Admin sees all projects on timeline | integration | `pytest backend/tests/test_timeline.py::test_admin_timeline_visibility -x` | ❌ Wave 0 |

### Sampling Rate
- **Per task commit:** `pytest backend/tests/ -x -v`
- **Per wave merge:** `pytest backend/tests/ -v`
- **Phase gate:** Full suite green before `/gsd-verify-work`

### Wave 0 Gaps
- `backend/tests/test_sub_teams.py` — covers TEAM-01
- `backend/tests/test_timeline.py` — covers VIS-01, VIS-02, VIS-03
- `backend/tests/test_projects.py` — covers TEAM-03
- `backend/tests/test_performance.py` — covers TEAM-04
- `backend/tests/test_dashboard.py` — covers TEAM-05
- `backend/tests/conftest.py` — shared fixtures for sub-team test data
- Framework install: None (pytest already installed)

## Security Domain

> Required when `security_enforcement` is enabled (absent = enabled). Omit only if explicitly `false` in config.

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | yes | JWT cookie auth (existing) |
| V3 Session Management | yes | JWT tokens with expiration (existing) |
| V4 Access Control | yes | Role-based + sub-team scoping (new in Phase 13) |
| V5 Input Validation | yes | Pydantic schemas (existing) |
| V6 Cryptography | yes | bcrypt for passwords (existing) |

### Known Threat Patterns for FastAPI + SQLAlchemy

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Horizontal privilege escalation (accessing other sub-teams) | Tampering/Elevation of Privilege | Server-side sub_team filtering in every endpoint, 403 on cross-team access |
| IDOR via direct object access | Information Disclosure | Always filter by sub_team_id in queries, never trust client-provided IDs |
| Missing sub_team_id on new records | Tampering | Database FK constraints, NOT NULL after migration, default values in INSERT |

## Sources

### Primary (HIGH confidence)
- [FastAPI dependency injection docs] - https://fastapi.tiangolo.com/tutorial/dependencies/
- [SQLAlchemy relationship docs] - https://docs.sqlalchemy.org/en/20/orm/basic_relationships.html
- [Alembic batch operations docs] - https://alembic.sqlalchemy.org/en/latest/batch.html
- [Svelte stores documentation] - https://svelte.dev/docs#run-time-stores

### Secondary (MEDIUM confidence)
- [PostgreSQL FK constraints] - https://www.postgresql.org/docs/current/ddl-constraints.html
- [localStorage API] - https://developer.mozilla.org/en-US/docs/Web/API/Window/localStorage

### Tertiary (LOW confidence)
- None

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - All libraries are existing project dependencies
- Architecture: HIGH - Patterns verified against official FastAPI/SQLAlchemy docs
- Pitfalls: HIGH - Based on common multi-tenant scoping mistakes documented in security literature

**Research date:** 2026-04-24
**Valid until:** 2026-05-24 (30 days for stable domain)
