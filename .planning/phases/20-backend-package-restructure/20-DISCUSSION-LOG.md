# Phase 20: Backend Package Restructure - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-27
**Phase:** 20-backend-package-restructure
**Areas discussed:** Package shape, Model/schema split depth, Compatibility shim policy, Verification floor

---

## Package Shape

| Option | Description | Selected |
|--------|-------------|----------|
| Conservative internal cleanup | Keep `backend/app` and most existing top-level names; add only obvious missing groups. | |
| Open WebUI-inspired groups | Keep `backend/app` as root, but reorganize toward clearer Open WebUI-style groups. | ✓ |
| Minimal router/runtime move only | Focus on app entrypoint, routers, Alembic, tests, and runtime imports; leave deeper grouping for later. | |
| You decide | Planner picks the safest structure using Phase 19 constraints. | |

**User's choice:** Open WebUI-inspired groups.
**Notes:** Follow-up choices locked Open WebUI-leaning names, grouping runtime-adjacent modules now, adding a new canonical app target with compatibility, using hybrid `create_app()` plus module-level `app`, and keeping routers flat by default while allowing splits for huge routers.

---

## Model/Schema Split Depth

| Option | Description | Selected |
|--------|-------------|----------|
| Full domain split now | Move models into domain files immediately. | |
| Incremental split with aggregate exports | Split by domain while preserving a package-level import surface. | ✓ |
| Enum/base split first | Move shared enums/base relationships first, split domain models only where easy. | |
| Leave models intact | Move package structure around the current large files. | |

**User's choice:** Incremental split with aggregate exports.
**Notes:** Schema split should match model domains. Cross-domain model relationships should keep tightly coupled clusters together rather than forcing tiny files. Temporary aggregate schema exports should continue working. The planner can decide whether original giant files become pure facades or retain hard-to-split leftovers temporarily.

---

## Compatibility Shim Policy

| Option | Description | Selected |
|--------|-------------|----------|
| Only `app.main`, `app.models`, `app.schemas` | Keep the riskiest public backend surfaces stable. | |
| All old top-level modules | Keep delegates for all moved top-level modules. | |
| No shims unless needed | Update imports and add shims only when breaks prove they are needed. | |
| You decide | Planner decides per module. | ✓ |

**User's choice:** Planner discretion per module.
**Notes:** Follow-up choices set the default bias toward direct import updates, with shims mainly for Alembic/runtime/test/public surfaces. Shims should be documented both inline and in a migration guide. Low-risk shims may be removed if safe, but high-risk surfaces such as `app.main`, `app.models`, and `app.schemas` should remain through Phase 22 verification. Test import migration is at planner discretion.

---

## Verification Floor

| Option | Description | Selected |
|--------|-------------|----------|
| Backend tests only | `pytest` passes after import moves. | |
| Tests + Alembic validation | Covers migration metadata and schema path safety. | |
| Tests + Alembic + uvicorn `/health` startup smoke | Proves app imports, lifespan, router registration, and health endpoint. | ✓ |
| Full backend plus frontend checks | Heavier than Phase 20 backend scope. | |

**User's choice:** Tests + Alembic + uvicorn `/health` startup smoke.
**Notes:** Focused checks should run after risky slices, with the full floor at the end. Phase 20 should include a concise backend migration guide. Smoke checks should include `/health` plus router registration/import checks; broader user-flow smoke remains Phase 22. If a verification command is blocked, document the exact blocker and run the next-best fallback.

---

## Agent's Discretion

- Exact Open WebUI-leaning group names and file boundaries.
- Exact router split candidates, limited to genuinely large/high-coupling routers.
- Exact model cluster boundaries and whether original giant files become pure facades by phase end.
- Exact compatibility shim list per module.
- Exact test import migration sequence, within the chosen compatibility policy.

## Deferred Ideas

None.
