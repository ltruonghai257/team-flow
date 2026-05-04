# Phase 24: Knowledge Sharing Scheduler - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-28
**Phase:** 24-knowledge-sharing-scheduler
**Areas discussed:** Schedule tab shape, Presenter rules, Reminder behavior, References and tags

---

## Schedule tab shape

| Option | Description | Selected |
|--------|-------------|----------|
| Agenda-first | Dedicated Knowledge Sessions tab opens in a clean upcoming-session list | |
| Calendar-first | Dedicated tab keeps the month-grid feel and focuses on date placement | |
| Both views | Tab opens on agenda list and includes a calendar toggle inside the tab | ✓ |
| Other | User-defined custom shape | |

**User's choice:** Both views
**Notes:** Default should be agenda/list for practical browsing, with a built-in switch to calendar view inside the Knowledge Sessions tab.

---

## Presenter rules

| Option | Description | Selected |
|--------|-------------|----------|
| Required, scoped users only | Presenter is mandatory and must be selected from the allowed scope | |
| Optional, scoped users only | Presenter may be blank, but if present must be in scope | |
| Default to creator | Presenter starts as the creator, but can be reassigned within scope | ✓ |
| Other | User-defined presenter rule | |

**User's choice:** Default to creator
**Notes:** Keep creation fast, but limit reassignment to users valid for the session scope.

---

## Reminder behavior

| Option | Description | Selected |
|--------|-------------|----------|
| Single fixed reminder | One automatic reminder at a fixed lead time | |
| Selectable reminder offsets | Reuse existing reminder chips with one or more offsets | ✓ |
| Simple default now | Use one sensible reminder and leave details to implementation | |
| Other | User-defined reminder behavior | |

**User's choice:** Selectable reminder offsets
**Notes:** Align with the existing schedule reminder pattern and existing backend reminder infrastructure.

---

## References and tags

| Option | Description | Selected |
|--------|-------------|----------|
| Structured links + chip tags | Explicit reference rows and chip-style tags | |
| Freeform references + comma tags | Plain textarea references and comma-separated tags | |
| Hybrid lightweight | Freeform references textarea with chip-style tags | ✓ |
| Other | User-defined input format | |

**User's choice:** Hybrid lightweight
**Notes:** References should stay flexible and low-friction; tags should stay cleaner for browsing/filtering.

---

## the agent's Discretion

- Exact agenda/calendar toggle control shape inside the `/schedule` page
- Exact validation and placeholder language for the references textarea
- Exact tag chip interaction details, provided it remains lightweight

## Deferred Ideas

- Existing todo `2026-04-26-status-transition-graph-workflow.md` was reviewed and left outside this phase
- Attendance tracking, recurring session series, and proposal/approval workflows stay out of scope
