---
phase: 15
slug: custom-kanban-statuses
status: approved
shadcn_initialized: false
preset: none
created: 2026-04-26
---

# Phase 15 — UI Design Contract

> Visual and interaction contract for custom Kanban statuses. Generated for `$gsd-ui-phase 15`, verified against the Phase 15 context and research.

---

## Design System

| Property | Value |
|----------|-------|
| Tool | none |
| Preset | not applicable |
| Component library | none; use existing Svelte components and Tailwind utilities |
| Icon library | `lucide-svelte` |
| Font | Existing `Inter, system-ui, sans-serif` from `frontend/tailwind.config.js` |

Do not add shadcn, Radix, chart, drag-and-drop, color picker, or modal packages in this phase. Reuse existing app primitives from `frontend/src/app.css`: `.card`, `.input`, `.label`, `.badge`, `.btn-primary`, `.btn-secondary`, `.btn-danger`.

---

## Target Surfaces

| Surface | Required Role |
|---------|---------------|
| `/tasks` Kanban view | Direct board-context status management for supervisors/admins; members can view statuses and move tasks only if existing permissions allow task updates |
| `/tasks` list/form UI | Replace hardcoded status filter and form options with DB-backed active statuses |
| `KanbanBoard.svelte` | Render columns from status records, not hardcoded enum arrays |
| `/projects` | Full project-context status settings: inherit/default state, create override, edit/reorder/archive/delete project statuses, revert to defaults |

The implementation may extract reusable components under `frontend/src/lib/components/statuses/` if it keeps the page files smaller. Recommended names:

- `StatusSetManager.svelte`
- `StatusEditorRow.svelte`
- `StatusReorderList.svelte`
- `StatusDeleteDialog.svelte`
- `ProjectStatusPanel.svelte`

---

## Layout Contract

### `/tasks` Status Management

Add a compact management entry point near the existing view toggle and filters.

Required structure:

1. Primary task controls remain at top: page title, task count, view toggle, `New Task`.
2. Status controls sit in the filter row when there is enough space, after type filters.
3. Use a secondary button labelled `Manage Statuses`.
4. Opening `Manage Statuses` shows a right-side drawer on desktop and a full-screen bottom sheet on mobile.
5. Drawer width: `min(520px, calc(100vw - 32px))`.
6. Mobile sheet must fit inside `max-h-[92dvh]` with internal scrolling.

Board-context behavior:

- If no project filter is active, show `Sub-team default statuses` as the editable scope.
- If exactly one project context is active, show `Project statuses` with inherited/default state and override actions.
- If the board is mixed-project, show a notice: `Project-specific statuses are available after filtering to one project.`
- Mixed-project view must not offer project override create/revert actions.

### `/projects` Status Settings

Each project card gains a low-emphasis action link: `Statuses`.

Clicking `Statuses` expands an inline panel beneath that project card on desktop and opens the same drawer/sheet pattern on mobile.

Required panel sections:

1. `Status source` row: `Inheriting sub-team defaults` or `Custom for this project`.
2. `Create project override` button when inheriting.
3. `Revert to defaults` button when custom.
4. Ordered status list with name, slug, color swatch, `Done` marker, and archived marker where applicable.
5. Add/edit controls for status name, color, and `is_done`.
6. Archive/delete controls use the destructive dialog contract below.

### Kanban Columns

Columns must render from active, non-archived status records ordered by `position`.

Column header contract:

- Left: color dot `10px` diameter using status `color`.
- Center: status `name`.
- Secondary: slug in monospace only in management mode, not in normal board mode.
- Right: count badge using existing gray badge styling.
- If `is_done = true`, show a small `Done` pill beside the name.

Column width must remain `w-72` to preserve current horizontal scroll behavior.

Column body must keep current mobile behavior:

- Horizontal board scroll remains enabled.
- `touch-action: pan-x pan-y` remains present on the board wrapper.
- Empty column copy: `No tasks in this status`.

---

## Interaction Contract

### Create/Edit Status

Fields:

