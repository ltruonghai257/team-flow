# Phase 14: Sprint Model - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-26
**Phase:** 14-sprint-model
**Areas discussed:** Sprint Board Layout, Sprint Close Flow, Date Enforcement, Hierarchy & Association

---

## Sprint Board Layout

| Option | Description | Selected |
|--------|-------------|----------|
| Fixed Left Column | A column on the far-left of the board that tasks can be dragged out of. Best for quick assignment. | ✓ |
| Collapsible Drawer | A toggleable sidebar drawer that slides over the board. Saves horizontal space on small screens. | |
| Separate Section | A horizontal list section above or below the board columns. Keeps columns focused on statuses. | |

**User's choice:** Fixed Left Column
**Notes:** None

---

## Sprint Close Flow

| Option | Description | Selected |
|--------|-------------|----------|
| Bulk Move All | All incomplete tasks are moved to either Backlog or the next active sprint as a single action. | |
| Per-Task Selection | A modal lists incomplete tasks, allowing the user to select destination per-task before closing. | ✓ |
| Auto-Move to Backlog | Simplest option: all automatically go to Backlog; no choice presented. | |

**User's choice:** Per-Task Selection
**Notes:** None

---

## Date Enforcement

| Option | Description | Selected |
|--------|-------------|----------|
| Strict (No Overlaps) | Sprints cannot overlap and must fit entirely within the milestone dates. UI blocks creation otherwise. | |
| Warning Only | UI warns if dates overlap or exceed the milestone, but allows creation anyway. | ✓ |
| None (Informational) | Sprint dates are purely informational labels. No validation against other sprints. | |

**User's choice:** Warning Only
**Notes:** None

---

## Hierarchy & Association

| Option | Description | Selected |
|--------|-------------|----------|
| Strict Sync | Assigning a sprint auto-sets the task's milestone to match. Mismatches not allowed. | |
| Independent Fields | Sprint and Milestone are independent fields; they can mismatch if the user wants. | ✓ |
| Sprint Owns Task | Tasks no longer belong to milestones directly; they belong to sprints, which belong to milestones. | |

**User's choice:** Independent Fields
**Notes:** None

---

## Claude's Discretion

- Exact UI design of the sprint close modal
- Visual styling of date warnings
- Responsive handling of the new fixed Backlog column

## Deferred Ideas

None