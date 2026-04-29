# Phase 28: Milestone Planning & Decisions - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-29
**Phase:** 28-milestone-planning-decisions
**Areas discussed:** Planning state signal, Milestone detail with linked tasks, Decision visibility, Command-view layout

---

## Planning State Signal

| Decision Point | Options Considered | Selected |
|----------------|--------------------|----------|
| Source of `committed` | Derive from existing data; add explicit planning-state field; use only current status enum and UI copy; the agent decides | Derive from existing data |
| Minimum bar for `committed` | Dates plus at least one linked task; dates alone; linked tasks alone; the agent decides | Dates plus at least one linked task |
| Source of `active` | Existing milestone status; today's date inside milestone window; linked task activity; the agent decides | Existing milestone status |
| Delayed/risky display | Risk overlay on planning state; delayed as separate top-level group; existing delayed badge only; the agent decides | Risk overlay on planning state |
| Manual override | No manual override; allow later but not Phase 28; add override now; the agent decides | No manual override |

**Notes:** User chose the conservative derived-state path. Main planning lanes should remain clean, with risk shown as an overlay rather than a separate lane.

---

## Milestone Detail With Linked Tasks

| Decision Point | Options Considered | Selected |
|----------------|--------------------|----------|
| Linked task display | Expandable milestone cards; dedicated detail panel; always-visible task sections; the agent decides | Expandable milestone cards |
| Collapsed task signal | Counts by task state plus progress summary; total task count only; top 2-3 task preview; the agent decides | Counts by task state plus progress summary |
| Expanded task organization | Group by status then due date; sort by due date only; group by assignee; the agent decides | Group by status then due date |
| Task actions | View/open existing task details only; inline status changes only; full inline task editing; the agent decides | View/open existing task details only |
| Suggested tasks | Only tasks already linked; show project tasks without a milestone; show project tasks due inside milestone window; the agent decides | Only tasks already linked |

**Notes:** User kept milestone details authoritative and scoped. The milestone page should show task context without becoming a duplicate task management surface.

---

## Decision Visibility

| Decision Point | Options Considered | Selected |
|----------------|--------------------|----------|
| What counts as a decision | Structured decision entries; milestone description summary; task tags/special task types; the agent decides | Structured decision entries |
| Decision statuses | open/decided/superseded; open/decided only; proposed/approved/rejected/superseded; the agent decides | proposed/approved/rejected/superseded |
| Decision fields | Title, status, note, created date, optional linked task; title/status/note only; title/status/owner/due date/note/linked task; the agent decides | Title, status, note, created date, optional linked task |
| Card placement | Collapsed summary plus expanded detail; expanded detail only; dedicated top-page decisions section; the agent decides | Collapsed summary plus expanded detail |
| Editing support | Create/edit/delete inside milestone details; create only; read-only seeded display; the agent decides | Create/edit/delete inside milestone details |

**Notes:** User chose new structured decision persistence with product-level CRUD inside milestone details. Boundary: statuses are visible states, not a full approval routing workflow.

---

## Command-View Layout

| Decision Point | Options Considered | Selected |
|----------------|--------------------|----------|
| Page organization | Planning-state lanes; prioritized command list; dashboard summary plus single list; the agent decides | Planning-state lanes |
| Lane ordering | Risk first, then nearest due date; nearest due date only; manual order later/due date now; the agent decides | Risk first, then nearest due date |
| Default expansion | Active and risky milestones; active only; none; the agent decides | Active and risky milestones |
| Top summary metrics | Compact metrics row; lanes only; only if no extra API work; the agent decides | Compact metrics row |
| Mobile behavior | Stack lanes as collapsible sections; combined prioritized list; horizontal lane scroll; the agent decides | Stack lanes as collapsible sections |

**Notes:** User chose a lane-based command view that directly supports the Phase 28 success criteria. Mobile should preserve the same mental model with stacked collapsible sections.

---

## the agent's Discretion

- Exact badge copy, icon choices, risk thresholds, responsive spacing, empty states, and visual treatment are left to the planner/implementer.

## Deferred Ideas

- Manual planning-state override.
- Suggested task linking from unassigned or date-matching project tasks.
- Inline task status changes or full task editing inside milestone cards.
- Approval routing, sign-off ownership, and formal decision workflow automation.
- Status-transition graph / workflow rules follow-up todo remains deferred outside Phase 28.
