# Phase 18: Status Transition Graph - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-26
**Phase:** 18-status-transition-graph
**Areas discussed:** Transition Editing UI, Enforcement Rules, User Feedback, Project Override Behavior

---

## Transition Editing UI

| Question | Options Presented | User's Choice |
|----------|-------------------|---------------|
| How should supervisors/admins edit transition rules? | Matrix table; Visual graph; Hybrid; You decide | Hybrid |
| How strict should validation be while supervisors configure rules? | Warnings only; Block invalid graphs; Minimal validation; You decide | You decide |
| What should the preview part of the hybrid editor show? | Compact flow preview; Warnings summary only; Full graph view; You decide | Full graph view |
| Where should transition rules live inside the existing status manager? | Expandable section under statuses; Tabs inside StatusSetManager; Separate modal/panel; You decide | You decide |
| Should there be a quick-start action when a status set has no transition rules yet? | Generate linear flow; Start empty; Use common defaults; You decide | Generate linear flow |
| Should supervisors be able to add self-transitions? | Hide/disable self-transitions; Allow self-transitions; You decide | Hide/disable self-transitions |
| Should transition editing include archived statuses? | Active statuses only; Show archived read-only; Include archived fully; You decide | Active statuses only |

**Notes:** Matrix/table is the primary editor. The graph is read-only preview. Empty transition list preserves free movement until rules are created.

---

## Enforcement Rules

| Question | Options Presented | User's Choice |
|----------|-------------------|---------------|
| What happens if a task has no current `custom_status_id` yet? | Resolve then enforce; Allow first move; Reject until normalized; You decide | Resolve then enforce |
| Should transition enforcement run only when status changes, or also when related fields change? | Status changes only; Any task update; Status and project changes; You decide | Status and project changes |
| If a status set has at least one transition defined, should all non-listed transitions be blocked? | Yes, strict allowlist; Per-status strictness; Require explicit enable flag; You decide | Yes, strict allowlist |
| How should transitions into `is_done` statuses behave? | No special treatment; Always allow into done; Require path to done warning only; You decide | No special treatment |
| How should blocked transitions be represented in the backend response? | HTTP 422 with structured detail; HTTP 422 with simple message; HTTP 400; You decide | HTTP 422 with structured detail |

**Notes:** Ordinary task edits should not be blocked. Project changes must validate/remap safely because they can change the effective status set.

---

## User Feedback

| Question | Options Presented | User's Choice |
|----------|-------------------|---------------|
| For Kanban drag-drop, should blocked moves be prevented before the drop or reverted after the drop attempt? | Prevent before drop; Allow drop then revert with toast; Hybrid; You decide | Hybrid |
| For the toast/error message, what tone should blocked moves use? | Direct rule message; Actionable message; Admin-focused message; You decide | You decide |
| For the task edit form status dropdown, how should restricted statuses appear? | Show only allowed statuses; Show all, disable blocked ones; Allowed statuses plus current status; You decide | Allowed statuses plus current status |
| Should the UI show workflow hints on Kanban column headers? | Small hint icons only; Visible allowed-next labels; No header hints; You decide | Small hint icons only |
| When rules change while users already have the board open, how fresh does the client-side transition data need to be? | Refresh on status-set reload only; Refresh after blocked backend response; Live refresh; You decide | Refresh after blocked backend response |

**Notes:** Frontend can use known transition data for hints, but backend remains final authority.

---

## Project Override Behavior

| Question | Options Presented | User's Choice |
|----------|-------------------|---------------|
| When creating a project-specific status override, what should happen to transition rules? | Copy matching transitions; Start with no rules; Ask during override creation; You decide | Copy matching transitions |
| When reverting a project override back to the sub-team default set, what should happen to project transition rules? | Discard project rules; Map rules back if possible; Require explicit confirmation; You decide | Discard project rules |
| Should deleting or archiving a status automatically clean up transitions involving that status? | Yes, delete affected transitions; Archive keeps rules hidden; Block until rules are removed manually; You decide | Archive keeps rules hidden |
| Should the transition API expose all transitions for the status set, including archived-status transitions, or only active-status transitions? | Active only by default; All transitions always; Query option; You decide | Query option |
| If default status-set transition rules change later, should project overrides inherit those changes automatically? | No, overrides are independent snapshots; Yes, sync default changes; Prompt to sync; You decide | No, overrides are independent snapshots |

**Notes:** Project overrides are copied snapshots. Reverting an override deletes project-specific workflow rules with the project status set.

---

## Agent's Discretion

- Choose the exact validation implementation, biased toward non-blocking warnings.
- Choose exact placement inside `StatusSetManager`, with tabs preferred if crowded.
- Choose exact blocked-move toast copy, using structured backend response detail.
- Choose exact read-only graph rendering approach, keeping matrix editing primary.

## Deferred Ideas

None.
