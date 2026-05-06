# Phase 32: Dashboard Frontend Redesign - Context

**Gathered:** 2026-05-07
**Status:** Ready for planning

<domain>
## Phase Boundary

Rebuild `frontend/src/routes/+page.svelte` into a professional, role-conditional dashboard. The new layout renders different sections based on the logged-in user's role: members see My Tasks + Activity Feed; supervisors/assistant managers/managers see KPI Summary Strip + My Tasks + Activity Feed + Team Health Panel.

This phase consumes the Phase 31 API contract (`GET /api/dashboard/` returning `my_tasks`, `team_health`, `kpi_summary`, `recent_activity`). No backend changes. No route change — dashboard stays at `/`.

</domain>

<decisions>
## Implementation Decisions

### Layout Structure
- **D-01:** Supervisor/manager layout (vertical stack, top to bottom):
  1. KPI Summary Strip (3 metric cards, full-width)
  2. Two-column row: My Tasks (left) + Activity Feed (right)
  3. Team Health Panel (full-width)
- **D-02:** Member layout (no KPI strip, no Team Health):
  1. Two-column row: My Tasks (left) + Activity Feed (right)
- **D-03:** Role check uses `isManagerOrLeader` derived store from `$lib/stores/auth` — renders supervisor+ sections conditionally with `{#if $isManagerOrLeader}`.

### My Tasks Panel
- **D-04:** Compact list — one row per task: title (truncated) + project name as small subtext. Right side: priority badge + status badge. Clicking any task navigates to `/tasks`.
- **D-05:** Overdue rows (`is_overdue: true`): red background tint (`bg-red-950/40`).
- **D-06:** Due-soon rows (`is_due_soon: true`, not overdue): yellow background tint (`bg-yellow-950/40`).
- **D-07:** Empty state: "No tasks assigned" + link to `/tasks`.

### Team Health Panel
- **D-08:** 2-3 column responsive card grid. Each member card: avatar/initials + full name + colored status dot (green = healthy, yellow = moderate, red = at-risk) + "X active · Y overdue" counts.
- **D-09:** At-risk members (red status) get a red border on their card (`border-red-500/50`).
- **D-10:** "View full performance →" link at panel footer navigates to `/performance`.
- **D-11:** Empty state: "No team members visible".

### KPI Summary Strip
- **D-12:** Three horizontal metric cards:
  1. **Avg Score** — integer, color-coded: green ≥80, yellow 60–79, red <60. Icon: TrendingUp.
  2. **Completion Rate** — displayed as percentage (e.g. "73%"). Icon: CheckSquare.
  3. **Needs Attention** — count of members with kpi_score < 70. Icon: AlertTriangle. Links to `/performance`.
- **D-13:** Strip uses same `card` class as rest of the app for visual consistency.

### Activity Feed
- **D-14:** Each activity item: avatar/initials + author name + relative time ("2h ago" via `timeAgo` util). Below: first non-empty field value from `field_values`, plain text, truncated to ~120 chars.
- **D-15:** "View all updates →" footer link navigates to `/updates`.
- **D-16:** Empty state: "No recent updates" + link to `/updates`.

### Empty States (all sections)
- **D-17:** Friendly single-line message with a CTA anchor link. Consistent `text-gray-500 text-sm py-4 text-center` styling matching existing dashboard patterns.

### Mobile Responsiveness
- **D-18:** Single-column stack on mobile (< `md` breakpoint), same section order as desktop. KPI strip cards stack to single column. Team Health card grid collapses to 2-col on mobile (already responsive from grid-cols-2 md:grid-cols-3 pattern).

### Claude's Discretion
- Exact Tailwind classes for card grid column count on each breakpoint.
- Whether to extract Team Health cards and KPI strip into separate component files or keep inline in `+page.svelte`.
- Exact status color mapping for team health `status` field values (green/yellow/red strings from API).
- Whether `dashboard.stats()` in `$lib/apis/dashboard.ts` is renamed to `dashboard.get()` or kept as-is.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase Scope & Requirements
- `.planning/ROADMAP.md` — Phase 32 goal, success criteria, requirements list
- `.planning/REQUIREMENTS.md` — DASH-01 through FEED-03 (all 15 frontend requirements for this phase)
- `.planning/PROJECT.md` — v2.4 milestone target features, out-of-scope constraints

### Phase 31 API Contract (source of truth for data shape)
- `.planning/phases/31-dashboard-api-data-contract/31-CONTEXT.md` — D-02 through D-15: exact field names, types, and role-gating rules for `my_tasks`, `team_health`, `kpi_summary`, `recent_activity`

### Existing Frontend Files to Modify/Extend
- `frontend/src/routes/+page.svelte` — Current dashboard page to rebuild
- `frontend/src/lib/apis/dashboard.ts` — API client wrapper (calls `GET /api/dashboard/`)
- `frontend/src/lib/stores/auth.ts` — `isManagerOrLeader`, `isLeader`, `isManager`, `currentUser` derived stores for role-conditional rendering

### Reusable Patterns
- `frontend/src/lib/utils.ts` — `timeAgo`, `formatDate`, `priorityColors`, `statusColors`, `statusLabels` utilities
- `frontend/src/lib/components/updates/StandupCard.svelte` — Activity card pattern (avatar, author name, timestamp, field_values rendering)
- `frontend/src/lib/components/performance/KpiScoreCard.svelte` — Member card pattern with status color logic

### Conventions
- `.planning/codebase/CONVENTIONS.md` — Svelte component structure, Tailwind-only styling, lucide-svelte icons

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `isManagerOrLeader` store (`$lib/stores/auth`): derived boolean — use `{#if $isManagerOrLeader}` to gate KPI strip and team health sections.
- `timeAgo()` util (`$lib/utils`): already imported-ready for activity feed timestamps.
- `priorityColors`, `statusColors`, `statusLabels` maps (`$lib/utils`): reuse for My Tasks badge rendering.
- `card` CSS class: already used across the app via `app.css` — use consistently for all panels.
- Lucide icons already used in current `+page.svelte`: CheckSquare, Clock, AlertTriangle, Users, TrendingUp — most KPI strip icons are already imported.

### Established Patterns
- Current `+page.svelte` uses `onMount` + async API call pattern — keep this pattern for the new `dashboard.get()` call.
- `grid grid-cols-2 lg:grid-cols-4 gap-4` pattern for responsive stat rows — adapt for KPI strip.
- `bg-gray-800 rounded-lg p-2.5 hover:bg-gray-700` for interactive list rows.

### Integration Points
- `frontend/src/lib/apis/dashboard.ts`: update `stats()` call to call new `GET /api/dashboard/` endpoint shape; return typed `DashboardPayload`.
- `frontend/src/routes/+page.svelte`: full rebuild consuming new payload; use `stats.my_tasks`, `stats.team_health`, `stats.kpi_summary`, `stats.recent_activity`.
- No new route files, no new stores needed.

</code_context>

<specifics>
## Specific Ideas

- KPI strip avg score number should be color-coded (green/yellow/red) matching the ≥80 / 60–79 / <60 thresholds already established in KpiScoreCard.svelte.
- Activity feed items should use the `timeAgo` util for relative timestamps ("2h ago") rather than full date formatting — keeps the feed feeling live.
- Team health cards should visually echo the KpiScoreCard avatar/initials pattern for visual consistency between dashboard and `/performance`.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 32-dashboard-frontend-redesign*
*Context gathered: 2026-05-07*
