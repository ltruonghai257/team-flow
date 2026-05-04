---
phase: 18
slug: status-transition-graph
status: approved
shadcn_initialized: false
preset: none
created: 2026-04-26
---

# Phase 18 - UI Design Contract

> Visual and interaction contract for the Status Transition Graph frontend work.

---

## Design System

| Property | Value |
|----------|-------|
| Tool | none |
| Preset | not applicable |
| Component library | none |
| Icon library | lucide-svelte |
| Font | Inter, system-ui, sans-serif |

Use existing Svelte 5, TailwindCSS, `lucide-svelte`, `svelte-sonner`, and `svelte-dnd-action` patterns. Do not introduce shadcn, Radix, Base UI, graph-editing packages, or a new visualization dependency for this phase.

---

## Spacing Scale

Declared values must stay on the existing Tailwind 4px scale.

| Token | Value | Usage |
|-------|-------|-------|
| xs | 4px | Icon gaps, matrix cell inner gaps, tooltip icon spacing |
| sm | 8px | Compact button padding, table cell padding, inline status metadata |
| md | 16px | Default panel padding, editor section spacing, modal row gaps |
| lg | 24px | Status manager group spacing, responsive stacked sections |
| xl | 32px | Major separation only when transition editor stacks under status list |

Exceptions: none.

Layout contract:

- Keep `StatusSetManager` compact. If the transition editor makes the manager crowded, split existing status editing and transition rules into tabs or a segmented control inside the same manager surface.
- Do not nest decorative cards inside the existing `/tasks` status-manager card. Use unframed sections, borders, tables, and compact panels.
- Matrix cells must have stable square-ish dimensions: minimum 36px by 32px on desktop and 40px by 36px on touch/mobile.
- The matrix must scroll horizontally inside its own region when status count exceeds available width; it must not force the whole page wider.

---

## Typography

| Role | Size | Weight | Line Height |
|------|------|--------|-------------|
| Body | 14px | 400 | 1.5 |
| Label | 12px | 500 | 1.4 |
| Heading | 14px | 600 | 1.4 |
| Dense metadata | 11px | 500 | 1.3 |
| Page heading | unchanged existing Tasks page heading | unchanged | unchanged |

Do not add hero-scale or marketing-style type. Transition rules are an operational configuration surface inside `/tasks` and `/projects`, not a new landing page.

---

## Color

| Role | Value | Usage |
|------|-------|-------|
| Dominant (60%) | `#111827`, `#030712` | Existing dark surfaces and page background |
| Secondary (30%) | `#1f2937`, `#374151` | Inputs, table headers, borders, inactive cells |
| Accent (10%) | `#4f46e5`, `#6366f1` | Primary save/generate actions, focused matrix cells |
| Success | `#16a34a`, `#14532d` | Allowed transition cells and valid flow indicators |
| Warning | `#f59e0b`, `#78350f` | Non-blocking graph-shape warnings |
| Destructive | `#dc2626` | Delete/remove transition and blocked-move feedback only |

Accent reserved for:

- `Generate linear flow`
- `Save transitions`
- focused matrix controls
- selected tab/segmented-control state

Transition state colors:

- Allowed edge: green check or active toggle with a subtle green surface.
- Disallowed edge: gray empty state; no red for ordinary off cells.
- Self-transition: disabled gray cell with no checkbox/toggle.
- Blocked runtime move: red/destructive toast or inline feedback only after a specific blocked action.

Avoid a one-note indigo/purple screen. Preserve status colors as data colors and keep workflow-rule controls mostly neutral.

---

## Copywriting Contract

| Element | Copy |
|---------|------|
| Transition section title | Transition rules |
| Transition section subtitle | Empty rules allow tasks to move freely. Add rules to restrict moves. |
| Primary CTA | Save transitions |
| Quick-start CTA | Generate linear flow |
| Empty transition state heading | No transition rules |
| Empty transition state body | Tasks can move between any active statuses until rules are saved. |
| Graph preview heading | Preview |
| Graph preview empty state | Save or select transitions to preview the workflow. |
| Warning heading | Workflow warnings |
| Matrix save success toast | Transition rules saved |
| Blocked move toast | Cannot move from {current} to {target} |
| Backend fallback blocked toast | This move is not allowed by the workflow rules. |
| Destructive confirmation | Remove transition: {from} to {to}? |

Do not add visible instructional paragraphs explaining how the whole feature works. Use concise labels, tooltips, empty states, and action text.

---

## StatusSetManager Contract

Primary surface:

