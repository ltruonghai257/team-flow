---
phase: 16
slug: advanced-kpi-dashboard
status: approved
shadcn_initialized: false
preset: none
created: 2026-04-26
---

# Phase 16 - UI Design Contract

> Visual and interaction contract for the Advanced KPI Dashboard. Generated for `$gsd-ui-phase 16` and intended as locked design context for `$gsd-plan-phase 16`.

---

## Design System

| Property | Value |
|----------|-------|
| Tool | none |
| Preset | not applicable |
| Component library | none |
| Icon library | lucide-svelte |
| Font | existing app font stack |

**Design direction:** Preserve TeamFlow's existing dark operational UI, but reorganize `/performance` into a denser supervisor command surface. The result should feel like a practical internal analytics console, not a marketing dashboard.

**Primary route:** `/performance`

**Existing visual language to preserve:**
- Dark surfaces: `bg-gray-950`, `bg-gray-900`, `bg-gray-900/50`, `border-gray-800`
- Compact supervisor table patterns from `frontend/src/routes/performance/+page.svelte`
- Inline SVG chart pattern unless a verified chart helper is explicitly chosen during planning
- `lucide-svelte` icons for tabs, actions, metric cards, filters, exports, and drill-down affordances

---

## Layout Contract

### Page Shell

`/performance` must remain the main route and become a tabbed KPI workspace.

Required structure:
1. Header band with title, sub-team scope indicator, refresh timestamp, and primary export action.
2. People-first Overview tab containing member KPI scorecards before charts.
3. Tab row with `Overview`, `Sprint`, `Quality`, `Members`, and `Settings`.
4. View-specific filter row inside each tab, not one global mega-filter.
5. Chart/content region with drill-down and export controls at the chart panel level.

### Tab Content

| Tab | Purpose | Required Content |
|-----|---------|------------------|
| Overview | Supervisor first look | Member KPI scorecards, exception list, top KPI summary tiles |
| Sprint | Sprint delivery health | Velocity chart, burndown chart, sprint/project/member/type/date filters |
| Quality | Defect and MTTR health | Bugs reported vs resolved, MTTR by member, defect trend, quality filters |
| Members | Comparative member analytics | Throughput stacked by type, cycle time by type, member table, drill-down links |
| Settings | KPI scoring policy | Weight sliders/inputs, default formula explanation, reset-to-default action |

### Responsive Behavior

- Desktop (`lg+`): scorecards use a 3-column grid; chart panels may use 2-column layout when charts fit.
- Tablet (`md`): scorecards use 2 columns; charts stack if labels would collide.
- Mobile: tabs become horizontally scrollable; filters collapse into a compact filter sheet/button; scorecards stack in one column.
- No chart label, legend, filter chip, or table cell may overlap at 375px viewport width.

---

## Spacing Scale

Declared values must stay on the existing Tailwind 4px rhythm.

| Token | Value | Usage |
|-------|-------|-------|
| xs | 4px | Icon-label gaps, chart legend swatches |
| sm | 8px | Button padding, filter chip spacing, compact row gaps |
| md | 16px | Card padding, table cell vertical rhythm |
| lg | 24px | Chart panel padding, tab content section gaps |
| xl | 32px | Page section gaps, overview grid gaps |
| 2xl | 48px | Major tab group separation only |
| 3xl | 64px | Not used in this phase |

Exceptions: inline SVG chart internal coordinates may use calculated pixel values as needed for axes, bars, and labels.

---

## Typography

| Role | Size | Weight | Line Height |
|------|------|--------|-------------|
| Body | 14px | 400 | 1.5 |
| Label | 11px | 700 | 1.2 |
| Small metric label | 10px | 700 | 1.2 |
| Panel heading | 18px | 600 | 1.3 |
| Page heading | 30px | 700 | 1.2 |
| KPI score | 32px | 800 | 1.0 |

Typography rules:
- Use uppercase tracking only for small metric labels and table headers, matching existing performance UI.
- KPI score numbers should be prominent but not hero-sized; max `text-4xl`.
- Long member names must truncate inside cards and tables instead of expanding layout.
- Button text must fit without wrapping on desktop; on mobile, icon-only buttons require `title` text.

---

## Color

| Role | Value | Usage |
|------|-------|-------|
| Dominant (60%) | `#030712` / Tailwind `gray-950` | Page background |
| Secondary (30%) | `#111827` / Tailwind `gray-900` | Panels, tables, filters, card surfaces |
| Accent (10%) | `#4f46e5` / existing `primary-600` | Active tab, primary export action, selected filter, main line/bar highlight |
| Success | `#10b981` / emerald | Healthy KPI score, completed/resolved signals |
| Warning | `#f59e0b` / amber | Watchlist, slipping trend, at-risk status |
| Destructive | `#ef4444` / red | Critical KPI warnings and destructive reset confirmation only |
| Informational | `#06b6d4` / cyan | Feature/task type chart segment where needed |

Accent reserved for:
- Active navigation/tab state
- Primary chart series when only one series exists
- Primary CTA: `Export KPI CSV`
- Selected filters
- KPI score ring/progress highlight

