# Phase 4: Team Timeline View - Research

**Researched:** 2026-04-23
**Domain:** Svelte 5 Gantt chart integration, FastAPI timeline API, SvelteKit routing
**Confidence:** HIGH (codebase patterns), MEDIUM (svelte-gantt compatibility), HIGH (backend patterns)

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **D-01:** Use **svelte-gantt** — purpose-built Svelte Gantt library with native drag-and-drop support. Not LayerChart. New dependency to add.
- **D-02:** Drag-to-reschedule is **enabled** — dragging a task bar updates `due_date` via `PATCH /api/tasks/{id}`.
- **D-03:** Timeline supports **two grouping modes** with a toggle: Project view (Project → Milestone → Tasks) and Member view (each member's tasks across projects).
- **D-04:** Tasks without `milestone_id` appear under a **"No Milestone"** catch-all row per project — not hidden.
- **D-05:** Tasks are color-coded using `project.color` (existing field on `Project` model).
- **D-06:** Clicking a task bar opens a **modal dialog** with the full task edit form. Saves via `PATCH /api/tasks/{id}`.
- **D-07:** After successful edit or drag, the timeline re-fetches/updates in place without full page reload.
- **D-08:** Default view: **"fit to data"** — auto-spans from earliest `start_date`/`created_at` to latest `due_date`.
- **D-09:** Range selector: **Week / Month / Custom**. Custom uses a Svelte date picker (researcher to confirm best option for SvelteKit 5).
- **D-10:** Tasks with **no `due_date`** shown as a short **dashed bar at today's date position** — not hidden.
- **D-11:** New endpoint `GET /api/timeline` returns all projects with milestones and tasks in a single response.
- **D-12:** Endpoint uses existing `get_current_user` dependency (all roles, no supervisor restriction).

### Claude's Discretion
- Overdue task visual treatment (red outline vs. red fill)
- Milestone marker shape on the time axis
- Assignee avatar display on task bars (initials circle)
- Member view row ordering (alphabetical by name is fine)

### Deferred Ideas (OUT OF SCOPE)
None — discussion stayed within phase scope.
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| REQ-03 | Team Timeline / Project Overview — `/timeline` route, Gantt view, color by project, time range selector, task bars with assignee, overdue distinct, milestone markers, click-to-edit | svelte-gantt integration patterns, PATCH task endpoint, data model analysis below |
</phase_requirements>

---

## Summary

Phase 4 builds a `/timeline` Gantt chart route. The core challenge is Svelte 5 compatibility: the user-selected `svelte-gantt` (ANovokmet) declares `svelte@^4.0.0` as a peer dependency and **does not officially support Svelte 5** — a peer conflict exists (verified via GitHub issue #253, Feb 2025). The library can be installed with `--legacy-peer-deps` in npm or without flags in yarn (which ignores peer conflicts by default), and the Svelte 5 compatibility layer means Svelte 4-style components often work at runtime, but with caveats around component instantiation API changes.

The backend is straightforward: one new endpoint (`GET /api/timeline`) following the established FastAPI router pattern with `selectinload` for relationships. The frontend follows the established SvelteKit routing + TailwindCSS dark theme pattern with `svelte-sonner` for toast notifications (already in `package.json`).

**Primary recommendation:** Install `svelte-gantt` via yarn (which skips the peer dep check), test runtime compatibility. If runtime issues occur, fall back to the `@svar-ui/svelte-gantt` (MIT-licensed, Svelte 5 native) with similar drag-drop API. Decision documented as an open question for the executor.

**Alternative on standby:** `@svar-ui/svelte-gantt` (free MIT tier) is Svelte 5 native with drag-drop support. API differs from `svelte-gantt` but documentation is clear.

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Timeline data fetching | API / Backend | — | Aggregates projects + milestones + tasks in one query |
| Gantt rendering | Browser / Client | — | svelte-gantt is a client-side component |
| Drag-to-reschedule | Browser / Client → API | — | Client fires PATCH; API persists |
| Click-to-edit modal | Browser / Client → API | — | Client renders form; API saves |
| Row grouping (project/member toggle) | Browser / Client | — | Pure UI transformation of fetched data |
| Date range selector | Browser / Client | — | Controls gantt time window only |
| Auth guard | Frontend Server (SSR) | Browser | SvelteKit layout auth check |

---

## Standard Stack

### Core — Frontend
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| svelte-gantt | 4.5.0 [VERIFIED: npm registry search] | Gantt chart with drag-drop | User-locked D-01 |
| svelte | ^5.0.0 | Already in devDependencies | Project stack |
| date-fns | ^3.6.0 | Date math for range calc | Already in package.json |
| lucide-svelte | ^0.378.0 | Toolbar icons | Already in package.json |
| svelte-sonner | ^0.3.27 | Toast notifications | Already in package.json |

### Core — Backend
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| FastAPI | existing | New timeline router | Project stack |
| SQLAlchemy asyncpg | existing | Eager-load relationships | Project pattern |
| Pydantic | existing | `TimelineOut` schema | Project pattern |

### Installation

```bash
# yarn (project uses yarn — ignores peer dep conflict automatically)
yarn add svelte-gantt

# If runtime issues with Svelte 5, fallback:
yarn add @svar-ui/svelte-gantt
```

**⚠ Peer dep conflict:** `svelte-gantt@4.5.0` declares `peerDependencies: { svelte: "^4.0.0" }`. yarn 1.x installs without error (peer conflicts are warnings only). npm requires `--legacy-peer-deps`. The project uses yarn (`"packageManager": "yarn@1.22.22"` in package.json) — no flag needed. [VERIFIED: GitHub issue #253, ANovokmet/svelte-gantt, Feb 2025]

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| svelte-gantt | @svar-ui/svelte-gantt | SVAR is Svelte 5 native (MIT free tier), but different API — wraps in `<WillowDark>` theme tag, not Tailwind-compatible out of box |
| svelte-gantt | Custom canvas/SVG | Full control but high complexity — not worth it |
| native `<input type="date">` | svelte-datepicker | UI-SPEC already locked: use native `<input type="date">` (D-09 resolved in UI-SPEC) |

---

## Architecture Patterns

### System Architecture Diagram

```
User browser
   │
   ├── /timeline route (frontend/src/routes/timeline/+page.svelte)
   │        │
   │        ├── onMount: GET /api/timeline → timelineData
   │        │
   │        ├── TimelineToolbar (view toggle + range selector)
   │        │        └── changes: viewMode, rangeStart, rangeEnd
   │        │
   │        └── TimelineGantt (svelte-gantt wrapper)
   │                 ├── renders rows + task bars from timelineData
   │                 ├── drag event → PATCH /api/tasks/{id} (due_date)
   │                 └── click event → TaskEditModal → PATCH /api/tasks/{id}
   │
FastAPI /api/timeline (GET)
   └── selectinload(Project.milestones → Milestone.tasks → Task.assignee)
       └── returns JSON: [{project, milestones:[{milestone, tasks:[]}], unassigned_tasks:[]}]
```

### Recommended Project Structure

```
frontend/src/
├── routes/
│   └── timeline/
│       └── +page.svelte          # route entry, data loading
├── lib/
│   └── components/
│       └── timeline/
│           ├── TimelineToolbar.svelte
│           ├── TimelineGantt.svelte
│           ├── TimelineTaskBar.svelte
│           ├── TimelineMilestoneMarker.svelte
│           └── TaskEditModal.svelte

backend/app/
├── routers/
│   └── timeline.py               # new router, prefix /api/timeline
└── schemas.py                    # add TimelineTaskOut, TimelineMilestoneOut,
                                  #     TimelineProjectOut, TimelineResponse
```

### Pattern 1: svelte-gantt Data Format

svelte-gantt expects rows and tasks arrays. For project view:

```javascript
// Source: [ASSUMED — svelte-gantt docs, cross-checked against GitHub README]
// Rows = grouping buckets (project, milestone, member)
const rows = [
  { id: 'project-1', label: 'Alpha Project', enableDragging: false },
  { id: 'milestone-1', label: 'Milestone 1', parent: 'project-1' },
  { id: 'no-milestone-1', label: 'No Milestone', parent: 'project-1' },
];

// Tasks = bar items
const tasks = [
  {
    id: 'task-42',
    resourceId: 'milestone-1',  // which row it belongs to
    label: 'Fix bug',
    from: new Date('2026-04-01'),  // start (svelte-gantt uses `from`/`to`)
    to: new Date('2026-04-10'),
    classes: 'task-bar',         // for custom styling
  }
];
```

**Key:** svelte-gantt uses `from`/`to` (not `start`/`end`) for Date objects. The backend returns ISO strings → frontend converts via `new Date(isoString)`.

### Pattern 2: Drag Event Handler

```javascript
// svelte-gantt fires 'change' event on drag complete
gantt.$on('change', ({ detail: { task } }) => {
  // task.to = new Date after drag
  await tasks.update(task.id, { due_date: task.to.toISOString() });
  toast.success(`Rescheduled to ${format(task.to, 'MMM d')}`);
});
```

[ASSUMED — based on svelte-gantt README event API; executor should verify against installed version]

### Pattern 3: Backend Timeline Endpoint

Follow the established FastAPI router pattern (same as `performance.py`):

```python
# backend/app/routers/timeline.py
from sqlalchemy.orm import selectinload

router = APIRouter(prefix="/api/timeline", tags=["timeline"])

@router.get("/", response_model=List[TimelineProjectOut])
async def get_timeline(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stmt = (
        select(Project)
        .options(
            selectinload(Project.milestones).selectinload(Milestone.tasks)
            .selectinload(Task.assignee)
        )
        .order_by(Project.name)
    )
    result = await db.execute(stmt)
    projects = result.scalars().unique().all()
    # ... build response with unassigned_tasks per project
    return build_timeline_response(projects)
```

[VERIFIED: SQLAlchemy selectinload chain pattern matches existing `performance.py` + `CONVENTIONS.md`]

### Pattern 4: Pydantic Timeline Schemas

```python
class TimelineTaskOut(BaseModel):
    id: int
    title: str
    status: TaskStatus
    priority: TaskPriority
    due_date: Optional[datetime]
    created_at: datetime
    milestone_id: Optional[int]
    project_id: Optional[int]
    assignee: Optional[UserOut] = None
    model_config = {"from_attributes": True}

class TimelineMilestoneOut(BaseModel):
    id: int
    title: str
    status: MilestoneStatus
    start_date: Optional[datetime]
    due_date: datetime
    tasks: List[TimelineTaskOut] = []
    model_config = {"from_attributes": True}

class TimelineProjectOut(BaseModel):
    id: int
    name: str
    color: str
    milestones: List[TimelineMilestoneOut] = []
    unassigned_tasks: List[TimelineTaskOut] = []
    model_config = {"from_attributes": True}
```

### Pattern 5: Nav Item Registration (layout.svelte)

The existing nav items follow this pattern in `+layout.svelte`:
```javascript
const navItems = [
  { href: '/', label: 'Dashboard', icon: LayoutDashboard },
  // ... existing items
  { href: '/timeline', label: 'Timeline', icon: GanttChartSquare }, // add this
];
```

[VERIFIED: pattern derived from ARCHITECTURE.md + CONTEXT.md canonical refs]

### Anti-Patterns to Avoid

- **Loading tasks in separate calls per project:** Use the single `GET /api/timeline` endpoint (D-11) — one request for all data.
- **Implementing drag with custom mouse events:** Use svelte-gantt's built-in drag event — don't hand-roll drag logic.
- **Filtering out tasks with no due_date:** Per D-10, render them as dashed bars at today's position — never hide.
- **Using Svelte 5 rune syntax inside svelte-gantt's slot props:** The library was built for Svelte 4; use `$props()` and Svelte 5 compatible syntax in wrapper components.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Gantt bar rendering | Custom SVG/Canvas timeline | svelte-gantt | Drag-drop, zoom, row headers are complex |
| Date range arithmetic | Custom date math | `date-fns` (already in package.json) | DST, month boundaries, edge cases |
| Toast feedback | Custom toast component | `svelte-sonner` (already in package.json) | Already project-standard |
| Modal overlay | Custom full-screen div | Follow existing modal pattern | CONTEXT.md specifies `fixed inset-0 bg-black/60 z-50` |
| `PATCH /api/tasks/{id}` | New patch endpoint | Use existing task router | Already exists and handles partial updates |

---

## Common Pitfalls

### Pitfall 1: svelte-gantt Svelte 5 Peer Conflict
**What goes wrong:** `npm install svelte-gantt` fails with ERESOLVE (peer requires svelte@^4).
**Why it happens:** svelte-gantt@4.5.0 hasn't updated peerDependencies for Svelte 5.
**How to avoid:** Project uses yarn 1.22 — yarn ignores peer conflict warnings and installs successfully. **Use `yarn add svelte-gantt`**, not npm.
**Warning signs:** If build fails with "Cannot find module 'svelte/internal'" — Svelte 5 changed internal APIs. Switch to `@svar-ui/svelte-gantt` (MIT free tier, Svelte 5 native).

### Pitfall 2: svelte-gantt `from`/`to` vs `start`/`end`
**What goes wrong:** Bars don't render; console shows NaN date errors.
**Why it happens:** svelte-gantt uses `from`/`to` Date props on task objects, not `start`/`end`. Backend returns ISO strings.
**How to avoid:** Always convert: `from: new Date(task.due_date ?? now)`, `to: new Date(task.due_date ?? now)`.

### Pitfall 3: SQLAlchemy Nested selectinload
**What goes wrong:** `MissingGreenlet` error or lazy loading error on `Project.milestones.tasks.assignee`.
**Why it happens:** Async SQLAlchemy requires explicit eager loading for nested relationships.
**How to avoid:** Chain selectinloads: `selectinload(Project.milestones).selectinload(Milestone.tasks).selectinload(Task.assignee)`. [VERIFIED: matches existing pattern in performance.py]

### Pitfall 4: Stale Timeline After Drag/Edit
**What goes wrong:** Timeline shows old data after task edit or drag.
**Why it happens:** svelte-gantt's row/task arrays are reactive but need to be reassigned (not mutated) for Svelte 5 reactivity.
**How to avoid:** After PATCH success, re-fetch full timeline (`await loadTimeline()`) or splice the updated task into the reactive array with `ganttTasks = ganttTasks.map(t => t.id === updated.id ? mapped(updated) : t)`.

### Pitfall 5: `unassigned_tasks` vs milestone-grouped tasks
**What goes wrong:** Tasks with `project_id` but no `milestone_id` disappear from view.
**Why it happens:** If backend only returns tasks via milestone relationships, project-scoped but milestone-less tasks are lost.
**How to avoid:** Backend must explicitly separate: `milestone.tasks` (those with milestone_id) and `unassigned_tasks` (tasks where `project_id = project.id AND milestone_id IS NULL`). This requires a separate query or post-processing on the fetched tasks. See D-04.

---

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| yarn | Package install | ✓ | 1.22.22 (package.json) | npm --legacy-peer-deps |
| svelte-gantt | Gantt chart | ✗ (not yet installed) | 4.5.0 | @svar-ui/svelte-gantt |
| date-fns | Date formatting | ✓ | ^3.6.0 (package.json) | — |
| svelte-sonner | Toasts | ✓ | ^0.3.27 (package.json) | — |
| lucide-svelte | Icons | ✓ | ^0.378.0 (package.json) | — |

**Missing dependencies with no fallback:** None blocking — all have clear install paths.

---

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | None detected (no pytest.ini, jest.config.*, vitest.config.* in project) |
| Config file | None — no existing test infrastructure |
| Quick run command | N/A — Wave 0 would need to create test scaffolding |
| Full suite command | N/A |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| REQ-03 | `/api/timeline` returns projects + milestones + tasks | Integration | `pytest tests/test_timeline.py -x` | ❌ Wave 0 |
| REQ-03 | Tasks with no `due_date` included in response | Integration | `pytest tests/test_timeline.py::test_unscheduled_task -x` | ❌ Wave 0 |
| REQ-03 | Tasks with no `milestone_id` in `unassigned_tasks` | Integration | `pytest tests/test_timeline.py::test_unassigned_task -x` | ❌ Wave 0 |

### Wave 0 Gaps
- [ ] `backend/tests/test_timeline.py` — covers REQ-03 API contract
- [ ] `backend/tests/conftest.py` — shared fixtures (may already exist; check before creating)
- [ ] Framework install: `pip install pytest pytest-asyncio httpx` (if not already in requirements.txt)

No frontend test infrastructure exists in this project — frontend verification is manual (checkpoint).

---

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | Yes | `get_current_user` dependency (existing) |
| V3 Session Management | No | Cookie auth already handled in Phase 1 |
| V4 Access Control | Yes | All roles allowed (D-12) — no privilege escalation risk. PATCH task endpoint already enforces user auth. |
| V5 Input Validation | Yes | `due_date` from drag must be validated in PATCH handler (existing TaskUpdate schema handles this) |
| V6 Cryptography | No | No new crypto |

### Known Threat Patterns

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Unauthorized task date modification via drag | Tampering | PATCH /api/tasks/{id} already enforces `get_current_user`; executor should verify task ownership check exists |
| Timeline data exposure to unauthenticated users | Information Disclosure | `get_current_user` dep on GET /api/timeline (D-12 specifies this) |
| XSS via task title in Gantt bar | Tampering | svelte-gantt renders via DOM text, not innerHTML — low risk; verify label rendering is text-based |

---

## Open Questions

1. **svelte-gantt Svelte 5 runtime compatibility**
   - What we know: svelte-gantt@4.5.0 installs via yarn (peer warning only), Svelte 5 has a compatibility layer for Svelte 4 components
   - What's unclear: Whether svelte-gantt's internal component instantiation (`new SvelteGantt({...})`) works with Svelte 5's changed component API
   - Recommendation: **Executor tries yarn add + test render first.** If runtime errors occur (common symptom: "Cannot find module 'svelte/internal'" or blank gantt), switch to `@svar-ui/svelte-gantt` with note that D-01 specified svelte-gantt but Svelte 5 incompatibility forced the fallback. The PLAN.md should include a decision checkpoint after install.

2. **Tasks belonging to milestones from OTHER projects**
   - What we know: `Task.milestone_id` can reference any milestone; the backend query joins via `Project.milestones.tasks`
   - What's unclear: Are there tasks where `task.project_id != task.milestone.project_id`? (data integrity issue)
   - Recommendation: Backend builds response by `project_id` on tasks, not via milestone chain — avoids orphan task issues.

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | svelte-gantt uses `from`/`to` Date props on task objects | Architecture Patterns | Bars won't render; check installed version's type definitions |
| A2 | svelte-gantt fires `'change'` event on drag complete | Architecture Patterns | Drag won't persist; check svelte-gantt docs for actual event name |
| A3 | yarn 1.22 ignores peer dep conflicts silently | Standard Stack | Install may fail; use `--legacy-peer-deps` as fallback |

---

## Sources

### Primary (HIGH confidence)
- `backend/app/models.py` — verified Task, Milestone, Project fields
- `backend/app/routers/performance.py` — verified selectinload pattern + router structure
- `frontend/package.json` — verified existing dependencies (date-fns, svelte-sonner, lucide-svelte, yarn)
- `backend/app/main.py` — verified router registration pattern
- `.planning/codebase/CONVENTIONS.md` — verified router/schema/component patterns
- `.planning/phases/04-team-timeline-view/04-UI-SPEC.md` — verified component names, date picker decision (native input)

### Secondary (MEDIUM confidence)
- GitHub ANovokmet/svelte-gantt issue #253 — Svelte 5 peer dep conflict confirmed [CITED]
- GitHub svar-widgets/gantt README — SVAR Svelte 5 native option confirmed [CITED]
- SVAR pricing page — MIT free tier confirmed [CITED]

### Tertiary (LOW confidence)
- svelte-gantt API (`from`/`to` prop names, `'change'` event) — [ASSUMED] based on README pattern; executor must verify against installed source

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — verified from codebase + GitHub
- Architecture: HIGH (backend), MEDIUM (svelte-gantt API specifics)
- Pitfalls: HIGH — peer dep confirmed from GitHub issue; others from codebase analysis

**Research date:** 2026-04-23
**Valid until:** 2026-05-23 (svelte-gantt Svelte 5 support may change)

## RESEARCH COMPLETE

**Phase:** 4 - Team Timeline View
**Confidence:** MEDIUM-HIGH

### Key Findings
- `svelte-gantt@4.5.0` has Svelte 5 peer dep conflict but installs via yarn (project package manager) without flags — runtime test needed at execution time
- `@svar-ui/svelte-gantt` is the MIT Svelte 5 native fallback if runtime issues occur
- Backend endpoint is straightforward: one `selectinload` chain, follows `performance.py` pattern exactly
- UI-SPEC already resolved the date picker question: native `<input type="date">` elements
- All 5 task model fields needed for timeline are confirmed present in `models.py`
- `project.color` field confirmed on `Project` model (default `#6366f1`)

### File Created
`.planning/phases/04-team-timeline-view/04-RESEARCH.md`

### Confidence Assessment
| Area | Level | Reason |
|------|-------|--------|
| Standard Stack | HIGH | Verified from package.json + GitHub issues |
| Architecture | HIGH | Backend pattern from existing code; frontend from CONTEXT.md |
| svelte-gantt API | MEDIUM | Core props assumed from README; executor verifies at install |
| Pitfalls | HIGH | Peer conflict confirmed; others from SQLAlchemy analysis |

### Open Questions
- svelte-gantt Svelte 5 runtime compatibility (peer issue confirmed, runtime unknown)
- Task–project cross-ownership edge case in backend query

### Ready for Planning
Research complete. Planner can now create PLAN.md files.