- `Name` required, max 40 visible characters before truncation in lists.
- `Color` required, selected from a preset palette plus optional hex input if simple to implement.
- `Marks tasks complete` checkbox maps to `is_done`.

Slug behavior:

- Show slug as read-only helper text: `Slug: {slug}`.
- Copy: `Slug is used to map project statuses back to defaults.`
- Do not allow silent slug changes after creation unless backend explicitly supports safe rename. If editing name changes slug in the API, the UI must show a warning before save.

Preset color palette:

| Name | Hex | Intended Status |
|------|-----|-----------------|
| Slate | `#64748b` | Backlog, To Do |
| Sky | `#0ea5e9` | In Progress |
| Amber | `#f59e0b` | Review |
| Emerald | `#10b981` | Done |
| Rose | `#f43f5e` | Blocked |
| Violet | `#8b5cf6` | Custom |
| Cyan | `#06b6d4` | Custom |
| Orange | `#f97316` | Custom |

### Reorder

Status reordering is immediate and shared.

Interaction requirements:

- Drag handle icon: `GripVertical` from `lucide-svelte`.
- Save reorder on drag finalize, not through a separate Save button.
- Optimistically update order.
- On failure, revert order and toast: `Could not save status order. Restored previous order.`
- While saving, show inline text `Saving order...` in the manager header.

### Archive/Delete

A status with assigned tasks must never disappear without an explicit safe path.

Destructive dialog states:

1. If `task_count = 0`, primary destructive action is `Delete status`.
2. If `task_count > 0`, show two choices:
   - `Move tasks and delete`
   - `Archive status`
3. `Move tasks and delete` requires a replacement status select.
4. Replacement select must exclude the status being deleted and archived statuses.
5. Archive copy must state that existing tasks keep the archived status but new tasks cannot select it.

Dialog title copy:

- Empty status: `Delete {status_name}?`
- Assigned status: `{task_count} tasks use {status_name}`

Dialog body copy:

- Empty status: `This removes the status from the current set. This cannot be undone.`
- Assigned status: `Choose how to handle existing tasks before removing this status from active use.`

Buttons:

- Cancel: `Cancel`
- Move/delete: `Move tasks and delete`
- Archive: `Archive status`
- Empty delete: `Delete status`

### Project Override Revert

When reverting a project to sub-team defaults:

- Show a mapping preview table before confirmation.
- Auto-matched rows show `Matched by slug`.
- Unmatched rows require a fallback default status select.
- Confirmation button is disabled until every unmatched status has a fallback.

Copy:

- Title: `Revert project statuses to defaults?`
- Body: `Tasks will be moved to matching default statuses by slug. Choose a fallback for any unmatched project statuses.`
- Confirmation: `Revert to defaults`

---

## Spacing Scale

Declared values must remain multiples of 4.

| Token | Value | Usage |
|-------|-------|-------|
| xs | 4px | Icon gaps, color dots, drag handles |
| sm | 8px | Inline button gaps, badge spacing |
| md | 16px | Filter row gaps, form group spacing |
| lg | 24px | Drawer/sheet padding, section spacing |
| xl | 32px | Page-level gaps between controls and content |
| 2xl | 48px | Empty states and major vertical separation |
| 3xl | 64px | Not used in this phase |

Exceptions: existing Kanban card and board spacing may remain as-is when not directly changed by status management.

---

## Typography

Use existing app typography; do not introduce new font families.

| Role | Size | Weight | Line Height |
|------|------|--------|-------------|
| Body | 14px | 400 | 1.5 |
| Label | 14px | 500 | 1.4 |
| Helper | 12px | 400 | 1.4 |
| Badge | 12px | 500 | 1.2 |
| Section heading | 14px | 600 | 1.4 |
| Page heading | 24px | 700 | 1.25 |

Status names in lists and Kanban headers use `text-sm font-semibold`. Slugs use `text-xs font-mono text-gray-500`.

---

## Color

Keep the existing dark TeamFlow palette.

