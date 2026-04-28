---
phase: 27
slug: timeline-gantt-clarity
status: approved
shadcn_initialized: false
preset: none
created: 2026-04-29
---

# Phase 27 - UI Design Contract

> Visual and interaction contract for the `/timeline` milestone-first planning surface. Generated inline from Phase 27 context and existing TeamFlow UI patterns.

---

## Design System

| Property | Value |
|----------|-------|
| Tool | none |
| Preset | not applicable |
| Component library | none |
| Icon library | `lucide-svelte` |
| Font | Existing TeamFlow sans stack (current app shell; do not introduce a new font family in this phase) |

---

## Spacing Scale

Declared values (must be multiples of 4):

| Token | Value | Usage |
|-------|-------|-------|
| xs | 4px | Icon gaps, compact badge padding |
| sm | 8px | Inline metadata spacing, dense row internals |
| md | 16px | Default row padding and control spacing |
| lg | 24px | Header and panel padding |
| xl | 32px | Major layout gaps between stacked sections |
| 2xl | 48px | Empty-state and large section spacing |
| 3xl | 64px | Not required on the main timeline surface |

Exceptions: the Gantt chart library's row and header geometry may use its existing internal dimensions when they are already close to this scale.

---

## Typography

| Role | Size | Weight | Line Height |
|------|------|--------|-------------|
| Body | 14px | 400 | 1.5 |
| Label | 12px | 500 | 1.4 |
| Heading | 16px | 600 | 1.35 |
| Display | 24px | 700 | 1.2 |

Rules:
- Milestone parent rows use `Heading` for title and `Label` for supporting metadata.
- Task rows use `Body` for title and `Label` for badges, due dates, and assignee context.
- Toolbar controls stay compact; do not promote them to hero-scale typography.

---

## Color

| Role | Value | Usage |
|------|-------|-------|
| Dominant (60%) | `#080d1a` | Timeline canvas, page shell, deep surfaces |
| Secondary (30%) | `#0f172a` | Toolbar, row backgrounds, supporting surfaces |
| Accent (10%) | `#4f46e5` | Active view toggle, focused milestone treatment, progress emphasis, selected range affordances |
| Destructive | `#ef4444` | Overdue/risk emphasis, destructive actions only |

Accent reserved for:
- Active project/member view state
- Focused milestone banner and selected milestone affordance
- Positive progress emphasis
- Interactive focus rings

Color behavior:
- Milestone rows should use secondary surfaces plus badges/icons for signal, not full-width accent fills.
- Task bars keep project color identity, but milestone planning signals should not rely on project color alone.
- Risk indicators should use red/amber-style signal badges sparingly so they remain scannable.

---

## Copywriting Contract

| Element | Copy |
|---------|------|
| Primary CTA | `Save task` |
| Empty state heading | `No timeline data yet` |
| Empty state body | `Add milestones and tasks to see planning timelines here.` |
| Error state | `Timeline unavailable. Refresh the page or try again after your connection recovers.` |
| Destructive confirmation | `Delete milestone`: `Delete this milestone?` |

Microcopy rules:
- Use planning language, not marketing language.
- Milestone rows should name concrete signals like `At risk`, `Blocked`, `Due soon`, `Decision`, and `On track`.
- View labels remain `By Project` and `By Member`.
- Focus banner copy should identify the current focused milestone or task without adding instructional filler.

---

## Layout Contract

### Primary Surface

- `/timeline` remains a single-page planning surface with three vertical bands:
  1. Page header
  2. Compact timeline toolbar
  3. Scrollable timeline work area
- The work area remains dominated by the Gantt canvas, but milestone parent rows become the first visual anchor in project view.

### Project View

- Each project remains a top-level group.
- Each milestone becomes a distinct parent row under its project, visually different from task bars and non-draggable.
- Milestone parent rows must show:
  - title
  - status badge
  - date span
  - progress badge/label
  - compact risk/decision/planning badges when applicable
- Unassigned tasks remain visible under a `No Milestone` bucket, but this bucket should read as secondary to milestone rows.

### Member View

- Member rows stay people-first.
- Task rows must include milestone badges or links so milestone context survives the view switch.
- If the current focused milestone is not naturally visible in member view, show a compact focused-milestone banner above the chart area.

---

## Interaction Contract

- Switching between `By Project` and `By Member` preserves:
  - selected date range
  - focused milestone/task context
- Clicking a milestone row focuses that milestone.
- Clicking a task row focuses the task and opens the existing edit modal.
- Parent milestone rows are not draggable.
- Task bars remain draggable for due-date rescheduling.
- Active or risky milestones should start expanded by default; quiet milestones may start collapsed.
- Collapsed milestone rows must still expose progress plus task-state counts.

---

## Signal Contract

### Milestone Progress

- Progress is always visible on milestone parent rows as a badge or compact numeric label in addition to any bar treatment.
- Progress should read quickly at a glance; avoid hiding it only inside hover states or task expansion.

### Risk

- Risk is derived from existing data only.
- The UI may derive risk from:
  - delayed milestone status
  - overdue milestone dates
  - blocked tasks
  - critical tasks
  - low completion near due date
  - relevant custom-status state
- Risk appears as compact badges/icons on milestone rows, not as full-surface alert blocks.

### Planning Window

- The milestone `start_date` to `due_date` span is the planning-window treatment.
- Planning-window emphasis should make milestone timing legible without competing with task bars for dominance.

### Decision Points

- Decision points in Phase 27 are lightweight placeholders only.
- They may be inferred from existing milestone description/tag content.
- Do not introduce new decision-entry controls or persistence in this phase.

---

## State And Feedback

- Loading state: centered spinner inside the timeline work area.
- Empty state: calm, centered message with clear next step; no decorative illustration required.
- Error state: single-line problem statement with recovery language.
- Focused state: selected milestone/task uses accent-level emphasis plus persistent visibility in the current view.
- Hover state: row hover may slightly lift or tint, but should not overpower milestone/task signal colors.

---

## Registry Safety

| Registry | Blocks Used | Safety Gate |
|----------|-------------|-------------|
| shadcn official | none | not required |
| third-party | `svelte-gantt` already in use | keep existing dependency; no new UI registry additions required for this phase |

---

## Checker Sign-Off

- [x] Dimension 1 Copywriting: PASS
- [x] Dimension 2 Visuals: PASS
- [x] Dimension 3 Color: PASS
- [x] Dimension 4 Typography: PASS
- [x] Dimension 5 Spacing: PASS
- [x] Dimension 6 Registry Safety: PASS

**Approval:** approved 2026-04-29
