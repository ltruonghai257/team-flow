# Phase 23: Standup Updates - Research

**Researched:** 2026-04-28
**Domain:** FastAPI + SQLAlchemy async (JSONB), SvelteKit 5 (cursor pagination, inline edit/delete, collapsible form)
**Confidence:** HIGH — all claims derived from verified codebase inspection or official package metadata

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- **D-01:** Global default template (6 fields: Pending Tasks, Future Tasks, Blockers, Need Help From, Critical Timeline, Release Date) stored as a DB settings row — not hardcoded.
- **D-02:** Per-team overrides stored in `StandupTemplate` table (one row per sub-team); teams with no row inherit the global default.
- **D-03:** Existing posts are immutable — template changes only affect future posts; JSONB snapshot preserves original field labels and values.
- **D-04:** Posts displayed as cards, reverse-chronological (newest first). No grouping.
- **D-05:** Task snapshot collapsed by default; a toggle expands it inline.
- **D-06:** Cursor-based pagination, "Load more" button, default page size 20.
- **D-07:** Standup form lives on `/updates` page (above feed), not a separate `/updates/new` route.
- **D-08:** Snapshot captures ALL tasks assigned to the submitting member regardless of status.
- **D-09:** Snapshot fields per task: `id`, `title`, `status`, `priority`, `due_date` — no sprint or project name.
- **D-10:** Edit surfaces inline — the card's field rows are replaced by an edit form in-place.
- **D-11:** Edit updates only template field text. Task snapshot is NOT re-frozen on edit.
- **D-12:** Delete confirmation is inline: "Delete this post? / Yes, delete / Keep post" — no modal, no browser confirm.

### Claude's Discretion

- Exact table/column name for the global settings store (e.g., `standup_settings` vs `app_settings`)
- Exact page size for pagination (20 is a suggested default)
- Collapsible-by-default vs always-open form on /updates — Claude can decide based on SvelteKit patterns

### Deferred Ideas (OUT OF SCOPE)

None — discussion stayed within phase scope.
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| UPD-01 | Member fills out standup post using configured template fields | D-07 layout; StandupForm renders template fields as labeled textareas fetched from `/api/updates/template` |
| UPD-02 | Default template: Pending Tasks, Future Tasks, Blockers, Need Help From, Critical Timeline, Release Date | D-01 DB-stored default; seeded in Alembic migration or first-access logic |
| UPD-03 | Supervisor can customize template (add/remove/rename fields) | D-02 per-sub-team StandupTemplate row; supervisor-only UI section below form |
| UPD-04 | Standup post captures frozen snapshot of member's task statuses at submit time (JSONB) | Server-side task query at POST time; stored in `task_snapshot JSONB NOT NULL` |
| UPD-05 | Posts visible to all team members and supervisor in team feed | GET `/api/updates/` with sub-team scoping via existing `get_sub_team` dependency |
| UPD-06 | Team feed can be filtered by member and date | Query params `?author_id=&date=&cursor=`; fresh API fetch on filter change, cursor reset |
| UPD-07 | Member can edit their own standup post | PATCH `/api/updates/{id}` — only `field_values` updated; ownership check `post.author_id == current_user.id` |
| UPD-08 | Member can delete their own standup post | DELETE `/api/updates/{id}` — ownership check enforced; inline Yes/No confirmation |
</phase_requirements>

---

## Summary

Phase 23 introduces three new backend tables (`standup_posts`, `standup_templates`, one settings row for global default), a new router at `routers/updates.py`, and two new frontend files (route page + components). The most technically interesting element is the JSONB task snapshot: it must be built server-side at POST time from a `SELECT tasks WHERE assignee_id = current_user.id` query, then stored immutably. No live task queries at read time.

The frontend has four distinct interaction states per card (read / edit-inline / delete-confirm / submitting), all managed in Svelte component local state — no global store needed for individual card transitions. A single Svelte writable store (`updates.ts`) holds the feed list, cursor, and filter state. Cursor-based pagination appends to the list on "Load more"; filter changes reset the cursor and replace the list.

The supervisor template editor is the most schema-sensitive part: the `StandupTemplate` table needs a `fields` JSONB column storing an ordered array of field-name strings. The GET template endpoint merges: if a row exists for the user's sub-team use that, else fall back to the global default settings row.