| Role | Value | Usage |
|------|-------|-------|
| Dominant (60%) | `#030712` / Tailwind `gray-950` equivalent | Page background and overlay depth |
| Secondary (30%) | `#111827` / `gray-900` | Cards, drawers, panels |
| Tertiary | `#1f2937` / `gray-800` | Inputs, row backgrounds, inactive buttons |
| Border | `#1f2937` / `gray-800` and `#374151` / `gray-700` | Card/drawer/input outlines |
| Accent (10%) | `#4f46e5` / `primary-600` | Primary CTA, focus rings, selected controls |
| Destructive | `#dc2626` / `red-600` | Delete and destructive confirmation only |

Accent reserved for:

- `New Task`
- `Create status`
- `Create project override`
- selected view toggle
- focused inputs
- enabled `Revert to defaults` confirmation only if not destructive

Do not use primary purple/indigo for arbitrary status colors. Status chips and column dots must use each status record's `color`.

---

## Copywriting Contract

| Element | Copy |
|---------|------|
| Tasks manager CTA | `Manage Statuses` |
| Projects action | `Statuses` |
| Create status CTA | `Create status` |
| Create project override CTA | `Create project override` |
| Revert project override CTA | `Revert to defaults` |
| Empty status set heading | `No statuses yet` |
| Empty status set body | `Create the first status to define this board's workflow.` |
| Mixed-project notice | `Project-specific statuses are available after filtering to one project.` |
| Inherited source label | `Inheriting sub-team defaults` |
| Custom source label | `Custom for this project` |
| Order save failure | `Could not save status order. Restored previous order.` |
| Status save failure | `Could not save status. Check the fields and try again.` |
| Delete blocked helper | `Statuses with tasks must be moved or archived before they can be deleted.` |
| Archive helper | `Archived statuses stay on existing tasks but are hidden from new selections.` |

Toast success copy:

- Create: `Status created`
- Update: `Status updated`
- Reorder: `Status order updated`
- Archive: `Status archived`
- Delete: `Status deleted`
- Project override: `Project status override created`
- Revert: `Project now uses default statuses`

---

## Accessibility Contract

- Every status form field must have a visible label.
- Color choices must expose `aria-label="Use {color_name} for status color"`.
- Color cannot be the only done indicator; done statuses must show text `Done`.
- Drag handles must have `aria-label="Drag to reorder {status_name}"`.
- Reorder must also provide keyboard-accessible `Move up` and `Move down` buttons or equivalent controls.
- Destructive dialogs must focus the dialog title on open and return focus to the triggering button on close if practical.
- Buttons must include disabled states during network saves.

---

## Responsive Contract

| Breakpoint | Behavior |
|------------|----------|
| Mobile `< 640px` | Manager uses full-width bottom sheet; action rows stack; status rows keep drag handle, color dot, name, and overflow menu visible |
| Tablet `640px-1024px` | Drawer or modal may be centered; status edit fields can use two-column layout |
| Desktop `> 1024px` | Right-side drawer for `/tasks`; inline expansion panel for `/projects`; Kanban columns remain horizontally scrollable |

The existing mobile Kanban horizontal-scroll behavior must not regress.

---

## Registry Safety

| Registry | Blocks Used | Safety Gate |
|----------|-------------|-------------|
| shadcn official | none | not required |
| third-party registry | none | not allowed for this phase |

---

## Implementation Guardrails

- Do not hardcode the five legacy status columns as the board source of truth.
- Do not hide archived statuses from existing task cards; hide them only from new assignment/status selectors.
- Do not allow project override actions in mixed-project board views.
- Do not make `is_done` visually depend on slug or legacy enum value.
- Do not remove or rename existing legacy `Task.status` UI compatibility in this phase.
- Do not introduce a new global theme or typography system.

---

## Checker Sign-Off

- [x] Dimension 1 Copywriting: PASS
- [x] Dimension 2 Visuals: PASS
- [x] Dimension 3 Color: PASS
- [x] Dimension 4 Typography: PASS
- [x] Dimension 5 Spacing: PASS
- [x] Dimension 6 Registry Safety: PASS

**Approval:** approved 2026-04-26

## UI-SPEC VERIFIED
