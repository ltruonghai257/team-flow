# Phase 27: Timeline & Gantt Clarity - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md - this log preserves the alternatives considered.

**Date:** 2026-04-29
**Phase:** 27-timeline-gantt-clarity
**Areas discussed:** Milestone-first layout, Task rollups inside milestones, Risk/planning/decision signals, Project vs people view continuity, Workflow signal todo

---

## Milestone-First Layout

| Question | Options Considered | Selected |
|----------|--------------------|----------|
| How should `/timeline` make milestones visually dominant? | Milestone parent rows; Milestone summary panels; Milestone lanes | Milestone parent rows |
| What should a milestone parent row show at a glance? | Title/status/date/progress; Dense risk/task counts; Minimal title/date | Title, status, date span, progress badge |
| How should task rows behave under each milestone? | Selectively expanded; All expanded; All collapsed | Expanded by default for active/risky milestones, collapsed for quiet ones |
| How should milestone rows look different from task bars? | Distinct summary row; Thicker milestone bar; Left-table emphasis only | Distinct summary row, not a normal draggable bar |

**Notes:** The selected direction keeps milestones as planning objects while preserving task bars as the editable work items.

---

## Task Rollups Inside Milestones

| Question | Options Considered | Selected |
|----------|--------------------|----------|
| What summary is visible when collapsed? | Progress plus counts by state; Progress only; Top 3 task chips | Progress badge plus task counts by state |
| How are expanded tasks organized? | Status then due date; Due date only; Assignee | Grouped by status, then due date |
| How much task detail is visible? | Title/assignee/priority/due date; Title/assignee only; Title/assignee/priority/due date/status | Title, assignee, priority, due date, and status label |
| What happens on task click? | Existing edit modal; Read-only drawer; Navigate to `/tasks` | Keep the existing edit modal |

**Notes:** The rollup should help supervisors scan execution state without leaving `/timeline`.

---

## Risk, Planning, And Decision Signals

| Question | Options Considered | Selected |
|----------|--------------------|----------|
| What counts as milestone risk? | Derived existing data; Manual risk flag; Only milestone status | Derived from existing data |
| What planning-window signal should show? | Milestone start-to-due span; Current week/month only; Both span and current marker | Milestone start-to-due span |
| How should decision points be represented? | Placeholder markers from existing text/tags; Add explicit data now; Defer entirely | Placeholder markers from milestone description/tags only if already present |
| How should signals look? | Small row badges/icons; Gantt overlays; Right-side signal column | Small badges/icons on milestone rows |

**Notes:** New risk persistence and explicit decision persistence were rejected for Phase 27 to keep the phase inside existing data and leave full decisions work to Phase 28.

---

## Project Vs People View Continuity

| Question | Options Considered | Selected |
|----------|--------------------|----------|
| What remains anchored when switching views? | Date range only; Date range plus expanded state; Date range plus highlighted milestone/task | Date range plus highlighted milestone/task |
| How does member view show milestone context? | Task milestone badges/links; Nested milestones under member; Summary strip | Task rows include milestone badges/links |
| What if focused milestone is not naturally visible? | Focused milestone banner; Auto-scroll nearest task; Drop highlight | Compact focused milestone banner |
| How is focus set? | Click milestone/task row; Dedicated focus button; Query-param only | Click milestone row or task row |

**Notes:** Member view should remain people-first while carrying enough milestone context to satisfy TL-04.

---

## Workflow Signal Todo

| Question | Options Considered | Selected |
|----------|--------------------|----------|
| How should Phase 27 treat `Status transition graph / workflow rules (YouTrack-style)`? | Use only blocked/status signal in timeline risk; Include workflow-rule visualization; Leave fully deferred | Use only blocked/custom-status signal in timeline risk |

**Notes:** The broader workflow-rule visualization remains deferred.

## the agent's Discretion

- Exact badge copy, icon selection, color thresholds, empty states, and responsive spacing.

## Deferred Ideas

- Workflow-rule graph editor and workflow-rule visualization.
- Explicit milestone decision persistence and decision lifecycle handling.