**Primary recommendation:** Implement backend models + migration first, then router, then frontend — each independently testable. The backend is the critical path because JSONB snapshot semantics must be locked before the frontend can render cards correctly.

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Task snapshot capture (frozen) | API / Backend | — | Must run server-side at POST time; client must never construct the snapshot |
| Template storage and retrieval | API / Backend | — | DB-backed; global default fallback logic belongs in backend |
| Standup post CRUD | API / Backend | — | Auth, ownership checks, pagination, filtering |
| Feed rendering (cards, pagination) | Browser / Client (SvelteKit) | — | SPA mode; reverse-chron list with cursor state in store |
| Inline edit / delete UX | Browser / Client (SvelteKit) | — | Component local state; no server round-trip for UI transitions |
| Template field rendering (form) | Browser / Client (SvelteKit) | — | Dynamic textarea list from template API response |
| Sub-team scoping of feed | API / Backend | — | Reuses existing `get_sub_team` dependency; admin uses X-SubTeam-ID header |
| Author ownership enforcement | API / Backend | — | 403 on PATCH/DELETE if `post.author_id != current_user.id` |

---

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| SQLAlchemy async | 2.0.23 (installed) | ORM + JSONB column | Already installed; async engine in use [VERIFIED: codebase] |
| FastAPI | 0.111.1 (installed) | Router, Depends, HTTPException | All existing routers use it [VERIFIED: codebase] |
| Alembic | 1.13.1 (installed) | Schema migration | Project policy: schema changes via Alembic only [VERIFIED: STATE.md] |
| Pydantic v2 | installed | Request/response schemas | All schemas use `BaseModel`, `model_config = {"from_attributes": True}` [VERIFIED: codebase] |
| SvelteKit 5 | installed | Frontend route + components | Project standard [VERIFIED: package.json] |
| date-fns | ^3.6.0 (installed) | Timestamp formatting in cards | Already used in schedule page [VERIFIED: package.json + schedule page] |
| lucide-svelte | ^0.378.0 (installed) | Icons (MessageSquare, ChevronDown, etc.) | Project standard icon library [VERIFIED: package.json] |
| svelte-sonner | ^0.3.27 (installed) | Toast notifications | Used in layout.svelte for notification toasts [VERIFIED: codebase] |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| marked | to install | Markdown parsing (Phase 25 usage) | Install in Phase 23, first `{@html}` use in Phase 25 [VERIFIED: STATE.md] |
| dompurify + @types/dompurify | to install | XSS sanitization for future {@html} | Install alongside marked; always pair together [VERIFIED: STATE.md + UI-SPEC] |

**Installation (frontend):**
```bash
cd frontend && bun add marked dompurify && bun add -d @types/dompurify
```

**No new backend packages needed.** [VERIFIED: requirements.txt — apscheduler, sqlalchemy, alembic, pydantic all present]

---

## Architecture Patterns

### System Architecture Diagram

```
Browser (SvelteKit SPA)
  └── /updates +page.svelte
        ├── onMount → GET /api/updates/template  ──────────► updates.py router
        │                                                        └── query StandupTemplate (sub_team fallback)
        ├── onMount → GET /api/updates/?cursor=&author_id=&date=
        │                                                        └── query standup_posts (scoped, ordered)
        │                                                              └── returns {posts, next_cursor}
        │
        ├── StandupForm.svelte
        │     submit → POST /api/updates/
        │                 ├── SELECT tasks WHERE assignee_id = user.id  (snapshot build)
        │                 ├── INSERT standup_posts (field_values JSONB, task_snapshot JSONB)
        │                 └── returns StandupPostOut
        │
        ├── updates store (writable)
        │     ├── posts[]        ← prepend on submit, append on "Load more"
        │     ├── nextCursor     ← null when exhausted
        │     └── filters        ← {authorId, date} — reset cursor on change
        │
        └── StandupCard.svelte (for each post)
              ├── read state      → SnapshotPanel.svelte (expand/collapse)
              ├── edit state      → PATCH /api/updates/{id}  (field_values only)
              └── delete state    → DELETE /api/updates/{id}
```

### Recommended Project Structure

