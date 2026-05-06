# Phase 31: Dashboard API & Data Contract - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-05-06
**Phase:** 31-dashboard-api-data-contract
**Areas discussed:** Schema Migration, my_tasks Shape, my_tasks Count & Sort, team_health Derivation, kpi_summary Sourcing, recent_activity Shape

---

## Schema Migration

| Option | Description | Selected |
|--------|-------------|----------|
| Replace in place | Overwrite DashboardStats and the existing endpoint with the new role-aware shape. Old fields gone. Phase 32 gets the clean new contract. | ✓ |
| Extend (keep old + add new) | Keep total_tasks, overdue_tasks, upcoming_milestones, recent_tasks and add new sections. Fatter response, no breakage if anything still reads old fields. | |
| New endpoint alongside | Add GET /api/dashboard/overview/ for the new shape, leave the old endpoint untouched. | |

**User's choice:** Replace in place
**Notes:** App is pre-release; no consumers of the old shape need to be preserved. Phase 32 will be built against the new contract.

---

## my_tasks Item Shape

| Option | Description | Selected |
|--------|-------------|----------|
| Slim DashboardTaskItem | id, title, project_name (string), status, priority, due_date, is_overdue, is_due_soon. Lightweight. | ✓ |
| Full TaskOut | Reuse the existing TaskOut schema (rich but large — assignee obj, custom_status obj, etc.). | |
| Slim + assignee name | Same as slim but also include assignee full_name string. | |

**User's choice:** Slim DashboardTaskItem
**Notes:** Dashboard task queue only needs to render the card; full task detail is at /tasks.

---

## my_tasks Count & Sort

| Option | Description | Selected |
|--------|-------------|----------|
| 10 tasks, overdue first then due soonest | Cap at 10 items. Overdue first (due_date asc), then upcoming (due_date asc), then no due date last. | |
| 20 tasks, overdue first then due soonest | Cap at 20 items. Same sort. Covers busy members. | ✓ |
| All assigned tasks, overdue first | No cap — return everything. Phase 32 decides how many to show. | |

**User's choice:** 20 tasks, overdue first then due soonest
**Notes:** 20 covers typical team member load without unbounded payload growth.

---

## team_health Derivation

| Option | Description | Selected |
|--------|-------------|----------|
| Reuse performance.py logic | Call the same service that populates /performance. status green/yellow/red, active_tasks, completed_30d. Consistent with performance page. | |
| Lightweight workload-only derivation | Count active tasks per member directly. Threshold: >8 active = overloaded, <3 = underloaded. Fast, no KPI computation. | |
| Reuse performance + add overdue flag | Same as reuse performance.py, but also annotate each member with overdue_tasks count. | ✓ |

**User's choice:** Reuse performance + add overdue flag
**Notes:** Overdue count enables Phase 32 to distinctly highlight at-risk members beyond just the green/yellow/red status band.

---

## kpi_summary Sourcing

| Option | Description | Selected |
|--------|-------------|----------|
| Call the existing KPI scorecard service | Extract performance.py scorecard logic into services/kpi.py. Dashboard strip always matches /performance numbers. | ✓ |
| Lightweight aggregate queries | Direct SQL aggregates on Task table. Faster but may diverge from /performance calculations. | |
| Call existing KPI overview endpoint internally | Reuse the service layer from GET /api/performance/kpi/overview. Cleaner than duplication. | |

**User's choice:** Call the existing KPI scorecard service (recommended)
**Notes:** Single source of truth prevents supervisors from seeing different numbers on dashboard vs. /performance. The extraction creates a reusable service that benefits both pages.

---

## recent_activity Item Shape

| Option | Description | Selected |
|--------|-------------|----------|
| First non-empty field value, truncated to ~120 chars | Pick first filled template field, truncate. Phase 32 renders as preview blurb. | |
| Full field_values JSONB | Return all template fields and values. Phase 32 decides what to render. More flexible. | ✓ |
| Concatenated field values, truncated to ~200 chars | Join all non-empty field responses, truncate. Richer preview without full JSONB. | |

**User's choice:** Full field_values JSONB
**Notes:** Gives Phase 32 maximum flexibility to choose the best preview field (e.g., "Pending Tasks" or "Blockers") without a second API call.

---

## Claude's Discretion

- Exact schema file placement (new `schemas/dashboard.py` vs. extend `schemas/work.py`)
- Whether role-gated sections use `Optional[X] = None` or structural omission in Pydantic model
- Exact KPI service function signature and internal structure in `services/kpi.py`
- Whether `my_tasks` done-exclusion uses `TaskStatus.done` only or also checks `custom_status.is_done`

## Deferred Ideas

None — discussion stayed within phase scope.
