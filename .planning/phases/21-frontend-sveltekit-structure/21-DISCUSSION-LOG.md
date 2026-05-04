# Phase 21: Frontend SvelteKit Structure - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md - this log preserves the alternatives considered.

**Date:** 2026-04-27
**Phase:** 21-frontend-sveltekit-structure
**Areas discussed:** API module migration style, Type centralization depth, Import target convention, Optional route-local cleanup

---

## API Module Migration Style

| Option | Description | Selected |
|--------|-------------|----------|
| Temporary re-export shim | Create `$lib/apis/*`, then keep `$lib/api.ts` briefly re-exporting from the new modules while imports migrate safely. | ✓ |
| Big-bang replacement | Create new modules and update every callsite off `$lib/api` in one pass. | |
| Keep `$lib/api.ts` as permanent public API | Internally split files, but external imports keep using `$lib/api`. | |

**User's choice:** Temporary re-export shim.
**Notes:** User also chose to remove the shim by the end of Phase 21 and to use one API module per current API namespace.

---

## Type Centralization Depth

| Option | Description | Selected |
|--------|-------------|----------|
| Only shared/exported API types | Move the existing exported status and reminder types from `api.ts`, plus any API response/request types reused by multiple files. | ✓ |
| Aggressively centralize domain types | Move most route/component domain interfaces into `src/lib/types`, even if currently local. | |
| Minimal map only | Move exactly the types named in Phase 19: status and notification/reminder types, nothing else. | |

**User's choice:** Only shared/exported API types.
**Notes:** User chose planner discretion for local-vs-shared borderline cases, and feature-domain type filenames such as `status.ts`, `notification.ts`, `task.ts`, and `project.ts`.

---

## Import Target Convention

| Option | Description | Selected |
|--------|-------------|----------|
| Barrel for API namespaces | Routes/components import `{ tasks, projects }` from `$lib/apis`; domain modules stay internal and easy to reorganize. | ✓ |
| Direct domain modules | Import from `$lib/apis/tasks`, `$lib/apis/projects`, etc.; more explicit, but more import churn later. | |
| Mixed rule | Page/routes use `$lib/apis`, low-level stores/components can import direct modules when they only need one domain. | |

**User's choice:** Barrel for API namespaces.
**Notes:** For shared types, user chose a mixed rule: common callsites can import from `$lib/types`, while API/domain internals may import direct modules like `$lib/types/status`. User chose planner discretion on exposing `request()`, with default internal-only.

---

## Optional Route-Local Cleanup

| Option | Description | Selected |
|--------|-------------|----------|
| Skip route extraction | Keep Phase 21 surgical: API modules, type modules, import updates, checks/build only. | ✓ |
| Only obvious low-risk extraction | Extract route-local components only where it clearly reduces file size without touching visuals. | |
| Include a planned route cleanup slice | Treat route-local component extraction as part of Phase 21's required scope. | |

**User's choice:** Skip route extraction.
**Notes:** Phase 21 should not include route-local component reshaping or visual redesign.

---

## the agent's Discretion

- Exact batch order for API module extraction.
- Exact placement of borderline local-vs-shared types during import mapping.
- Whether to expose `request()` if an existing callsite genuinely needs it, though the default is internal-only.

## Deferred Ideas

None.