```
backend/app/
├── models/
│   └── updates.py          # StandupPost, StandupTemplate, StandupSettings
├── schemas/
│   └── updates.py          # StandupPostCreate, StandupPostOut, StandupPostUpdate,
│                           #   TemplateOut, TemplateUpdate, StandupSettingsOut
├── routers/
│   └── updates.py          # GET /template, PUT /template, GET /, POST /, PATCH /{id}, DELETE /{id}
└── api/
    └── main.py             # add: from app.routers import updates; app.include_router(updates.router)

frontend/src/
├── routes/
│   └── updates/
│       └── +page.svelte    # /updates page
└── lib/
    ├── apis/
    │   └── updates.ts      # API module
    ├── stores/
    │   └── updates.ts      # feed store (posts, cursor, filters)
    └── components/
        └── updates/
            ├── StandupForm.svelte
            ├── StandupCard.svelte
            └── SnapshotPanel.svelte
```

### Pattern 1: SQLAlchemy JSONB Column

**What:** Store template field_values (dict) and task_snapshot (list of dicts) as native PostgreSQL JSONB.
**When to use:** Any unstructured or variable-length structured data that must be stored immutably.

```python
# Source: verified via `python3 -c "import sqlalchemy.dialects.postgresql as pg; print('JSONB' in dir(pg))"` — confirmed present
from sqlalchemy.dialects.postgresql import JSONB
from app.db.database import Base
from sqlalchemy import Column, Integer, ForeignKey, DateTime
from datetime import datetime, timezone

class StandupPost(Base):
    __tablename__ = "standup_posts"

    id = Column(Integer, primary_key=True, index=True)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    sub_team_id = Column(Integer, ForeignKey("sub_teams.id"), nullable=False, index=True)
    field_values = Column(JSONB, nullable=False)        # {"Pending Tasks": "...", ...}
    task_snapshot = Column(JSONB, nullable=False)       # [{"id":1,"title":"...","status":"todo",...}]
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None), index=True)
    updated_at = Column(DateTime,
        default=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
        onupdate=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
    )
```

### Pattern 2: Cursor-Based Pagination (ID-based)

**What:** Use the last-seen post ID as the cursor; query `id < cursor` for the next page.
**When to use:** Reverse-chronological feeds where stable ordering by created_at + id is guaranteed.

```python
# Source: verified project pattern — schedules.py uses select().where().order_by() pattern [VERIFIED: codebase]
from sqlalchemy import select

async def list_posts(db, sub_team_id, author_id=None, date=None, cursor=None, limit=20):
    q = select(StandupPost).where(StandupPost.sub_team_id == sub_team_id)
    if author_id:
        q = q.where(StandupPost.author_id == author_id)
    if date:
        q = q.where(StandupPost.created_at >= date_start, StandupPost.created_at < date_end)
    if cursor:
        q = q.where(StandupPost.id < cursor)
    q = q.order_by(StandupPost.id.desc()).limit(limit + 1)
    result = await db.execute(q)
    rows = result.scalars().all()
    has_more = len(rows) > limit
    return rows[:limit], rows[limit].id if has_more else None
```

### Pattern 3: Task Snapshot Build (server-side, at POST time)

**What:** Query all tasks assigned to `current_user.id` and serialize the snapshot fields.
**When to use:** Any time a frozen point-in-time record of task state is needed.

```python
# Source: Task model verified in backend/app/models/work.py [VERIFIED: codebase]
from sqlalchemy import select
from app.models.work import Task

async def build_task_snapshot(db, user_id: int) -> list[dict]:
    result = await db.execute(
        select(Task).where(Task.assignee_id == user_id)
    )
    tasks = result.scalars().all()
    return [
        {
            "id": t.id,
            "title": t.title,
            "status": t.status.value if t.status else None,
            "priority": t.priority.value if t.priority else None,
            "due_date": t.due_date.isoformat() if t.due_date else None,
        }
        for t in tasks
    ]
```

### Pattern 4: Template Fallback Logic

**What:** Look up sub-team-specific template; fall back to global default settings row.
**When to use:** Per-team overrides with an org-wide default.

```python
# Source: D-01 and D-02 decisions in CONTEXT.md [VERIFIED: CONTEXT.md]
async def get_template_for_user(db, sub_team_id: int | None) -> list[str]:
    if sub_team_id:
        result = await db.execute(
            select(StandupTemplate).where(StandupTemplate.sub_team_id == sub_team_id)
        )
        template = result.scalar_one_or_none()
        if template:
            return template.fields  # JSONB list of field name strings

    # Fall back to global default
    result = await db.execute(select(StandupSettings).limit(1))
    settings = result.scalar_one_or_none()
    if settings:
        return settings.default_fields
    return ["Pending Tasks", "Future Tasks", "Blockers", "Need Help From", "Critical Timeline", "Release Date"]
```

