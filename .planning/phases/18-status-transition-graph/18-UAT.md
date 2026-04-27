---
status: testing
phase: 18-status-transition-graph
source:
  - 18-01-SUMMARY.md
  - 18-02-SUMMARY.md
  - 18-03-SUMMARY.md
  - 18-04-SUMMARY.md
started: 2026-04-27T00:00:00Z
updated: 2026-04-27T03:28:00Z
---

## Current Test
<!-- OVERWRITE each test - shows where we are -->

number: 1
name: Transition matrix updates immediately
expected: |
  Open the status manager on the Tasks page, switch to Transition rules, and toggle cells in the matrix.
  A checked transition should show the green saved state immediately.
  An unchecked saved transition should lose the green state immediately.
  A newly selected transition should show the orange draft state immediately in the matrix, without waiting for Save.
awaiting: user response

## Tests

### 1. Transition matrix updates immediately
expected: |
  Open the status manager on the Tasks page, switch to Transition rules, and toggle cells in the matrix.
  A checked transition should show the green saved state immediately.
  An unchecked saved transition should lose the green state immediately.
  A newly selected transition should show the orange draft state immediately in the matrix, without waiting for Save.
result: pending

### 2. Kanban drag respects transition rules
expected: |
  In Kanban view, drag a task with transition rules enabled.
  Only statuses allowed by the active transition graph stay enabled as valid drop targets.
  Disallowed statuses are visually disabled during the drag and do not accept the drop.
result: pending

### 3. Status manager route is shareable
expected: |
  Open /tasks with the status manager route state and switch between Statuses and Transition rules.
  The manager state should persist in the URL so the same tab can be reopened directly.
result: pending

### 4. Blocked moves recover correctly
expected: |
  Attempt a move that the workflow rules block.
  The move should be rejected, the board should recover to the canonical state, and a clear blocked-move message should appear.
result: pending

## Summary

total: 4
passed: 0
issues: 0
pending: 4
skipped: 0

## Gaps

[none yet]
