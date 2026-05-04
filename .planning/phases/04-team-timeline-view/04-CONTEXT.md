# Phase 4: Team Timeline View - Context

**Gathered:** 2026-04-23
**Status:** Ready for planning

<domain>
## Phase Boundary

Build a `/timeline` route with a Gantt-style horizontal timeline of milestones and tasks across all projects. Accessible to all roles. Supports project-view/member-view toggle, drag-to-reschedule, and click-to-edit via modal.

</domain>

<decisions>
## Implementation Decisions

### Gantt Library
- **D-01:** Use **svelte-gantt** — purpose-built Svelte Gantt library with native drag-and-drop support. Not LayerChart (that's Phase 3 for bar/trend charts). New dependency to add.
- **D-02:** Drag-to-reschedule is **enabled** — dragging a task bar updates `due_date` via `PATCH /api/tasks/{id}`. Leverages svelte-gantt's built-in drag support.

### Data Grouping & Hierarchy
- **D-03:** Timeline supports **two grouping modes** with a toggle:
  - **Project view**: rows grouped by Project → Milestone → Tasks (milestone markers on axis)
  - **Member view**: each team member gets a row showing their tasks across all projects
- **D-04:** In project view, tasks without a `milestone_id` appear under a **"No Milestone"** catch-all row per project — not hidden.
- **D-05:** Tasks are color-coded using `project.color` (existing field on `Project` model).

### Interactivity & Click Behavior
- **D-06:** Clicking a task bar opens a **modal dialog** with the full task edit form (title, status, priority, due date, assignee). Saves via `PATCH /api/tasks/{id}`.
- **D-07:** After a successful edit or drag, the timeline re-fetches/updates in place without full page reload.

### Time Range & Navigation
- **D-08:** Default view on open: **"fit to data"** — automatically spans from the earliest `start_date` (or `created_at` as fallback) to the latest `due_date` across all active milestones/tasks.
- **D-09:** Range selector buttons: **Week** / **Month** / **Custom**. Custom range uses a **Svelte date picker** (e.g. `svelte-datepicker` or equivalent — researcher to confirm best option compatible with SvelteKit 5).
- **D-10:** Tasks with **no `due_date`** are shown as a short **dashed bar at today's date position** to flag they exist but are unscheduled — not hidden.

### Backend API
- **D-11:** New endpoint `GET /api/timeline` returns all projects with their milestones and tasks in a single response. Structure: `[{ project, milestones: [{ milestone, tasks: [] }], unassigned_tasks: [] }]`.
- **D-12:** Endpoint respects the existing `get_current_user` dependency (all roles can access, no supervisor-only restriction).

### Claude's Discretion
- Overdue milestone/task visual treatment (red outline vs. red fill) — Claude decides based on svelte-gantt's styling API
- Milestone marker shape on the time axis (diamond, triangle, vertical line) — Claude picks
- Assignee avatar display on task bars (initials circle — follow existing pattern from Phase 3)
- Member view row ordering (alphabetical by name is fine)

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Requirements
- `.planning/REQUIREMENTS.md` § REQ-03 — Team Timeline / Project Overview (acceptance criteria)

### Data Models
- `backend/app/models.py` — `Milestone` (start_date, due_date, status), `Task` (due_date, assignee_id, status, priority), `Project` (color), `User`

### Frontend Patterns
- `frontend/src/routes/+layout.svelte` — nav items pattern, `isSupervisor` store import, auth guard
- `frontend/src/lib/stores/auth.ts` — `authStore`, `isSupervisor` derived store
- `frontend/src/lib/api.ts` — API client pattern; add `timeline` namespace here
- `frontend/src/lib/components/tasks/KanbanBoard.svelte` — existing component for modal/edit pattern reference

### Phase 3 Context (established patterns)
- `.planning/phases/03-supervisor-performance-dashboard/03-CONTEXT.md` — LayerChart for charts, `/performance` route guard pattern, component directory convention (`frontend/src/lib/components/{domain}/`)

### Backend Conventions
- `.planning/codebase/CONVENTIONS.md` — router pattern, `{Domain}Out` schema pattern, `get_db` session, `selectinload` for relationships

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `Project.color` field (String, default `#6366f1`) — already on model, use for bar color-coding
- `Milestone.start_date` + `Milestone.due_date` — duration available for milestone bars
- `Task.due_date`, `Task.assignee_id`, `Task.status`, `Task.priority` — all available for timeline rendering
- `isSupervisor` derived store in `auth.ts` — available for any supervisor-only UI elements
- `lucide-svelte` icons — tree-shaken, use for toolbar icons (already in layout)
- `svelte-sonner` toast — for save/drag success/error feedback

### Established Patterns
- New route: `frontend/src/routes/timeline/+page.svelte`
- New components: `frontend/src/lib/components/timeline/` directory
- API client extension: add `timeline` object to `frontend/src/lib/api.ts`
- New backend router: `backend/app/routers/timeline.py` with prefix `/api/timeline`
- Dark theme: `bg-gray-950` / `bg-gray-900` base, `text-gray-400` secondary, `primary-600` accent

### Integration Points
- Register new router in `backend/app/main.py`
- Add `/timeline` nav item to `navItems` array in `frontend/src/routes/+layout.svelte`
- Modal edit uses `PATCH /api/tasks/{id}` — already exists in `backend/app/routers/tasks.py`
- Drag reschedule also uses `PATCH /api/tasks/{id}` with `{ due_date: newDate }`

</code_context>

<specifics>
## Specific Ideas

- User explicitly chose **svelte-gantt** (not LayerChart) — it's a different library with drag support, researcher should confirm compatibility with SvelteKit 5 / Svelte 5.
- User chose **"fit to data"** default — means the timeline auto-zooms to show all active work on first load, not a fixed week/month window.
- User wants unscheduled tasks (no due_date) **visible as dashed bars** — don't silently drop them.
- Custom range picker: user said "svelte date picker" — researcher to identify the best option compatible with SvelteKit 5 (e.g. `svelte-date-picker`, `date-picker-svelte`, or native inputs as fallback if no good option exists).

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 04-team-timeline-view*
*Context gathered: 2026-04-23*