### Pattern 5: Ownership Enforcement (403 pattern)

**What:** Raise 403 if the requesting user does not own the resource.
**When to use:** Any PATCH or DELETE on user-authored content.

```python
# Source: get_current_user pattern verified in auth.py [VERIFIED: codebase]
from fastapi import HTTPException

post = result.scalar_one_or_none()
if not post:
    raise HTTPException(status_code=404, detail="Post not found")
if post.author_id != current_user.id:
    raise HTTPException(status_code=403, detail="Cannot modify another member's post")
```

### Pattern 6: SvelteKit Inline Edit State (local component state)

**What:** Use a local boolean `editing` to switch between read and edit view within a single card component.
**When to use:** Inline edit with no navigation — card-level state only.

```svelte
<!-- Source: D-10 decision + UI-SPEC interaction contract [VERIFIED: 23-UI-SPEC.md] -->
<script lang="ts">
  let editing = false;
  let editValues: Record<string, string> = {};

  function startEdit() {
    editValues = { ...post.field_values };
    editing = true;
  }
  function discardEdit() { editing = false; }
  async function saveEdit() {
    // call PATCH, on success: update post in parent via dispatch or store update
    editing = false;
  }
</script>

{#if editing}
  <!-- edit form -->
{:else}
  <!-- read view -->
{/if}
```

### Anti-Patterns to Avoid

- **Live task query at render time:** Never SELECT tasks when rendering a standup card. The snapshot is immutable. Fetching live tasks defeats the purpose and makes historical standups incorrect.
- **Client-side task snapshot construction:** Never let the browser build the task snapshot. A user could manipulate it. Always build server-side at POST time.
- **Global template hardcoded in frontend:** The frontend must always fetch the template from `/api/updates/template` — never hardcode the 6 field names. Template can change at runtime.
- **Re-freezing snapshot on edit:** On PATCH, update only `field_values`. Never touch `task_snapshot`. (D-11)
- **Browser confirm() for delete:** Use the inline Yes/No pattern from D-12 and UI-SPEC. No `window.confirm()`.
- **Reloading page on filter change:** Filters trigger a fresh API call with cursor reset — not a page reload.
- **Using `{@html}` without DOMPurify:** Template field values are plain text in Phase 23. Render with `whitespace-pre-wrap`. The `{@html}` pattern is reserved for Phase 25.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| JSONB storage for snapshot | Custom serialization / separate snapshot_items table | `Column(JSONB)` from `sqlalchemy.dialects.postgresql` | Native type, indexed, queryable; SQLAlchemy handles serialization [VERIFIED: codebase confirms JSONB available] |
| Pagination | Offset-based `LIMIT/OFFSET` | Cursor-based `id < cursor` | Offset pagination is unstable when new posts arrive; cursor is stable for a reverse-chron feed [ASSUMED] |
| Toast notifications | Custom toast component | `toast` from `svelte-sonner` | Already installed and wired in layout.svelte [VERIFIED: codebase] |
| Icons | SVG strings inline | `lucide-svelte` tree-shaken imports | Already installed, tree-shaken, consistent stroke weight [VERIFIED: package.json] |
| Auth dependency | Cookie parsing in router | `Depends(get_current_user)` | Handles both cookie and bearer token; already tested [VERIFIED: auth.py] |
| Sub-team scoping | Custom X-SubTeam-ID parsing | `Depends(get_sub_team)` | Already implements member/supervisor/admin logic [VERIFIED: auth.py] |
| Timestamp formatting | Custom date formatter | `format()` from `date-fns` | Already installed; used in schedule page [VERIFIED: package.json + schedule/+page.svelte] |

**Key insight:** This phase requires zero new infrastructure. Every pattern (JSONB, async SQLAlchemy, cursor pagination, inline edit, toast, auth dependencies) has an existing reference in the codebase.

---

## Common Pitfalls

### Pitfall 1: Alembic Migration Missing Model Import

**What goes wrong:** `alembic revision --autogenerate` generates an empty migration (no tables created) even though models are defined.
**Why it happens:** `alembic/env.py` imports `app.models` (the aggregate `__init__.py`). If the new `updates.py` model file is not imported in `app/models/__init__.py`, `Base.metadata` does not include the new tables.
**How to avoid:** Add imports to `backend/app/models/__init__.py` for `StandupPost`, `StandupTemplate`, `StandupSettings` BEFORE running `alembic revision --autogenerate`.
**Warning signs:** Generated migration script has empty `upgrade()` body.

