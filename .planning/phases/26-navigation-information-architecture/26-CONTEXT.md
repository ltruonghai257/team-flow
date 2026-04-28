# Phase 26: Navigation Information Architecture - Context

**Gathered:** 2026-04-29
**Status:** Ready for planning

<domain>
## Phase Boundary

Reorganize TeamFlow's existing desktop sidebar and mobile drawer into workflow-based parent/child navigation sections. Existing route URLs stay stable. This phase clarifies navigation grouping, expansion behavior, active route signaling, and current-role navigation visibility. The deeper member / supervisor / assistant manager / manager scoped visibility model remains Phase 29 work.

</domain>

<decisions>
## Implementation Decisions

### Navigation Grouping
- **D-01:** Use workflow-based parent sections: Dashboard, Work, Planning, Team, and AI.
- **D-02:** Place child pages as follows:
  - Dashboard: Dashboard (`/`)
  - Work: Projects (`/projects`), Tasks (`/tasks`)
  - Planning: Milestones (`/milestones`), Timeline (`/timeline`), Schedule (`/schedule`)
  - Team: Team (`/team`), Updates (`/updates`), Weekly Board (`/board`), Performance (`/performance`)
  - AI: AI Assistant (`/ai`)
- **D-03:** Performance belongs under Team and remains visible only to supervisor/admin-style users.

### Expansion Behavior
- **D-04:** Auto-expand the active parent section and allow users to manually expand or collapse other sections.
- **D-05:** Remember manual expand/collapse state only within the current browser session.
- **D-06:** On mobile, tapping a child route navigates and closes the drawer.
- **D-07:** Parent rows are workflow containers only: they expand/collapse but do not navigate.

### Active Route Signal
- **D-08:** Use a subtle highlight for the active parent section and a stronger highlight for the active child route.
- **D-09:** Preserve the existing active child visual language: blue-tinted background/text plus the right chevron.
- **D-10:** Parent expand/collapse state should use ChevronDown/ChevronRight next to the parent label.
- **D-11:** Active child detection should use prefix matching so nested pages like `/performance/[id]` and `/schedule/knowledge-sessions` stay anchored to their parent child item.

### Role-Aware Visibility
- **D-12:** Phase 26 should enforce current-role navigation behavior now and shape the nav data so Phase 29 can add deeper scope rules later.
- **D-13:** Preserve current behavior: members see normal pages except privileged Performance/admin routes; supervisor/admin-style users see Performance.
- **D-14:** Hidden navigation items should be removed entirely, not shown disabled.
- **D-15:** Parent groups with no visible children should be hidden.

### the agent's Discretion
- Exact spacing, indentation, transition timing, and subtle parent highlight styling are left to implementation, as long as the parent and child active states remain visually distinct.
- The concrete TypeScript shape for grouped nav items is left to implementation, but it should be future-ready for Phase 29 visibility predicates or role/scope metadata.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase Scope
- `.planning/ROADMAP.md` — Phase 26 goal, dependencies, success criteria, and fixed scope boundary.
- `.planning/REQUIREMENTS.md` — NAV-01 through NAV-05 requirements and milestone out-of-scope constraints.
- `.planning/PROJECT.md` — v2.3 milestone intent, route stability decision, and navigation IA rationale.

### Current Implementation
- `frontend/src/routes/+layout.svelte` — Current flat sidebar, mobile drawer, active-route matching, auth gating, and Performance visibility behavior.
- `frontend/src/lib/stores/auth.ts` — Current user role types and derived role helpers used by navigation.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `frontend/src/routes/+layout.svelte`: Existing sidebar and mobile drawer structure should be refactored rather than replaced with new routes.
- `lucide-svelte`: Existing icon set already includes ChevronRight and ChevronDown, which should be reused for child active markers and parent expansion state.
- `NotificationBell`: Already lives inside the sidebar and mobile top bar; grouped navigation should preserve its placement and avoid duplicating notification behavior.

### Established Patterns
- SvelteKit routes live under `frontend/src/routes/`; this phase should keep those URLs unchanged.
- Frontend components use `<script lang="ts">`, Svelte reactive declarations, and Tailwind utility classes.
- Navigation currently uses `$page.url.pathname` for active route checks and `authStore` / `isSupervisor` derived stores for route visibility.

### Integration Points
- The primary integration point is `frontend/src/routes/+layout.svelte`.
- Role-aware nav filtering should connect to `frontend/src/lib/stores/auth.ts` and preserve the existing redirects that prevent non-privileged users from opening `/performance` or `/admin`.
- Mobile behavior should preserve the current `sidebarOpen` drawer state and close the drawer after child navigation.

</code_context>

<specifics>
## Specific Ideas

- The selected grouping is intentionally workflow-oriented, not object-oriented.
- Parent labels should be exactly: Dashboard, Work, Planning, Team, AI.
- Parent rows are containers only; no new parent routes should be introduced.

</specifics>

<deferred>
## Deferred Ideas

### Reviewed Todos (not folded)
- `2026-04-26-status-transition-graph-workflow.md` — Status transition graph / workflow rules was considered because it matched workflow/UI keywords, but it is not part of Phase 26 navigation IA. Keep it deferred for a future workflow-rules phase.

</deferred>

---

*Phase: 26-navigation-information-architecture*
*Context gathered: 2026-04-29*
