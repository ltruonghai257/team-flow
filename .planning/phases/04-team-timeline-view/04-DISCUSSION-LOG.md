# Phase 4: Team Timeline View - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-23
**Phase:** 04-team-timeline-view
**Areas discussed:** Gantt library vs custom, Data grouping & hierarchy, Interactivity & click behavior, Time range & navigation

---

## Gantt library vs custom

| Option | Description | Selected |
|--------|-------------|----------|
| Reuse LayerChart | Horizontal bar charts with time axis, consistent with Phase 3, no new dependency | |
| svelte-gantt | Purpose-built Svelte Gantt library with native drag-and-drop, virtualization | ✓ |
| Custom SVG/div bars | TailwindCSS positioned divs or inline SVG, full control, zero dependencies | |
| You decide | Claude picks based on stack | |

**User's choice:** svelte-gantt

---

### Follow-up: Read-only or drag-to-reschedule?

| Option | Description | Selected |
|--------|-------------|----------|
| Read-only — view only | No drag, keeps scope tight | |
| Drag to reschedule | Dragging updates due_date via PATCH /api/tasks/{id} | ✓ |

**User's choice:** Drag to reschedule

---

## Data grouping & hierarchy

| Option | Description | Selected |
|--------|-------------|----------|
| By project → milestone → tasks | Rows grouped under each project with milestone markers | |
| By assignee (member rows) | Each member gets a row showing tasks across all projects | |
| Flat — all tasks in one list | Single chronological list, color-coded by project.color | |
| Switchable (project view / member view) | Toggle between project grouping and assignee grouping | ✓ |

**User's choice:** Switchable (project view / member view)

---

### Follow-up: Tasks without a milestone in project view?

| Option | Description | Selected |
|--------|-------------|----------|
| Show under 'Unassigned' group | Catch-all 'No Milestone' row per project | ✓ |
| Hide milestone-less tasks | Only tasks with a milestone shown | |

**User's choice:** Show under 'Unassigned' group

---

## Interactivity & click behavior

| Option | Description | Selected |
|--------|-------------|----------|
| Open a side panel / drawer | Slide-in panel, stays on timeline | |
| Open a modal dialog | Centered modal with task details and edit form | ✓ |
| Navigate to /tasks | Redirect to tasks board | |

**User's choice:** Open a modal dialog

---

### Follow-up: What's editable in the modal?

| Option | Description | Selected |
|--------|-------------|----------|
| Full task edit (title, status, priority, due date, assignee) | Same as main task edit form | ✓ |
| Status + due date only | Quick-update for timeline context | |

**User's choice:** Full task edit

---

## Time range & navigation

### Default time range on open

| Option | Description | Selected |
|--------|-------------|----------|
| Current month | Current calendar month | |
| Current week | Current 7-day window | |
| Fit to data | Auto-spans earliest start_date to latest due_date | ✓ |

**User's choice:** Fit to data

---

### Custom range picker

| Option | Description | Selected |
|--------|-------------|----------|
| Native HTML date inputs (from / to) | Two `<input type="date">` fields, no dependency | |
| You decide | Claude picks based on codebase | |
| (free text) | "svelte date picker" | ✓ |

**User's choice:** Svelte date picker (researcher to confirm best compatible library)

---

### Tasks with no due_date

| Option | Description | Selected |
|--------|-------------|----------|
| Hide them | Only tasks with due_date appear | |
| Show at current date with a dashed bar | Short dashed bar at today's position | ✓ |

**User's choice:** Show at current date with a dashed bar

---

## Claude's Discretion

- Overdue visual treatment (red outline vs fill)
- Milestone marker shape on time axis
- Assignee avatar style on task bars
- Member view row ordering

## Deferred Ideas

None
