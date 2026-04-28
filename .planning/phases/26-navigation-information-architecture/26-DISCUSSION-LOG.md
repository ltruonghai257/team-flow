# Phase 26: Navigation Information Architecture - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-29
**Phase:** 26-navigation-information-architecture
**Areas discussed:** Navigation Grouping, Expansion Behavior, Active Route Signal, Role-Aware Visibility

---

## Navigation Grouping

| Question | Selected | Alternatives Considered |
|----------|----------|-------------------------|
| How should TeamFlow's sidebar groups be organized? | Workflow areas | Object areas; current order with section headers; other |
| How should child pages be placed inside groups? | Dashboard: Dashboard; Work: Projects, Tasks; Planning: Milestones, Timeline, Schedule; Team: Team, Updates, Weekly Board, Performance; AI: AI Assistant | Move Schedule into Team; move Updates and Weekly Board into Work; other |
| What parent labels should the sidebar use? | Dashboard, Work, Planning, Team, AI | Home, Execution, Planning, People, AI; Overview, Work, Timeline, People, Assistant; other |
| Should Performance sit inside Team and remain visible only to supervisor/admin-style users? | Yes, Team-only and privileged | Put Performance under Dashboard; make Performance top-level when visible; other |

**User's choice:** Workflow grouping with exact parent labels and Performance under Team.
**Notes:** This matches the milestone decision to group navigation by workflow area rather than raw route list.

---

## Expansion Behavior

| Question | Selected | Alternatives Considered |
|----------|----------|-------------------------|
| How should parent sections behave by default? | Auto-expand the active section, let users manually expand/collapse others | All expanded; accordion mode; other |
| Should the sidebar remember manually opened/closed sections? | Remember within the current browser session only | Reset on page load; persist with localStorage; other |
| When a user taps a child route in the mobile drawer, what should happen? | Navigate and close the drawer | Keep drawer open; close after route-change delay; other |
| Should parent rows be navigable or only expand/collapse? | Parent rows only expand/collapse; child rows navigate | Parent navigates to default child with separate chevron; contextual parent behavior; other |

**User's choice:** Active section auto-expands; manual state is session-only; child links navigate; parent rows only toggle.
**Notes:** No new parent routes should be introduced.

---

## Active Route Signal

| Question | Selected | Alternatives Considered |
|----------|----------|-------------------------|
| How strongly should the active parent section be highlighted? | Subtle parent highlight plus strong child highlight | Strong highlight on both; child highlight only; other |
| What visual cue should mark the active child route? | Existing blue-tinted background/text plus right chevron | Blue tint without chevron; left accent bar; other |
| What cue should show parent expanded/collapsed state? | ChevronDown/ChevronRight beside the parent label | Plus/minus icons; no icon; other |
| Should active child route detection use prefix matching for nested pages? | Yes, prefix matching per child route | Exact route matching; custom matching per route; other |

**User's choice:** Parent context should be visible but quiet; child route remains the strongest signal.
**Notes:** Nested pages such as `/performance/[id]` and `/schedule/knowledge-sessions` should keep the correct child highlighted.

---

## Role-Aware Visibility

| Question | Selected | Alternatives Considered |
|----------|----------|-------------------------|
| How far should navigation permissions go in Phase 26? | Use current roles now, design nav data shape to accept Phase 29 visibility later | Implement full future role model now; only regroup visually; other |
| Which current role behavior should Phase 26 preserve? | Members see normal pages except privileged Performance/admin routes; supervisor/admin-style users see Performance | Members see fewer pages immediately; everyone sees same nav but blocked pages redirect; other |
| For hidden items, remove them or show disabled? | Remove hidden items entirely | Show disabled items with lock icons; show parent groups but omit hidden children; other |
| What should happen if all children in a parent group are hidden? | Hide empty parent groups | Show disabled parent; keep only if parent has default route; other |

**User's choice:** Preserve current role behavior while making the nav data future-ready for Phase 29.
**Notes:** Phase 29 owns the broader scoped leadership visibility model.

---

## the agent's Discretion

- Exact styling values for subtle parent highlight, spacing, indentation, and transition timing.
- Concrete TypeScript data structure for grouped navigation, provided it supports future visibility metadata.

## Deferred Ideas

- `2026-04-26-status-transition-graph-workflow.md` was reviewed but not folded because workflow rules are outside Phase 26 navigation IA.