### Pitfall 2: JSONB Not Available on SQLite (local dev without PostgreSQL)

**What goes wrong:** `sqlalchemy.dialects.postgresql.JSONB` raises import errors or behaves unexpectedly on SQLite.
**Why it happens:** JSONB is a PostgreSQL-specific type. If the project's local dev uses SQLite (check `DATABASE_URL`), JSONB will silently fall back to a string column.
**How to avoid:** Use `sa.JSON` as a cross-dialect fallback if SQLite testing is needed, or use the PostgreSQL container for all testing. STATE.md watch-out #5 confirms PostgreSQL is expected.
**Warning signs:** Migration runs on SQLite without error, but JSONB queries return raw strings instead of dicts.

### Pitfall 3: Enum `.value` Missing on Snapshot Serialization

**What goes wrong:** `task_snapshot` stored with Enum objects (`TaskStatus.todo`) instead of string values (`"todo"`), causing JSON serialization errors.
**Why it happens:** SQLAlchemy Enum columns return Python Enum instances, not strings. `json.dumps()` cannot serialize Enum instances.
**How to avoid:** In `build_task_snapshot()`, always access `.value`: `t.status.value`, `t.priority.value`.
**Warning signs:** `TypeError: Object of type TaskStatus is not JSON serializable` on POST.

### Pitfall 4: Cursor Reset on Filter Change (Frontend)

**What goes wrong:** Changing a filter appends new results to an existing page instead of replacing the feed.
**Why it happens:** `nextCursor` from the previous unfiltered fetch is passed to the filtered fetch.
**How to avoid:** Reset `nextCursor = null` and `posts = []` in the store whenever `filterAuthorId` or `filterDate` changes before calling the API.
**Warning signs:** Filtered results show up below unfiltered results instead of replacing them.

### Pitfall 5: `get_sub_team` Returns `None` for Admin Without X-SubTeam-ID

**What goes wrong:** Admin with no X-SubTeam-ID header gets no results (query filters to `sub_team_id IS NULL`) or throws a 500.
**Why it happens:** `get_sub_team` returns `None` for admin without header (see auth.py line ~116: "Admin sees all data when no filter").
**How to avoid:** In the feed list endpoint, when `sub_team` is `None` (admin with no filter), return all posts across all sub-teams (no sub_team_id filter). This is intentional admin behavior.
**Warning signs:** Admin user sees empty feed on `/updates` page.

### Pitfall 6: `alembic revision --autogenerate` Including JSONB Column Type Warning

**What goes wrong:** Autogenerate may emit a "Can't render column of type JSONB" warning and fall back to `sa.JSON`.
**Why it happens:** Some Alembic versions require explicit type rendering for PostgreSQL-specific types.
**How to avoid:** In the migration script, import from `sqlalchemy.dialects.postgresql import JSONB` explicitly and use it in `op.create_table()` rather than relying on autogenerate output verbatim. Review autogenerated migration before committing.
**Warning signs:** Migration creates a `JSON` column instead of `JSONB`.

### Pitfall 7: Router Not Registered in `app/api/main.py`

**What goes wrong:** All endpoints return 404 even though the router file is correct.
**Why it happens:** `create_app()` in `backend/app/api/main.py` has an explicit list of `application.include_router(...)` calls. New routers must be added here.
**How to avoid:** Add `from app.routers import updates` and `application.include_router(updates.router)` to `app/api/main.py`. [VERIFIED: main.py pattern]

---

## Code Examples

### Alembic Migration Template (JSONB tables)

```python
# Source: pattern from c2d3e4f5a6b7_add_sprint_release_reminders.py [VERIFIED: codebase]
from sqlalchemy.dialects.postgresql import JSONB
import sqlalchemy as sa
from alembic import op

def upgrade() -> None:
    op.create_table(
        "standup_posts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("author_id", sa.Integer(), nullable=False),
        sa.Column("sub_team_id", sa.Integer(), nullable=False),
        sa.Column("field_values", JSONB(), nullable=False),
        sa.Column("task_snapshot", JSONB(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["author_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["sub_team_id"], ["sub_teams.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_standup_posts_id", "standup_posts", ["id"])
    op.create_index("ix_standup_posts_author_id", "standup_posts", ["author_id"])
    op.create_index("ix_standup_posts_sub_team_id", "standup_posts", ["sub_team_id"])
    op.create_index("ix_standup_posts_created_at", "standup_posts", ["created_at"])
```

