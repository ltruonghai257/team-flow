# Phase 21: Frontend SvelteKit Structure - Context

**Gathered:** 2026-04-27
**Status:** Ready for planning

<domain>
## Phase Boundary

Reorganize TeamFlow's SvelteKit shared frontend code into Open WebUI-style `src/lib` groups while preserving existing route URLs, API request behavior, WebSocket behavior, and visual UI behavior. This phase owns frontend API/type/module structure, import updates, and frontend verification.

This phase does not redesign UI, move SvelteKit routes, change user-facing route URLs, add dependencies, modify backend code, or perform integrated Docker/Azure runtime verification. Runtime and cross-stack regression verification belongs to Phase 22.

</domain>

<decisions>
## Implementation Decisions

### API Module Migration
- **D-01:** Split the current `frontend/src/lib/api.ts` into `frontend/src/lib/apis/*`.
- **D-02:** Use one API module per current API namespace, matching the Phase 19 map: `auth`, `users`, `projects`, `milestones`, `sprints`, `tasks`, `schedules`, `notifications`, `ai`, `chat`, `dashboard`, `performance`, `timeline`, `invites`, `status-sets`, and `sub-teams`.
- **D-03:** Keep request/auth behavior centralized in `frontend/src/lib/apis/request.ts`. Feature API modules call the shared wrapper rather than creating their own fetch logic.
- **D-04:** Keep a temporary `frontend/src/lib/api.ts` re-export shim during migration so callsites can move safely.
- **D-05:** Remove the temporary `$lib/api` shim by the end of Phase 21 after all route, component, and store callsites have migrated.

### Type Centralization
- **D-06:** Move shared/exported API-facing types into `frontend/src/lib/types`, including the existing status and reminder/notification types currently exported from `api.ts`.
- **D-07:** Use feature-domain type modules such as `status.ts`, `notification.ts`, `task.ts`, and `project.ts` when new shared type files are needed.
- **D-08:** Planner decides borderline local-vs-shared cases during import mapping. Reused API-facing types should move to `src/lib/types`; one-page or UI-only types may stay local when that is cleaner.

### Import Conventions
- **D-09:** API callsites should import namespaces from `$lib/apis`, e.g. `import { tasks, projects } from '$lib/apis';`.
- **D-10:** Shared type imports use a mixed rule: common route/component callsites may import from the `$lib/types` barrel, while API/domain internals may import direct modules like `$lib/types/status` when clearer.
- **D-11:** `request()` defaults to API-internal. The planner may expose it only if an existing callsite genuinely needs direct request access.

### Route and Component Scope
- **D-12:** Skip optional route-local component extraction in Phase 21.
- **D-13:** Keep Phase 21 surgical: API modules, type modules, import updates, frontend check/build, and focused smoke verification only.
- **D-14:** Preserve all current route URLs and visual behavior. No route reshaping or UI redesign is part of this phase.

### the agent's Discretion
- Exact batch order for extracting low-coupling versus high-usage API modules, provided checks run after risky slices.
- Exact local-vs-shared placement for borderline types discovered during the importer map, provided reused API-facing types move to `src/lib/types`.
- Whether to expose `request()` from `$lib/apis` if a real current callsite requires it; default is internal-only.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Roadmap and Requirements
- `.planning/ROADMAP.md` - Phase 21 goal, dependency on Phase 19, success criteria, route preservation requirement, and Phase 20/21/22 sequencing.
- `.planning/PROJECT.md` - v2.1 milestone intent, Open WebUI reference, preserved behavior list, Bun preference, and no-new-dependencies constraint.
- `.planning/REQUIREMENTS.md` - FRONT requirements and v2.1 frontend/runtime/verification constraints; note stale traceability table and defer to ROADMAP for phase numbering.
- `.planning/STATE.md` - Active milestone notes, Bun preference, runtime watch-outs, and v2.1 architecture decisions.

