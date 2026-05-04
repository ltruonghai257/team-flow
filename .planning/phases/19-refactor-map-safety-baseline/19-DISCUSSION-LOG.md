# Phase 19: Refactor Map & Safety Baseline - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md - this log preserves the alternatives considered.

**Date:** 2026-04-27
**Phase:** 19-refactor-map-safety-baseline
**Areas discussed:** Target Structure Strictness, Backend Split Granularity, Frontend Split Granularity, Safety Baseline, Migration Map Format

---

## Target Structure Strictness

| Option | Description | Selected |
|--------|-------------|----------|
| Adapted Open WebUI style | Keep `backend/app` and `frontend/src`, reorganize inside them toward Open WebUI-style groups. | yes |
| Rename backend package | Move `backend/app` toward a renamed package while keeping `frontend/` intact. | |
| Aggressive mirror | Move closer to Open WebUI's exact root shape. | |
| You decide | Let planner choose after mapping runtime impact. | |

**User's choice:** Adapted Open WebUI style.
**Notes:** The refactor should be conservative about roots and runtime targets.

| Option | Description | Selected |
|--------|-------------|----------|
| Translate concepts | Use TeamFlow-native names for Open WebUI-inspired concepts. | yes |
| Preserve names where possible | Use Open WebUI folder names even if slightly foreign. | |
| Only document reference | Use TeamFlow-native names and keep Open WebUI only as rationale. | |
| You decide | Let planner pick names case by case. | |

**User's choice:** Translate concepts.
**Notes:** Borrow structure, not product vocabulary.

---

## Backend Split Granularity

| Option | Description | Selected |
|--------|-------------|----------|
| Map slices, do not split yet | Document target modules and dependencies; Phase 20 performs moves. | |
| Plan full domain splits | Define detailed target files for every domain up front. | |
| Only split obvious support modules | Keep large model/schema modules mostly intact for now. | |
| You decide | Let planner choose after inspecting import complexity. | yes |

**User's choice:** You decide.
**Notes:** Phase 19 should expose coupling and leave split depth flexible.

| Option | Description | Selected |
|--------|-------------|----------|
| Allowed but temporary | Permit small import shims with removal notes. | yes |
| Avoid shims entirely | Update every import directly in each slice. | |
| Use broad shims first | Keep old paths working broadly, clean later. | |
| You decide | Let planner choose per module. | |

**User's choice:** Allowed but temporary.
**Notes:** Shims are safety tools, not permanent architecture.

---

## Frontend Split Granularity

| Option | Description | Selected |
|--------|-------------|----------|
| Shared lib only | Keep route files stable; split shared `src/lib` code. | |
| Shared lib plus route internals | Keep URLs stable and map large route files into route-local components. | |
| Full frontend structure pass | Reorganize shared code, route internals, and component hierarchy in one broader plan. | yes |
| You decide | Let planner choose after checking file size and coupling. | |

**User's choice:** Full frontend structure pass.
**Notes:** User added that the refactor should prioritize scalability. Route URLs and visual behavior remain protected.

| Option | Description | Selected |
|--------|-------------|----------|
| Yes, feature modules | Split API clients and shared types by feature domain; keep request/auth centralized. | yes |
| Mostly central | Split only largest domains and keep many helpers together. | |
| Route-owned | Put API/types near routes when practical. | |
| You decide | Let planner choose per domain. | |

**User's choice:** Yes, feature modules.
**Notes:** Target map should include `apis` and `types` feature-domain organization.

---

## Safety Baseline

| Option | Description | Selected |
|--------|-------------|----------|
| Full available baseline | Backend tests, Alembic check, frontend check/build, Docker/runtime review, manual smoke checklist. | yes |
| Fast baseline | Backend tests plus frontend check; document the rest. | |
| Runtime-heavy baseline | Prioritize Docker/Azure/dev smoke over broad automated checks. | |
| You decide | Let planner pick based on environment constraints. | |

**User's choice:** Full available baseline.
**Notes:** Strong baseline is needed before structural moves.

| Option | Description | Selected |
|--------|-------------|----------|
| Document block with exact fallback | Record command, failure reason, and next-best check. | yes |
| Treat blocked checks as hard stop | Do not continue until every command runs locally. | |
| Skip blocked checks silently | Keep moving if the map is clear. | |
| You decide | Let planner choose case by case. | |

**User's choice:** Document block with exact fallback.
**Notes:** Strict but not brittle.

---

## Migration Map Format

| Option | Description | Selected |
|--------|-------------|----------|
| Refactor playbook | Target structure, maps, protected behavior, commands, sequencing, and shim notes. | yes |
| Concise map only | Mostly old-to-new tables with minimal narrative. | |
| Plan-ready checklist | Organize directly as future Phase 20/21 task groups. | |
| You decide | Let planner choose artifact shape. | |

**User's choice:** Refactor playbook.
**Notes:** The output should be practical for downstream planning, not just a table.

| Option | Description | Selected |
|--------|-------------|----------|
| Separate backend/frontend tracks | Map backend and frontend independently; Phase 22 handles integration smoke. | yes |
| One combined sequence | Interleave backend/frontend moves by feature/domain. | |
| Backend first, frontend second | Stabilize backend before frontend cleanup. | |
| You decide | Let planner choose after mapping dependencies. | |

**User's choice:** Separate backend/frontend tracks.
**Notes:** Phase 20 and Phase 21 should be independently plannable after Phase 19.

## the agent's Discretion

- Backend module split depth for large modules like `models.py` and `schemas.py`.
- Exact TeamFlow-native target folder names where multiple names fit.
- Exact frontend route-local component extraction boundaries.

## Deferred Ideas

None.