### Frontend API Module Pattern

```typescript
// Source: pattern from frontend/src/lib/apis/tasks.ts [VERIFIED: codebase]
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

### Svelte Store for Feed (cursor + filter state)

```typescript
// Source: pattern from frontend/src/lib/stores/auth.ts [VERIFIED: codebase]
import { writable } from 'svelte/store';

export interface StandupPost { /* ... */ }

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

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Offset-based pagination | Cursor-based (id < cursor) | Decision D-06 | Stable under concurrent writes — no missed/duplicate posts when feed is active |
| Separate edit route (`/updates/{id}/edit`) | Inline edit on card | Decision D-10 | Fewer page navigations; card context preserved during edit |
| Modal for delete confirmation | Inline Yes/No on card | Decision D-12 | No focus trap; keeps card fully visible |

**No deprecated patterns identified for this phase.**

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | ID-based cursor (id < cursor) is stable enough for this feed size | Architecture Patterns (Pattern 2) | If IDs are not monotonically increasing under concurrent inserts (e.g., sequence gaps), cursor may skip posts. In practice PostgreSQL serial sequences with async inserts make this negligible for team-scale traffic. |
| A2 | `StandupSettings` (global default) stores one canonical row; first-access logic seeds it if absent | Architecture Patterns (Pattern 4) | If the seeding logic is omitted, GET /template returns the hardcoded Python fallback list — functional but not DB-driven. Alternative: seed in Alembic migration `data migration` block. |

---

## Open Questions

1. **Global settings table name**
   - What we know: D-01 says "stored as a row in a DB settings table"; CONTEXT.md says "Claude's Discretion" owns the name.
   - What's unclear: Whether to create a new `standup_settings` table (single-row) or a generic `app_settings` key-value table.
   - Recommendation: Use `standup_settings` — a dedicated single-row table is clearer and avoids premature generalization. One row, seeded in migration.

2. **Sub-team scoping for StandupPost visibility (UPD-05)**
   - What we know: `get_sub_team` returns the sub-team for member/supervisor; returns `None` for admin without X-SubTeam-ID.
   - What's unclear: Should an admin with no sub-team filter see ALL posts org-wide, or only their own?
   - Recommendation: Admin with no X-SubTeam-ID header sees all posts (no sub_team_id filter). This matches existing behavior for tasks and schedules [VERIFIED: get_sub_team in auth.py].

---

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python 3 | Backend | Yes | 3.10.11 | — |
| Node.js | Frontend build | Yes | 22.16.0 | — |
| Bun | Frontend package management | Yes | 1.3.8 | — |
| SQLAlchemy JSONB dialect | JSONB columns | Yes | 2.0.23 | — |
| Alembic | Schema migration | Yes | 1.13.1 | — |
| FastAPI | Router | Yes | 0.111.1 | — |
| PostgreSQL | Runtime DB (JSONB requires it) | Not verified locally | — | SQLite silently degrades JSONB to JSON string — test against Postgres container |

**Missing dependencies with no fallback:**
- PostgreSQL (JSONB): Not verified as running locally, but required for correct JSONB behavior. Plan should include a note to test migrations against the Postgres container.

**Missing dependencies with fallback:**
- None

---

## Validation Architecture

> `workflow.nyquist_validation` key is absent from config.json — treated as enabled.

### Test Framework

| Property | Value |
|----------|-------|
| Framework | No automated test framework detected in project |
| Config file | None found |
| Quick run command | N/A — no test runner configured |
| Full suite command | N/A |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| UPD-04 | POST /updates/ returns task_snapshot that does not change after task update | integration | manual — no test runner | ❌ Wave 0 |
| UPD-07 | PATCH /updates/{id} by non-author returns 403 | integration | manual — no test runner | ❌ Wave 0 |
| UPD-08 | DELETE /updates/{id} by non-author returns 403 | integration | manual — no test runner | ❌ Wave 0 |
| UPD-06 | GET /updates/?author_id=X returns only that author's posts | integration | manual — no test runner | ❌ Wave 0 |

### Sampling Rate

No automated test runner is present in the project. Validation for this phase is **manual smoke testing** against a running instance.

### Wave 0 Gaps