Color constraints:
- Do not make every chart `primary`/purple. Multi-series charts must use distinct semantic colors by task type: feature cyan, bug red, task gray, improvement emerald.
- Red/amber/emerald labels must always include a textual reason, not color alone.
- The dashboard must not introduce beige, pastel, or marketing gradient palettes.

---

## Component Contracts

### Member KPI Scorecard

Each scorecard must show:
- Member avatar/initials and name.
- Numeric KPI score out of 100.
- Trend indicator: `up`, `down`, or `flat`.
- Top reason labels, max 3, such as `Cycle time rising`, `High defect load`, `Balanced workload`.
- Metric breakdown row: workload, velocity/completion, cycle time, on-time rate, defects.
- `View detail` affordance linking to `/performance/{user_id}` or opening a member drill-down.

States:
- Empty member data: show `No completed work in this period` and keep the card visible if the member is in scope.
- Warning score: show amber border and reason label.
- Critical score: show red border and first reason label; do not hide the numeric score.

### Exception List

Overview must include a concise list titled `Needs attention`.

Each item must include:
- Member name.
- Trigger reason.
- Metric value causing the trigger.
- Drill-down action.

Empty state copy: `No members need attention for the selected period.`

### Chart Panels

Every chart panel must include:
- Heading.
- Date/scope subtitle.
- View-specific filters or visible selected-filter chips.
- `Export CSV` button.
- Optional drill-down hint on clickable data points.
- Empty state with a reason and next step.

Required chart panels:
- Velocity by sprint/member.
- Burndown for active/closed sprint.
- Cycle time by task type.
- Throughput by member and type.
- Bugs reported vs resolved.
- MTTR by member.

### Drill-Down

Drill-down may be a modal, side panel, or linked filtered detail view. It must show:
- Title matching the clicked slice.
- Applied filters.
- Underlying task list with task title, type, assignee, project, sprint, status, created date, completed date.
- Export button for the drill-down task list.
- Close/back action that preserves the current dashboard tab and filters.

### Filters

Use familiar controls:
- Select/menu for sprint, project, member, task type.
- Date range inputs for custom ranges.
- Segmented controls for preset windows where useful.
- Clear/reset filters button.

Required behavior:
- Filters are view-specific.
- Changing filters should update only the current tab's content.
- Defaults must match requirement windows: last 6 sprints, active sprint, last 3 months, last 8 weeks, and last 30 days.

### KPI Weight Settings

Settings tab must expose editable weights for:
- Workload balance.
- Completion/velocity.
- Cycle time.
- On-time rate.
- Defect/quality metrics.

Controls:
- Use numeric inputs or sliders with visible percentage values.
- Show total weight and prevent saving if total is not 100%.
- Provide `Save weights` and `Reset defaults`.
- Show a short formula explanation in plain language.

Destructive confirmation copy for reset:
`Reset KPI weights? This restores the default scoring formula for this performance dashboard.`

---

## Copywriting Contract

| Element | Copy |
|---------|------|
| Page title | Performance Dashboard |
| Page subtitle | Track member KPI health, sprint delivery, and quality trends. |
| Primary CTA | Export KPI CSV |
| Overview tab empty state heading | No KPI data for this period |
| Overview tab empty state body | Adjust filters or wait for completed tasks to appear in the selected window. |
| Needs attention empty state | No members need attention for the selected period. |
| Chart empty state heading | Not enough data |
| Chart empty state body | This chart needs completed tasks in the selected scope. |
| Error state | Performance data could not be loaded. Retry or adjust the current filters. |
| Settings save success | KPI weights updated. |
| Settings validation error | Total weight must equal 100%. |
| Destructive confirmation | Reset KPI weights? This restores the default scoring formula for this performance dashboard. |

Do not add in-app tutorial text explaining how tabs, filters, or charts work. Controls should be self-explanatory through labels and tooltips.

---

## Accessibility and Interaction

- All buttons need visible text or a `title` for icon-only controls.
- Tab buttons must expose selected state visually and via `aria-current` or equivalent Svelte markup.
- Filter labels must be associated with inputs.
- Chart data must have table/list fallback through drill-down or accessible labels.
- Do not rely on hover alone for critical values; mobile users must see labels or tap targets.
- Clickable chart bars/points must have at least 32px effective target size where practical.
- CSV export must be keyboard accessible.

---

## Registry Safety

| Registry | Blocks Used | Safety Gate |
|----------|-------------|-------------|
| shadcn official | none | not required |
| third-party registries | none | not allowed without explicit review |

Chart library safety:
- `layerchart` is installed as `next` but current code comments say it was removed/bypassed.
- Planner may choose inline SVG or a verified chart helper.
- If using `layerchart`, first create a small isolated proof that imports compile and one chart renders before replacing dashboard charts.
- Do not add new charting packages in Phase 16 unless explicitly approved.

---

## Checker Sign-Off

- [x] Dimension 1 Copywriting: PASS
- [x] Dimension 2 Visuals: PASS
- [x] Dimension 3 Color: PASS
- [x] Dimension 4 Typography: PASS
- [x] Dimension 5 Spacing: PASS
- [x] Dimension 6 Registry Safety: PASS

**Approval:** approved 2026-04-26
