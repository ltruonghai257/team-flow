---
phase: 4
slug: team-timeline-view
status: approved
shadcn_initialized: false
preset: none
created: 2026-04-23
---

# Phase 4 — UI Design Contract

> Visual and interaction contract for the Team Timeline View. Generated from CONTEXT.md locked decisions + existing codebase patterns. Verified before planning.

---

## Design System

| Property | Value |
|----------|-------|
| Tool | none (manual TailwindCSS) |
| Preset | not applicable |
| Component library | none (SvelteKit — shadcn not applicable) |
| Icon library | lucide-svelte (tree-shaken per-component) |
| Font | Inter (system-ui fallback) |

**Note:** No `components.json` found. Project uses manual TailwindCSS utility classes with shared tokens in `app.css`. All timeline components follow the same pattern as existing pages (no new design system to introduce).

---

## Spacing Scale

Standard 8-point scale — consistent with all existing routes:

| Token | Value | Usage |
|-------|-------|-------|
| xs | 4px | Icon gaps, badge padding |
| sm | 8px | Toolbar button spacing, task bar inner padding |
| md | 16px | Section padding, card inner spacing |
| lg | 24px | Timeline header padding, panel gaps |
| xl | 32px | Page-level section breaks |
| 2xl | 48px | Major layout gaps |
| 3xl | 64px | Page top padding |

Exceptions:
- Gantt row height: 44px minimum (touch target compliance for drag handles)
- Timeline axis label spacing: derived from svelte-gantt's internal layout — do not override with custom values; use svelte-gantt's `columnWidth` prop to control density

---

## Typography

Inherited from project Inter font + Tailwind defaults. Phase-specific declarations:

| Role | Size | Weight | Line Height | Tailwind Class |
|------|------|--------|-------------|----------------|
| Body / task label | 14px | 400 | 1.4 | `text-sm` |
| Toolbar label | 14px | 500 | 1.4 | `text-sm font-medium` |
| Section heading | 16px | 600 | 1.3 | `text-base font-semibold` |
| Page title | 20px | 700 | 1.2 | `text-xl font-bold` |

**Rule:** Max 4 sizes (14, 16, 20 — display not needed for this phase). Max 2 weights in any single component (400 + 600, or 500 + 700). Task bar title truncates with `truncate` at bar width.

---

## Color

60/30/10 split — consistent with existing app theme:

| Role | Value | Usage |
|------|-------|-------|
| Dominant (60%) | `#030712` (`bg-gray-950`) | Page background, timeline canvas background |
| Secondary (30%) | `#111827` (`bg-gray-900`) | Toolbar bar, header row, modal background, sidebar |
| Accent (10%) | `#4f46e5` (`primary-600`) | Active range selector button, focus rings, drag resize handle highlight |
| Destructive | `#dc2626` (`red-600`) | Used only for overdue task/milestone visual treatment (red outline `ring-1 ring-red-500`) |

**Accent reserved for:**
1. Active range selector button (Week / Month / Custom — active state only)
2. Focus rings on interactive controls (date picker input, modal form fields)
3. Drag resize handle on task bars (thin left/right indicator strip)

**Task bar colors:** Derived from `project.color` field (not accent). Each project gets its own color. Default project color is `#6366f1` (primary-500).

**Overdue treatment:** Red outline (`ring-1 ring-red-500/70`) on overdue task bars and milestone markers — not red fill (preserves project color readability).

**Unscheduled task bars (no due_date):** Dashed border (`border border-dashed border-gray-500`) with `bg-gray-700/50` fill and muted label — visually distinct from scheduled tasks.

**Member view / Project view toggle:** Inactive button = `bg-gray-800 text-gray-400`, active = `bg-gray-700 text-gray-200 font-medium`.

---

## Component Inventory

Phase-specific components in `frontend/src/lib/components/timeline/`:

| Component | Purpose | Key Props |
|-----------|---------|-----------|
| `TimelinePage.svelte` | Root page container, data loading | — |
| `TimelineToolbar.svelte` | View toggle + range selector | `viewMode`, `rangeMode`, `customStart`, `customEnd` |
| `TimelineGantt.svelte` | svelte-gantt wrapper, row + bar rendering | `rows`, `tasks`, `viewMode` |
| `TimelineTaskBar.svelte` | Custom task bar slot for svelte-gantt | `task`, `project` |
| `TimelineMilestoneMarker.svelte` | Milestone diamond marker on time axis | `milestone` |
| `TaskEditModal.svelte` | Modal dialog for task edit (reuse pattern from existing modals) | `taskId`, `onSave`, `onClose` |

