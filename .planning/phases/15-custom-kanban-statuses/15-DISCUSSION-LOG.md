# Phase 15: Custom Kanban Statuses - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md - this log preserves the alternatives considered.

**Date:** 2026-04-26
**Phase:** 15-Custom Kanban Statuses
**Areas discussed:** Status Set Ownership, Per-Project Override Behavior, Completion Status Rules, Status Management UI Placement, Status Deletion and Archiving, Status Reordering, AI Task Parsing Compatibility

---

## Status Set Ownership

| Option | Description | Selected |
|--------|-------------|----------|
| Per sub-team defaults | Each sub-team has its own default Kanban statuses; supervisor/admin manages them. Fits Phase 13 scoping model best. | Yes |
| One global org default | All sub-teams share the same default status set unless projects override it. Simpler migration, less flexible. | |
| Admin global + supervisor project overrides | Admin controls the default set; supervisors only customize at project level. | |

**User's choice:** Per sub-team defaults.
**Notes:** This locks default status ownership to sub-team scope.

---

## Per-Project Override Behavior

| Option | Description | Selected |
|--------|-------------|----------|
| Auto-map by canonical key | Statuses have a stable slug; matching slugs move automatically, and unmatched tasks require a chosen fallback status. | Yes |
| Manual mapping modal | Supervisor maps every custom status to a default status before switching. Safest, but more UI work. | |
| Block until empty | Project cannot switch back while any task uses a project-specific status. Simple but frustrating. | |

**User's choice:** Auto-map by canonical key.
**Notes:** Matching slugs map automatically; unmatched statuses need explicit fallback handling.

---

## Completion Status Rules

| Option | Description | Selected |
|--------|-------------|----------|
| Multiple done statuses allowed | Any status with `is_done` completes the task. Supports flows like `Done`, `Released`, `Cancelled`. | Yes |
| Exactly one done status per set | Simpler mental model and board behavior. | |
| One primary done status plus archived terminal statuses | Tasks complete on primary done; other terminal states are excluded from normal board/KPI logic. | |

**User's choice:** Multiple done statuses allowed.
**Notes:** Any `is_done` status drives `completed_at`.

---

## Status Management UI Placement

| Option | Description | Selected |
|--------|-------------|----------|
| Project settings panel inside `/projects` | Project-specific overrides are edited in project context; sub-team defaults can be reached from the same panel. | Yes |
| Board settings inside `/tasks` | Manage columns directly from the Kanban board where the effect is visible. | Yes |
| Sub-team management on `/team` | Default statuses live with team administration; project overrides live elsewhere or later. | |

**User's choice:** Both `/projects` and `/tasks`.
**Notes:** Treat `/projects` as the full settings surface and `/tasks` as the direct Kanban column-management entry point.

---

## Status Deletion and Archiving

| Option | Description | Selected |
|--------|-------------|----------|
| Block deletion | Require moving tasks first. Matches roadmap acceptance criteria exactly. | |
| Prompt to move tasks | Choose a replacement status in the delete flow, then delete. | Yes |
| Archive the status | Hide it from new tasks but keep existing tasks attached until moved. | Yes |

**User's choice:** Offer both prompt-to-move/delete and archive paths.
**Notes:** The deletion flow should expose two safe options.

---

## Status Reordering

| Option | Description | Selected |
|--------|-------------|----------|
| Immediate shared order | Drag-and-drop reorder saves instantly and all users see the new order. | Yes |
| Save/cancel draft | Supervisor reorders in an edit mode, then saves changes as a batch. | |
| Project-only previews | Changes can be previewed on the board before applying, mainly for project-specific overrides. | |

**User's choice:** Immediate shared order.
**Notes:** Reorder is saved immediately and shared across users.

---

## AI Task Parsing Compatibility

| Option | Description | Selected |
|--------|-------------|----------|
| Keep AI/status input on legacy enum for now | AI parsing continues returning `todo/in_progress/review/done/blocked`; backend maps to custom status. Lowest risk. | Yes |
| Expose custom statuses to AI parsing | AI can return project/sub-team custom statuses directly. More natural, but needs context injection and validation. | |
| No AI status assignment | AI-created tasks always start in the default first status. | |

**User's choice:** Keep AI/status input on legacy enum for now.
**Notes:** Backend mapping handles compatibility during dual-write migration.

## Agent's Discretion

- Exact schema names for status set/status tables and relationships.
- Exact API route names for status set management, as long as they follow existing router/API client patterns.
- Exact UI layout for status management controls on `/projects` and `/tasks`.
- Exact color picker implementation.

## Deferred Ideas

None.
