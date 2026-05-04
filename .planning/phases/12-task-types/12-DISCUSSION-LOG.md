# Phase 12: Task Types - Discussion Log

**Date:** 2026-04-24
**Purpose:** Human-readable audit trail for the Phase 12 context decisions.

## Phase Boundary

Phase 12 adds task types (`feature`, `bug`, `task`, `improvement`) to tasks. The type is visible on cards, usable as a board filter, and existing tasks are migrated to `task`.

## Gray Areas Selected

The user selected all four proposed discussion areas:

- Type picker in create/edit flow
- Card display style
- Filter behavior
- AI and autofill behavior

## Questions and Decisions

### Type Picker in Create/Edit Flow

**Question:** Where should `type` live in the task form?

**Options presented:**
- Right next to `status` and `priority` as a third small selector
- Near the title/description as a more prominent field
- Hidden under an advanced section, defaulting to `task`
- Something else

**User selected:** Right next to `status` and `priority` as a third small selector.

### Card Display Style

**Question:** How should task type appear on task cards?

**Options presented:**
- Icon plus short label badge, like `Bug` or `Feature`
- Icon-only marker with tooltip
- Colored text badge without icon
- Something else

**User selected:** Icon plus short label badge.

### Filter Behavior

**Question:** How should type filtering behave?

**Options presented:**
- Single-select filter, same style as the current status filter
- Multi-select filter, so users can show several types at once
- Type filter only on Kanban view, not list/agile
- Something else

**User selected:** Multi-select filter, so users can show several types at once.

### AI and Autofill Behavior

**Question:** How should task type be set for AI/autofill?

**Options presented:**
- AI infers type when obvious; otherwise default to `task`
- AI never sets type; all AI-created tasks default to `task`
- AI suggests a type, but user must confirm before create
- Something else

**User selected:** AI suggests a type, but user must confirm before create.

## Deferred Ideas

None.