**Modal pattern:** Follow existing modal pattern — `fixed inset-0 bg-black/60 z-50` overlay, `bg-gray-900 rounded-xl` panel, close on backdrop click or Escape key.

---

## Interaction Contract

### Drag-to-Reschedule
- Drag a task bar horizontally → updates `due_date` via `PATCH /api/tasks/{id}`
- On drag start: bar gets `opacity-80 scale-y-95` visual feedback
- On drag success: `svelte-sonner` toast — "Task rescheduled to {new date}" (success variant)
- On drag error (API failure): `svelte-sonner` toast — "Failed to reschedule — changes reverted" (error variant), bar snaps back
- Drag is only enabled when `isLoggedIn` — no role restriction (all roles can drag)

### Click-to-Edit Modal
- Click task bar → opens `TaskEditModal` with current task data pre-filled
- Save button: `btn-primary` class, label "Save Changes"
- Cancel button: `btn-secondary` class, label "Cancel"
- Delete action (if user is supervisor/admin): `btn-danger` class, label "Delete Task" with confirmation text "Delete this task? This cannot be undone."
- After successful save: modal closes, timeline bar updates in place (no full reload)

### Range Selector
- Three buttons: "Week" | "Month" | "Custom" — grouped as a pill button set
- Active state: `bg-gray-700 text-white font-medium rounded-md`
- Inactive state: `text-gray-400 hover:text-gray-200`
- "Custom" selection reveals date picker inline below toolbar
- Date picker: native `<input type="date">` elements (start + end), styled with `.input` class — no third-party date picker dependency (avoids SvelteKit 5 compatibility risk)

### View Toggle (Project / Member)
- Two buttons: "Projects" | "Members" — same pill style as range selector
- Toggle changes row grouping in svelte-gantt: project→milestone→task rows vs. member rows
- Transition: instantaneous (no animation — gantt re-renders row data)

### Fit-to-Data Default
- On page load: auto-calculate earliest `start_date` (or `created_at` fallback) and latest `due_date` across active items
- Zoom/scroll position set to show full range with ~5% padding on each side

---

## Copywriting Contract

| Element | Copy |
|---------|------|
| Page title | "Team Timeline" |
| View toggle — option 1 | "Projects" |
| View toggle — option 2 | "Members" |
| Range button — week | "This Week" |
| Range button — month | "This Month" |
| Range button — custom | "Custom Range" |
| Custom range — start label | "From" |
| Custom range — end label | "To" |
| Drag success toast | "Rescheduled to {date}" |
| Drag error toast | "Couldn't reschedule — please try again" |
| Task edit modal — primary CTA | "Save Changes" |
| Task edit modal — secondary | "Cancel" |
| Task edit modal — delete CTA | "Delete Task" |
| Delete confirmation message | "Delete this task? This action cannot be undone." |
| Empty state heading | "No timeline data yet" |
| Empty state body | "Create tasks with due dates to see them on the timeline." |
| Error state | "Couldn't load timeline data. Refresh to try again." |
| Unscheduled task tooltip | "No due date — drag to schedule" |
| Loading state | "Loading timeline..." (spinner, centered) |

---

## Registry Safety

| Registry | Blocks Used | Safety Gate |
|----------|-------------|-------------|
| shadcn official | none (not initialized) | not applicable |
| svelte-gantt (npm package, not shadcn registry) | `SvelteGantt` component | npm package — not a shadcn registry block; no view/diff gate required. Researcher confirmed: standard npm install, no network access in source. |

**Note:** `svelte-gantt` is installed via npm (not a shadcn registry). The shadcn registry safety gate applies only to shadcn registries. No third-party shadcn registries are used in this phase.

---

## Visual Hierarchy

**Primary focal point:** The Gantt chart canvas — takes ~85% of viewport height, full width minus sidebar.

**Visual priority (top to bottom):**
1. Page title + view toggle (top-left) — orientation
2. Range selector (top-right) — time control
3. Gantt row headers (left column) — context labels
4. Task bars (center/right) — primary work data
5. Milestone markers (axis overlay) — project structure
6. At-a-glance: overdue = red outline, unscheduled = dashed

**Accessibility notes:**
- Icon-only toolbar buttons must have `title` attribute for tooltip
- Task bars show assignee initials (2-char avatar circle) — label always visible on hover via native `title`
- Keyboard navigation: Tab through toolbar controls, Enter to open edit modal

---

## Checker Sign-Off

- [x] Dimension 1 Copywriting: PASS
- [x] Dimension 2 Visuals: PASS
- [x] Dimension 3 Color: PASS
- [x] Dimension 4 Typography: PASS
- [x] Dimension 5 Spacing: PASS
- [x] Dimension 6 Registry Safety: PASS

**Approval:** approved 2026-04-23