No test infrastructure exists. The plan should include a Wave 0 task for manual verification steps documented in the plan itself (curl commands or browser walkthrough), not a new test framework (out of scope per CLAUDE.md simplicity rule).

*(No test framework detected — existing project has no pytest.ini, jest.config, or vitest.config. Out of scope to introduce one.)*

---

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | Yes | `Depends(get_current_user)` — all /updates endpoints [VERIFIED: auth.py] |
| V3 Session Management | No | Handled at application level; no new session logic |
| V4 Access Control | Yes | `post.author_id != current_user.id` → 403 on PATCH/DELETE [ownership enforcement] |
| V5 Input Validation | Yes | Pydantic schemas validate all request bodies; template field names should have max length |
| V6 Cryptography | No | No new crypto; existing JWT auth handles this |

### Known Threat Patterns for This Stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Horizontal privilege escalation (editing another user's post) | Tampering | Ownership check: `post.author_id != current_user.id` → 403 |
| Stored XSS via template field values | Tampering | Phase 23 renders fields as `whitespace-pre-wrap` plain text — no `{@html}`. XSS surface is zero for Phase 23. |
| Mass assignment via PATCH (snapshot override) | Tampering | `StandupPostUpdate` Pydantic schema must include ONLY `field_values` — exclude `task_snapshot`, `author_id`, `sub_team_id` from update schema |
| Feed scraping across sub-teams | Information Disclosure | Sub-team scoping via `get_sub_team` dependency ensures members only see their team's posts |

**Critical:** The PATCH schema (`StandupPostUpdate`) must explicitly exclude `task_snapshot` from accepted fields. If task_snapshot were patchable, a user could retroactively falsify their historical standup. [ASSUMED — standard Pydantic practice but worth explicit attention]

---

## Sources

### Primary (HIGH confidence)

- `backend/app/models/work.py` — Task model fields (id, title, status, priority, due_date, assignee_id) verified
- `backend/app/models/notifications.py` — EventNotification and reminder model patterns
- `backend/app/routers/schedules.py` — Router pattern (async, Depends, select, scalar_one_or_none)
- `backend/app/utils/auth.py` — `get_current_user`, `require_supervisor`, `get_sub_team` dependencies verified
- `backend/app/api/main.py` — Router registration pattern verified
- `backend/app/models/__init__.py` — Aggregate import pattern for Alembic env.py
- `backend/app/db/database.py` — `get_db` async session dependency pattern
- `backend/app/schemas/work.py` — Pydantic v2 schema pattern (`model_config = {"from_attributes": True}`)
- `backend/alembic/versions/c2d3e4f5a6b7_add_sprint_release_reminders.py` — Alembic migration pattern
- `frontend/src/lib/apis/tasks.ts` — API module pattern
- `frontend/src/lib/apis/request.ts` — `request()` helper, `X-SubTeam-ID` header injection
- `frontend/src/lib/stores/auth.ts` — Store pattern; `isSupervisor` derived store confirmed
- `frontend/src/routes/+layout.svelte` — `navItems` array structure; toast and notification wiring
- `frontend/src/app.css` — `.btn-primary`, `.btn-secondary`, `.btn-danger`, `.card`, `.input`, `.label`, `.badge` utility classes
- `frontend/package.json` — Confirmed: date-fns, lucide-svelte, svelte-sonner, SvelteKit 5, Svelte 5, Tailwind 3 installed; marked and dompurify NOT yet installed
- `.planning/phases/23-standup-updates/23-UI-SPEC.md` — Full UI interaction contract, copywriting, component inventory
- `.planning/phases/23-standup-updates/23-CONTEXT.md` — All locked decisions D-01 through D-12
- `python3 -c "import sqlalchemy.dialects.postgresql as pg; ..."` — JSONB confirmed available

### Secondary (MEDIUM confidence)

- STATE.md — Architecture decisions for v2.2 (JSONB snapshot, zero new packages, Alembic-only migrations, marked+DOMPurify install timing)

### Tertiary (LOW confidence)

- None — all claims verified against codebase or project docs.

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — all packages verified via package.json and pip inspect
- Architecture: HIGH — models, routers, auth patterns all verified from codebase
- Pitfalls: HIGH — derived from direct inspection of migration pattern, model imports, and auth.py get_sub_team behavior
- UI patterns: HIGH — UI-SPEC.md is the authoritative contract; verified against app.css utility classes

**Research date:** 2026-04-28
**Valid until:** 2026-05-28 (stable stack, no fast-moving dependencies)