### Prior Phase Context and Maps
- `.planning/phases/19-refactor-map-safety-baseline/19-CONTEXT.md` - Locked Phase 19 decisions for adapted Open WebUI structure, protected behavior, shim policy, and frontend scalability priority.
- `.planning/phases/19-refactor-map-safety-baseline/19-FRONTEND-MAP.md` - Target frontend structure, `api.ts` split map, type split map, migration slices F0-F7, and protected frontend behavior.
- `.planning/phases/19-refactor-map-safety-baseline/19-REFACTOR-PLAYBOOK.md` - Phase 21 handoff responsibilities, sequencing rules, and temporary shim policy.
- `.planning/phases/19-refactor-map-safety-baseline/19-SAFETY-BASELINE.md` - Protected route URLs, request behavior, WebSocket behavior, frontend verification commands, and manual smoke checklist.
- `.planning/phases/20-backend-package-restructure/20-CONTEXT.md` - Phase 20 boundary and backend/frontend separation; useful to avoid pulling backend runtime work into Phase 21.

### Existing Codebase Maps
- `.planning/codebase/STRUCTURE.md` - Current frontend layout, route files, component groups, stores, API client, WebSocket client, and config files.
- `.planning/codebase/CONVENTIONS.md` - Current frontend API client pattern, store pattern, Svelte/Tailwind conventions, and import style.
- `.planning/codebase/STACK.md` - SvelteKit, TypeScript, Bun/Yarn package context, frontend libraries, and build/check scripts.

### Reference Structure
- `https://github.com/open-webui/open-webui` - Inspiration for frontend shared-code organization. Use as a reference pattern, not as a product architecture or UI pattern to copy exactly.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `frontend/src/lib/api.ts`: Current centralized API surface. It contains the shared request wrapper, all feature API namespaces, and exported status/reminder types that will seed `lib/apis` and `lib/types`.
- `frontend/src/lib/stores/subTeam.ts`: Used by the request wrapper to inject `X-SubTeam-ID`; this behavior must remain centralized in `apis/request.ts`.
- `frontend/src/lib/stores/auth.ts`, `frontend/src/lib/stores/notifications.ts`, and `frontend/src/lib/stores/chat.ts`: Store callsites currently import API namespaces from `$lib/api` and must migrate to `$lib/apis`.
- `frontend/src/lib/components/statuses/*` and task/status routes: Heavy users of exported status types; they are primary callsites for the new `src/lib/types/status.ts`.
- `frontend/src/lib/components/NotificationBell.svelte`, `frontend/src/lib/websocket.ts`, and route files: Existing shared UI and WebSocket assets stay in place.

### Established Patterns
- API calls currently use namespace objects such as `tasks`, `projects`, `statusSets`, and `performance`.
- Request behavior must keep base URL `/api`, `credentials: 'include'`, `Content-Type: application/json`, `X-SubTeam-ID` header injection, structured error parsing, and 204 handling.
- Svelte route URLs are protected and must not move or change.
- Components are already organized by feature group under `src/lib/components`.
- Stores are already organized under `src/lib/stores`.
- The project prefers Bun for frontend operations, though `package.json` still declares Yarn metadata.

### Integration Points
- Update every `$lib/api` importer across routes, components, and stores before removing the shim.
- Create `src/lib/apis/index.ts` as the stable namespace import surface.
- Create `src/lib/types/index.ts` as the common type barrel while allowing direct type-module imports inside API/domain internals.
- Run `cd frontend && bun run check` after migration slices when dependencies are available, and `cd frontend && bun run build` before declaring Phase 21 complete.
- Use the Phase 19 manual smoke checklist for affected frontend routes after build/check, especially login/session, task board, sub-team context header, notifications, invite acceptance, and SPA fallback.

</code_context>

<specifics>
## Specific Ideas

- The temporary `$lib/api.ts` shim is migration scaffolding only; it should not survive Phase 21.
- The new API shape should be easy for future contributors to scan: domain namespaces from `$lib/apis`, shared request internals in one place, and shared API-facing types in `$lib/types`.
- Route-local cleanup is intentionally deferred so this phase stays focused on structural shared-code moves without visual drift.

</specifics>

<deferred>
## Deferred Ideas

None - discussion stayed within phase scope.

</deferred>

---

*Phase: 21-frontend-sveltekit-structure*
*Context gathered: 2026-04-27*
