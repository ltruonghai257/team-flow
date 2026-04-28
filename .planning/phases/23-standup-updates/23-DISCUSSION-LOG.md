# Phase 23: Standup Updates - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-28
**Phase:** 23-standup-updates
**Areas discussed:** Template storage, Feed layout & display, Task snapshot scope, Post edit/delete UX

---

## Template storage

| Option | Description | Selected |
|--------|-------------|----------|
| Separate StandupTemplate table | One row per sub-team, JSONB field definitions. Clean schema. | |
| JSONB column on SubTeam | Add standup_template column to sub_teams table. Fewer tables. | |
| Global config with per-team overrides | Single global default, sub-teams store overrides only. | ✓ |

**User's choice:** Global config with per-team overrides

### Global default location

| Option | Description | Selected |
|--------|-------------|----------|
| Hardcoded in backend (Python constant) | Default defined in code, no DB row needed. | |
| A single app_settings row in DB | Settings table stores global default; runtime-changeable. | ✓ |

**User's choice:** A single app_settings row in DB

### Behavior when template changes

| Option | Description | Selected |
|--------|-------------|----------|
| Existing posts unaffected (snapshot preserves original fields) | Posts immutable after submission. | ✓ |
| Existing posts adapt to new template labels | Old posts show renamed labels. | |

**User's choice:** Existing posts are unaffected — snapshot preserves original field labels+values.

---

## Feed layout & display

### Post display style

| Option | Description | Selected |
|--------|-------------|----------|
| Card per post, reverse-chronological | Newest first, one card per post. | ✓ |
| Grouped by date, then by author | Posts grouped under date headers. | |
| Author-grouped (expandable rows) | One row per person, expandable. | |

**User's choice:** Card per post, reverse-chronological

### Task snapshot visibility

| Option | Description | Selected |
|--------|-------------|----------|
| Collapsed by default, expand on click | Template field text visible; snapshot hidden until toggled. | ✓ |
| Always visible inline as a small task list | Snapshot always shown below text fields. | |
| Not shown in feed — click to open full post view | Feed cards minimal, detail page/modal shows snapshot. | |

**User's choice:** Collapsed by default, expand on click

### Pagination

| Option | Description | Selected |
|--------|-------------|----------|
| Cursor-based pagination with "Load more" button | Preferred FastAPI pattern, stable with new posts. | ✓ |
| Offset-based pagination with page controls | Page 1, 2, 3 navigation. | |
| Infinite scroll | Auto-loads on scroll. | |

**User's choice:** Cursor-based pagination with "Load more" button

### Form placement

| Option | Description | Selected |
|--------|-------------|----------|
| Same page — form above the feed (or in a collapsible panel) | One-page UX, no routing. | ✓ |
| Separate route — /updates/new | Dedicated page. | |
| Modal/drawer triggered by floating button | Overlay form. | |

**User's choice:** Same page — form above the feed

---

## Task snapshot scope

### Which tasks to capture

| Option | Description | Selected |
|--------|-------------|----------|
| All tasks assigned to the member (any status) | Complete picture: todo, in-progress, done, blocked. | ✓ |
| Only active tasks (todo + in-progress) | Lighter snapshot; loses "completed since last standup". | |
| Tasks in the active sprint only | Scoped to sprint; breaks if no active sprint. | |

**User's choice:** All tasks assigned to the member (any status)

### Which task fields to capture

| Option | Description | Selected |
|--------|-------------|----------|
| id, title, status, priority, due_date (core fields) | Compact. Enough context without excess storage. | ✓ |
| id, title, status, priority, due_date, sprint name, project name | Richer context. Requires joins at snapshot time. | |
| All task fields (full row copy) | Maximum fidelity, large JSONB. | |

**User's choice:** id, title, status, priority, due_date

---

## Post edit/delete UX

### Edit method

| Option | Description | Selected |
|--------|-------------|----------|
| Inline edit — form replaces the card in the feed | In-place, no navigation. | ✓ |
| Modal/drawer | Overlay, complex with multi-field forms. | |
| Separate /updates/[id]/edit page | Clean separation, extra routing. | |

**User's choice:** Inline edit — form replaces the card in the feed

### Snapshot behavior on edit

| Option | Description | Selected |
|--------|-------------|----------|
| Keep original snapshot — edits only change text fields | Snapshot immutable after first submit. | ✓ |
| Re-freeze snapshot to current task state on edit | Snapshot updates on edit. | |

**User's choice:** Keep the original snapshot; editing only updates template field text responses.

### Delete confirmation

| Option | Description | Selected |
|--------|-------------|----------|
| Inline confirmation (Yes / No buttons appear on card) | Simple two-step, no modal. | ✓ |
| Browser confirm() dialog | Quick but inconsistent with app style. | |
| Modal confirmation dialog | More polished, more work. | |

**User's choice:** Inline confirmation — Yes/No buttons appear on the card.

---

## Claude's Discretion

- Exact table/column name for the global settings store
- Exact pagination page size (20 suggested)
- Collapsible-vs-always-open form on /updates

## Deferred Ideas

None — discussion stayed within phase 23 scope.
