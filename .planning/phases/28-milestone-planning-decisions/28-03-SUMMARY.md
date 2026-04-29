---
phase: 28-milestone-planning-decisions
plan: 03
subsystem: milestones
tags:
  - command-view
  - planning-lanes
  - decision-crud
  - execution-visibility
dependency_graph:
  requires:
    - "28-02-SUMMARY.md"
  provides:
    - "Milestone command-view UI"
    - "Planning-state lanes (Planned, Committed, Active, Completed)"
    - "Expandable milestone cards with task rollups"
    - "In-context milestone decision CRUD"
  affects:
    - "frontend/src/routes/milestones/+page.svelte"
tech_stack:
  added:
    - "MilestoneLane.svelte"
    - "MilestoneCard.svelte"
    - "MilestoneDecisionForm.svelte"
  patterns:
    - "Command view with lanes"
    - "Expandable details with task/decision groupings"
    - "Embedded CRUD surface"
key_files:
  created:
    - "frontend/src/lib/components/milestones/MilestoneLane.svelte"
    - "frontend/src/lib/components/milestones/MilestoneCard.svelte"
    - "frontend/src/lib/components/milestones/MilestoneDecisionForm.svelte"
  modified:
    - "frontend/src/routes/milestones/+page.svelte"
    - "frontend/src/lib/apis/milestones.ts"
decisions:
  - "Used grid layout for lanes with mobile collapsible sections"
  - "Default expanded state for active and risky milestones"
  - "Task rows link to /tasks?task_id={id} for detail navigation"
  - "Decision CRUD lives entirely within the expanded card detail"
metrics:
  duration: "45m"
  completed_date: "2026-04-29"
---

# Phase 28 Plan 03: Milestone Command View Summary

The `/milestones` route has been completely rebuilt from a flat list into a scan-first command view. This transformation provides immediate visibility into planning states, execution progress, risk signals, and key decisions.

## Key Changes

### 1. Command View Architecture
- **Summary Metrics:** A new row at the top provides aggregate counts for active milestones, risky milestones, proposed decisions, and blocked tasks.
- **Planning Lanes:** Milestones are now organized into four distinct lanes: `Planned`, `Committed`, `Active`, and `Completed`.
- **Responsive Layout:** Lanes are rendered side-by-side on desktop and as collapsible stacked sections on mobile.

### 2. Expandable Milestone Cards
- **High-Signal Header:** Collapsed cards show title, project, due date, task progress (percent + counts), and decision tallies.
- **Risk Overlays:** Visible risk badges (`At risk`, `Delayed`, `Blocked`, `Watch`) signal attention needs without breaking lane organization.
- **Execution Visibility:** Expanded cards reveal linked tasks grouped by status (Todo, In Progress, etc.) and ordered by due date. Each task links directly to the main task detail view.

### 3. Embedded Decision CRUD
- **In-Context Records:** Milestone decisions (`Proposed`, `Approved`, `Rejected`, `Superseded`) can now be managed directly within the expanded detail surface.
- **Streamlined Workflow:** Support for creating, editing, and deleting decisions without leaving the milestone page.
- **Task Linking:** Decisions display links to associated tasks where applicable.

## Deviations from Plan

- **API Update:** Added missing decision CRUD methods (`list`, `create`, `update`, `delete`) to `frontend/src/lib/apis/milestones.ts` to support the new UI.
- **Milestone Editing:** Added an "Edit" button to the card header to preserve the existing milestone edit modal flow as required by the plan.

## Verification Results

- [x] `cd frontend && bun run check` passed with 0 errors.
- [x] `cd frontend && bun run build` completed successfully.
- [x] Lanes match the exact labels: `Planned`, `Committed`, `Active`, `Completed`.
- [x] Task links use `/tasks?task_id=` pattern.
- [x] Decisions use exact states: `Proposed`, `Approved`, `Rejected`, `Superseded`.

## Self-Check: PASSED
- [x] Created files exist.
- [x] Page uses `commandView` API.
- [x] Summary row exists.
- [x] Four lanes exist.
- [x] Task links exist.
- [x] Decision CRUD exists.
