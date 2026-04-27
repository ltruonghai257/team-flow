# Phase 21: Frontend SvelteKit Structure - Research

**Phase:** 21 - Frontend SvelteKit Structure
**Date:** 2026-04-27
**Status:** Complete

## Research Question

What does the planner need to know to reorganize TeamFlow's frontend shared code into Open WebUI-style SvelteKit groups without changing routes, request behavior, WebSocket behavior, or visual UI behavior?

## Inputs Read

- `.planning/phases/21-frontend-sveltekit-structure/21-CONTEXT.md`
- `.planning/phases/19-refactor-map-safety-baseline/19-FRONTEND-MAP.md`
- `.planning/phases/19-refactor-map-safety-baseline/19-REFACTOR-PLAYBOOK.md`
- `.planning/phases/19-refactor-map-safety-baseline/19-SAFETY-BASELINE.md`
- `.planning/codebase/STRUCTURE.md`
- `.planning/codebase/CONVENTIONS.md`
- `.planning/codebase/STACK.md`
- `frontend/src/lib/api.ts`
- `$lib/api` importer inventory from `frontend/src`

## Primary Findings

### SvelteKit Structure Constraints

SvelteKit's documented structure treats `src/lib` as reusable library code and `src/routes` as route definitions. SvelteKit also explicitly supports colocating route-only components under `src/routes`, but Phase 21 context says route-local extraction is out of scope. Therefore Phase 21 should keep every route file in place and focus only on shared library structure.

Relevant source:
- `https://svelte.dev/docs/kit/project-structure`
- `https://svelte.dev/docs/kit/$lib`

### Open WebUI Structural Reference

Open WebUI currently uses `src/lib` groups including `apis`, `components`, `stores`, `types`, and `utils`, and its `src/lib/apis` folder is split into many domain folders. This supports TeamFlow's selected direction: adapted Open WebUI-style grouping, one API module per current TeamFlow namespace, and no product vocabulary copied from Open WebUI.

Relevant source:
- `https://github.com/open-webui/open-webui/tree/main/src/lib`
- `https://github.com/open-webui/open-webui/tree/main/src/lib/apis`

### Current TeamFlow API Surface

`frontend/src/lib/api.ts` is the main migration hotspot. It currently contains:

- shared `BASE = '/api'`
- private `request<T>()`
- `ApiError` and local `SubTeam` interfaces
- namespace exports: `auth`, `users`, `projects`, `milestones`, `sprints`, `tasks`, `schedules`, `notifications`, `ai`, `chat`, `dashboard`, `performance`, `timeline`, `invites`, `statusSets`, `sub_teams`, `reminderSettings`
- exported shared types: `StatusSetScope`, `CustomStatus`, `StatusSet`, `StatusTransition`, `StatusTransitionPair`, `ReminderSettings`, `ReminderSettingsProposal`

The request wrapper has protected behavior:

- base URL `/api`
- `credentials: 'include'`
- `Content-Type: application/json`
- `X-SubTeam-ID` from `subTeamStore`
- structured error parsing into `Error` with `detail`, `status`, and `payload`
- 204 response returns `undefined`

Planning implication: extract `request.ts` before feature modules, and keep the old `api.ts` as a temporary re-export shim only after all namespaces have canonical homes.

### Importer Map

Current `$lib/api` imports exist in routes, components, and stores:

- Routes: `+layout.svelte`, `+page.svelte`, `ai/+page.svelte`, `invite/accept/+page.svelte`, `milestones/+page.svelte`, `performance/+page.svelte`, `performance/[id]/+page.svelte`, `projects/+page.svelte`, `register/+page.svelte`, `schedule/+page.svelte`, `tasks/+page.svelte`, `team/+page.svelte`, `timeline/+page.svelte`
- Stores: `stores/auth.ts`, `stores/notifications.ts`
- Components: `timeline/TimelineGantt.svelte`, `sprints/SprintForm.svelte`, `sprints/SprintCloseModal.svelte`, `performance/KpiWarnButton.svelte`, `tasks/AiTaskInput.svelte`, `tasks/KanbanBoard.svelte`, and status components under `components/statuses`