- Add transition management inside `frontend/src/lib/components/statuses/StatusSetManager.svelte` or a child component owned by it.
- The editor must operate on active statuses only. Archived statuses remain visible only in the existing archived-status disclosure and must not appear as editable matrix rows or columns.
- If `isMixedProjectView` is true, keep the existing mixed-project message and hide transition editing.
- If `canManage` is false, the transition matrix must be read-only or hidden according to the surrounding manager permissions. Write controls must not render for non-managers.

Editor structure:

- Use a matrix/table as the source of truth.
- Rows are `from` statuses; columns are `to` statuses.
- Status names in headers must show the existing color dot where space allows.
- Self-transition cells must be disabled or replaced with a neutral dash.
- Each editable cell should use a checkbox/toggle control with accessible labels like `Allow {from} to {to}`.
- The matrix save action must persist all selected edges together so the UI does not leave partial graph states.

Quick-start:

- `Generate linear flow` creates forward transitions from each active status to the next active status in current position order.
- It must not auto-save without an explicit `Save transitions` action unless the implementation clearly shows it is saving immediately.

Warnings:

- Warnings are non-blocking by default.
- Warn for active statuses with no outgoing edges when rules exist, no path to any `is_done` status, and disconnected active statuses if feasible.
- Warnings must be compact and scannable; avoid modal warnings for ordinary graph-shape issues.

Preview:

- Provide a read-only graph preview derived from the selected transition matrix.
- The preview can be a lightweight CSS/SVG representation inside the app code. Do not add heavy interaction scope.
- The preview must not become the primary editor.
- The preview must handle more statuses than fit horizontally by wrapping or scrolling without overlapping labels.

---

## Kanban Contract

Inputs:

- `KanbanBoard.svelte` should receive transition data or a precomputed allowed-target helper from `/tasks/+page.svelte`.
- Empty transition list means unrestricted movement.

Column feedback:

- Add small `lucide-svelte` hint icons/tooltips to restricted column headers, not always-visible labels.
- Obvious invalid drop targets may be visually muted or blocked during drag.
- Do not resize columns or cards when hints appear.

Drop behavior:

- If the client can determine the move is invalid, prevent or revert the drop and show blocked-move feedback.
- Always handle backend HTTP 422 as authoritative: revert local state, show the structured blocked-move toast, and refresh status set/transition data.
- Do not remove the backend attempted-move path entirely; stale clients must still rely on server enforcement.

---

## Task Edit Dropdown Contract

In `frontend/src/routes/tasks/+page.svelte`:

- The edit status dropdown must show allowed target statuses plus the current status so the current value never disappears.
- Empty transition list means all active statuses are available.
- Creation forms are not constrained by transition rules because there is no prior status move.
- If the effective status set changes because project changes are edited, recompute allowed targets after the relevant status/project data refresh.
- Legacy fallback options must remain usable when no DB-backed active statuses are loaded.

---

## Error and Refresh Contract

Structured backend blocked-transition errors should be parsed when possible:

- `detail.code === "status_transition_blocked"`
- `detail.current_status_name`
- `detail.target_status_name`
- `detail.allowed_status_ids`

UI response:

- Toast: `Cannot move from {current} to {target}`.
- Fallback toast: `This move is not allowed by the workflow rules.`
- Refresh status set and transition data after a backend blocked-transition 422.
- Preserve the task's previous visual status after the blocked move.

---

## Responsive Contract

Desktop:

- Status manager can show status list/editor and transition rules in tabs or stacked sections.
- Matrix table may use sticky row/column headers if implementation cost is modest.

Mobile:

- Matrix must be horizontally scrollable inside the transition editor.
- Controls must remain at least 40px high where touch interaction is expected.
- The graph preview may collapse below the matrix; it must not be required to edit rules.

No text may overflow buttons, table headers, tooltips, or status chips. Long status names should truncate in dense headers and remain readable via title/tooltip text.

---

## Registry Safety

| Registry | Blocks Used | Safety Gate |
|----------|-------------|-------------|
| shadcn official | none | not required |
| third-party registries | none | not allowed for this phase |

No registry components are approved for this phase.

---

## Checker Sign-Off

- [x] Dimension 1 Copywriting: PASS
- [x] Dimension 2 Visuals: PASS
- [x] Dimension 3 Color: PASS
- [x] Dimension 4 Typography: PASS
- [x] Dimension 5 Spacing: PASS
- [x] Dimension 6 Registry Safety: PASS

**Approval:** approved 2026-04-26
