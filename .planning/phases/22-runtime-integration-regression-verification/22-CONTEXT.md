# Phase 22: Runtime Integration & Regression Verification - Context

**Gathered:** 2026-04-27
**Status:** Ready for planning

<domain>
## Phase Boundary

Finalize the v2.1 Open WebUI-Style Project Structure Refactor by integrating the new backend and frontend structures into the runtime environment. This phase updates runtime entrypoints (Docker, Azure, dev scripts, supervisord, Alembic) to the new canonical paths and performs exhaustive regression verification. 

This phase does not move frontend or backend code (except to fix import bugs discovered during verification), nor does it change product behavior, UI visuals, or database schema. It is the final safety gate before declaring the v2.1 milestone complete.

</domain>

<decisions>
## Implementation Decisions

### Runtime Entrypoints
- **D-01:** Update `supervisord.conf`, `backend/Dockerfile`, and `Dockerfile` (monolith) to use the new canonical app entrypoint `app.api.main:app`. Maintain `supervisord` as the process manager for `nginx` and `uvicorn` in the monolith image.
- **D-02:** Update `alembic.ini` and `backend/alembic/env.py` to locate the correct `Base.metadata` in the new refactored structure, ensuring migration history remains intact.
- **D-03:** Verify `docker-compose.yml` mounts and startup commands function correctly with the refactored paths.

### Shim Policy
- **D-04:** Keep Phase 20 and 21 compatibility shims (e.g., `app.main`, `app.models`, `frontend/src/lib/api.ts`) as deprecated fallbacks for the duration of this milestone. 
- **D-05:** Ensure all internal project code (routes, components, scripts, tests) uses canonical paths, but leave the shims intact to protect any undetected external scripts or tools.

### Verification Floor
- **D-06:** The mandatory verification floor requires four distinct layers:
  1. **Backend Tests:** Run the full `pytest` suite.
  2. **Frontend Build:** Run `bun run check` and `bun run build`.
  3. **Playwright E2E:** Execute a full Playwright end-to-end run against the integrated container.
  4. **Manual Smoke:** Follow the manual smoke checklist defined in Phase 19 (login/session, task board, AI input, WebSocket chat, scheduler/notifications).
- **D-07:** If verification fails due to import path changes from Phase 20/21, fix those imports directly within this phase as bug fixes.
- **D-08:** Document the final verified deployment commands and any persistent environment variable changes (such as new `config.py` locations) in the milestone wrap-up.

### Smoke Test Evidence
- **D-09:** Playwright run is the evidence for flows it already covers (login/session, task board). For flows without E2E coverage (WebSocket chat connection, scheduler/notifications tick, AI task input, `/health`), record a manual checklist entry with timestamp, observed result, and the relevant HTTP/console/log snippet inline.
- **D-10:** All smoke evidence lives in a single `${phase_dir}/22-VERIFICATION.md`: smoke checklist, Playwright run summary, manual notes, and final pass/fail signoff. Reference Playwright's generated HTML report path; do not copy it.
- **D-11:** Phase 19 fallback rule applies — if a smoke check is blocked by local environment, document the exact command, the blocker, and the next-best fallback that actually ran. Phase 22 may complete with documented fallbacks as long as the canonical path is exercised at least once (CI counts).

### Migration Notes & Shim Cleanup
- **D-12:** The migration/dev-notes deliverable has three sections: (1) old→new import path table covering backend and frontend, (2) shim ledger (one row per shim with location, delegate target, owner, removal trigger), (3) runtime runbook covering how to start backend, frontend, docker compose, and Azure-style image with the new canonical entrypoints.
- **D-13:** The deliverable lives at `docs/MIGRATION-V2.1.md` (persists past milestone archival). `README.md` and `backend/CLAUDE.md` each receive a one-line pointer to it.
- **D-14:** Each shim ledger row records a concrete removal trigger plus the exact grep command that verifies zero remaining callsites outside `.planning/phases`. Phase 22 runs each grep once and records the current callsite count as the baseline. Actual removal is deferred to a future cleanup milestone (see Deferred Ideas).

### Agent's Discretion
- The specific order of running the verification suites, provided all four layers pass before the phase is marked complete.
- The exact method of fixing discovered import bugs, provided they align with the Phase 20/21 target structures.
- The exact column shape of the path table and shim ledger in `docs/MIGRATION-V2.1.md`, provided D-12 sections are present.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Roadmap and Requirements
- `.planning/ROADMAP.md` - Phase 22 goal, dependencies on Phase 20/21, and success criteria.
- `.planning/PROJECT.md` - v2.1 milestone intent and preserved behavior list.
- `.planning/STATE.md` - Active milestone notes and runtime watch-outs.

### Prior Phase Context
- `.planning/phases/19-refactor-map-safety-baseline/19-CONTEXT.md` - Protected behavior, shim policy, and verification baseline.
- `.planning/phases/20-backend-package-restructure/20-CONTEXT.md` - Backend app target changes and shim decisions.
- `.planning/phases/21-frontend-sveltekit-structure/21-CONTEXT.md` - Frontend API/type module structures.

</canonical_refs>

<code_context>
## Existing Code Insights

### Integration Points
- `supervisord.conf`: Currently references `app.main:app`. Must update the `[program:uvicorn]` command line.
- `backend/Dockerfile` & `Dockerfile` (monolith): Check for `CMD` or `ENTRYPOINT` referencing `app.main:app`.
- `backend/alembic/env.py`: Must load `target_metadata` correctly; Phase 20 moved models, so this needs verification.
- `scripts/deploy.sh` & `scripts/setup-azure.sh`: Rely on the monolith Dockerfile and Azure config; they likely do not need code changes, but their conceptual integration must be verified.
- `docker-compose.yml`: Mounts and environment variables must align with the refactored structure.

</code_context>

<specifics>
## Specific Ideas

- The goal is confidence. If a Playwright test fails because a SvelteKit API call still references a shim, fix the callsite to use the canonical `$lib/apis` path.
- The Phase 22 plan should explicitly list the four verification steps as distinct tasks to ensure none are skipped.
- `22-VERIFICATION.md` and `docs/MIGRATION-V2.1.md` are both required deliverables of this phase; neither is optional.
- Shim ledger baseline grep counts give the future cleanup milestone an objective trigger ("count is still zero") rather than a calendar deadline.

</specifics>

<deferred>
## Deferred Ideas

- Removing the deprecated compatibility shims is deferred to a future cleanup milestone to minimize immediate runtime risk.
- Changing Azure App Service SKUs or deployment architecture is out of scope for this structural refactor.

</deferred>

---

*Phase: 22-Runtime Integration & Regression Verification*
*Context gathered: 2026-04-27*