Planning implication: final callsite migration should be its own plan after the feature modules and barrels exist. It should update value imports to `$lib/apis` and type imports to `$lib/types` or direct type modules according to the mixed rule.

### Recommended Migration Shape

1. Create `src/lib/types` first and re-export moved types through old `api.ts` while callsites still use `$lib/api`.
2. Extract `src/lib/apis/request.ts` and helper query-string utility without changing callsites.
3. Extract feature API modules in batches, then create `src/lib/apis/index.ts`.
4. Turn `src/lib/api.ts` into a temporary re-export shim from `$lib/apis` and `$lib/types`.
5. Migrate all callsites away from `$lib/api`.
6. Delete `src/lib/api.ts`.
7. Run frontend check/build and focused import/route smoke checks.

### Verification Reality

`frontend/node_modules` exists in this workspace, but `bun`, `yarn`, and `npm` are not on PATH for this shell, so I could not run `bun run check` during planning. The Phase 21 plans should still require these exact commands when the executor environment has Bun:

- `cd frontend && bun run check`
- `cd frontend && bun run build`

If Bun is missing during execution, the executor must document the blocker and run the strongest available fallback, such as invoking the local SvelteKit/svelte-check binaries through the available project runtime.

## Risks and Mitigations

| Risk | Why It Matters | Mitigation |
|------|----------------|------------|
| Request behavior drift | Auth cookies, sub-team context, and error handling are user-visible and protected | Extract `request.ts` byte-for-byte where possible; verify `credentials: 'include'`, `X-SubTeam-ID`, 204 handling, and `ApiError` fields |
| Circular type imports | API modules and components will share domain types | Keep type modules dependency-light; use `import type`; keep API modules importing types, not components/stores |
| Shim left behind | Context decision D-05 requires removal by end of Phase 21 | Make shim deletion a final task with `rg "\\$lib/api"` proving no callsites remain |
| Route or visual drift | Phase success criteria forbid route changes and UI redesign | Do not move `frontend/src/routes`; do not extract route-local components; verify route directory still contains protected route files |
| Over-broad API batch | Large extraction can obscure regressions | Batch modules by dependency risk and run `bun run check` after each material slice |

## Validation Architecture

### Automated Checks

- `rtk rg "\\$lib/api" frontend/src` after final import migration should return no callsites except none; `frontend/src/lib/api.ts` should be deleted.
- `rtk rg "credentials: 'include'|X-SubTeam-ID|res.status === 204|BASE = '/api'" frontend/src/lib/apis/request.ts` should find all protected request behaviors.
- `rtk rg "export const auth|export const tasks|export const statusSets|export const reminderSettings" frontend/src/lib/apis` should prove feature namespaces exist.
- `rtk rg "export interface CustomStatus|export interface ReminderSettings" frontend/src/lib/types` should prove shared types moved.
- `cd frontend && bun run check` should pass after each risky slice and at final.
- `cd frontend && bun run build` should pass before Phase 21 is complete.

### Manual / Focused Smoke

If the stack is available, smoke the affected frontend flows after final build:

- login/register/session
- dashboard load
- `/tasks` board load and status type usage
- `/projects`, `/milestones`, `/timeline`, `/schedule`, `/team`, `/performance`, `/ai`
- invite acceptance route
- notification bell polling
- admin sub-team switch sends `X-SubTeam-ID`

## Planner Guidance

- Keep Phase 21 source-only; do not modify backend, Docker, nginx, supervisord, or Azure runtime files.
- Do not create a UI-SPEC for this phase unless the user explicitly requests visual work. ROADMAP says `UI hint: no`, CONTEXT says no UI redesign, and the work is frontend source organization rather than visual/interface design.
- Include `<threat_model>` in every plan because security enforcement defaults to enabled.
- Include exact `read_first`, `action`, `acceptance_criteria`, and `verify` fields for every task.

## RESEARCH COMPLETE

