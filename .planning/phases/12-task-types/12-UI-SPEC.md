---
phase: 12
slug: task-types
status: approved
shadcn_initialized: false
preset: none
created: 2026-04-24
---

# Phase 12 — UI Design Contract

> Visual and interaction contract for adding task types to TeamFlow task surfaces.

---

## Design System

| Property | Value |
|----------|-------|
| Tool | none |
| Preset | not applicable |
| Component library | none |
| Icon library | lucide-svelte |
| Font | existing app font stack |

This phase extends the existing TeamFlow task UI. Do not introduce a new component library, page layout pattern, or visual theme.

---

## Scope

### In Scope

- Add a task type selector to the task create/edit form.
- Show task type as a compact icon plus label badge on task cards and rows.
- Add a multi-select task type filter to the existing task filter bar.
- Keep task type presentation consistent across list, Kanban, and Agile views.
- Let AI parse/breakdown flows suggest a task type, while keeping user confirmation before create.

### Out of Scope

- Custom task type management.
- New KPI charts or analytics views.
- Custom Kanban status UI.
- Sprint UI changes.
- New global navigation or page layout changes.

---

## Task Type Visual Language

| Type | Label | Icon | Badge Style | Intent |
|------|-------|------|-------------|--------|
| `feature` | Feature | `Sparkles` or `PackagePlus` | muted cyan/blue badge | New capability work |
| `bug` | Bug | `Bug` | muted red badge | Defect or regression work |
| `task` | Task | `CheckSquare` or `ListTodo` | neutral gray badge | General execution work |
| `improvement` | Improve | `Wrench` or `RefreshCw` | muted amber/green badge | Refinement or enhancement work |

Badge contract:
- Always render icon plus short label, not icon-only.
- Use `text-[10px]` or `text-xs` to match existing priority/status badges.
- Use `px-1.5 py-0.5` for compact cards and `px-2 py-0.5` where space allows.
- Use existing `.badge` class patterns and Tailwind utility colors.
- Keep badge contrast readable on `bg-gray-800` and `bg-gray-900` surfaces.

---

## Spacing Scale

Declared values are multiples of 4:

| Token | Value | Usage |
|-------|-------|-------|
| xs | 4px | Icon gaps inside badges and compact controls |
| sm | 8px | Badge row gaps, filter chip gaps |
| md | 16px | Form grid gaps, modal field spacing |
| lg | 24px | Page/filter section spacing |
| xl | 32px | Large task surface gaps |
| 2xl | 48px | Empty state vertical rhythm |
| 3xl | 64px | Not used in this phase |

Exceptions: none.

---

## Typography

| Role | Size | Weight | Line Height |
|------|------|--------|-------------|
| Body | existing `text-sm` | 400-500 | existing app default |
| Label | existing `.label` / `text-xs` | 500 | existing app default |
| Badge | `text-[10px]` or `text-xs` | 500-700 | compact |
| Heading | existing page/modal headings | 600-700 | existing app default |
| Display | not applicable | not applicable | not applicable |

Do not add display-scale typography. This phase is a task workflow enhancement, not a new destination page.

---

## Color

| Role | Value | Usage |
|------|-------|-------|
| Dominant (60%) | existing `gray-950` / `gray-900` | Page and modal backgrounds |
| Secondary (30%) | existing `gray-800` / `gray-700` | Cards, inputs, filter surfaces, badges |
| Accent (10%) | existing `primary-500` | Focus rings, selected filter chips, active controls |
| Destructive | existing red scale | Bug badge, delete hover states, destructive actions |

Accent reserved for:
- Selected type filter chips.
- Input focus rings.
- Existing primary actions.

Task type badges may use muted semantic colors, but they must not overpower status or priority badges.

---

## Interaction Contract

### Create/Edit Form

- Add `Type` beside `Status` and `Priority`.
- On desktop and tablet, use a three-column row when there is enough width.
- On narrow mobile widths, allow the selectors to wrap into a two-column or single-column layout without horizontal scrolling.
- Default value is `task`.
- The field is visible in both create and edit mode.

### List View

- Show type badge in the existing metadata row near status and priority.
- Recommended order: status, type, priority, due date, assignee, tags.
- Keep long titles and descriptions unchanged; type badge must not push action buttons off-screen.

### Kanban View

- Show type badge in `KanbanCard.svelte` in the existing badge row with priority, due date, and tags.
- Badge should remain visible even when description is present.
- Do not add a second row unless wrapping naturally occurs.

### Agile View

- Show type badge in each task row near priority.
- Group-level summaries may continue to count priority only; adding type summaries is optional and not required for Phase 12.

### Multi-Select Type Filter

- Add type filtering alongside the existing status filter and "My tasks only" checkbox.
- The filter must support selecting any combination of `feature`, `bug`, `task`, and `improvement`.
- Selected types should render as compact chips or pressed toggle buttons with icon plus label.
- Empty selection means "all types".
- On mobile, controls may wrap; no dropdown or chip row should overflow the viewport.
- Filtering applies to list, Kanban, and Agile views.

### AI Suggestion Confirmation

- AI may populate the form's type field after parse/breakdown.
- The user must still see the type selector before creating the task.
- If AI confidence is unclear or no type is returned, keep `task`.

---

## Copywriting Contract

| Element | Copy |
|---------|------|
| Type field label | Type |
| Type filter label | Type |
| All-types state | All types |
| Empty filtered state heading | No tasks match these filters |
| Empty filtered state body | Change the filters or create a new task. |
| AI parse success | Parsed — review and create |
| Create CTA | Create Task |
| Edit CTA | Save Changes |
| Destructive confirmation | Delete task? |

Avoid explanatory helper text unless validation fails. The type names should be self-evident from icon plus label.

---

## Accessibility Contract

- Type selector must have a visible `<label>` associated with the input/control.
- Icon badges must include readable text, so the icon is decorative.
- Filter chips or toggles must expose selected state visually and via native checkbox/button semantics.
- All type controls must be keyboard reachable.
- Focus states must match existing input/button focus styling.
- Color cannot be the only signal; the label must always appear.

---

## Responsive Contract

- The task form must remain usable inside the existing `max-h-[92dvh]` modal.
- The type selector row must wrap on mobile instead of shrinking labels below readability.
- Kanban cards must retain stable width; badges may wrap inside the card.
- The filter bar may wrap across rows using existing `flex-wrap`.
- No task type text may overflow its badge or push card actions out of view.

---

## Registry Safety

| Registry | Blocks Used | Safety Gate |
|----------|-------------|-------------|
| shadcn official | none | not required |
| third-party | none | not required |

No registry components are required for this phase.

---

## Checker Sign-Off

- [x] Dimension 1 Copywriting: PASS
- [x] Dimension 2 Visuals: PASS
- [x] Dimension 3 Color: PASS
- [x] Dimension 4 Typography: PASS
- [x] Dimension 5 Spacing: PASS
- [x] Dimension 6 Registry Safety: PASS

**Approval:** approved 2026-04-24
