# Phase 21: Frontend SvelteKit Structure - Pattern Map

**Created:** 2026-04-27
**Status:** Ready for planning

## Scope

This pattern map identifies the closest existing analogs and protected code shapes for Phase 21 frontend source reorganization.

## Target Files and Analogs

| Target | Role | Closest Existing Analog | Notes |
|--------|------|-------------------------|-------|
| `frontend/src/lib/apis/request.ts` | Shared fetch wrapper | `frontend/src/lib/api.ts` `request<T>()` | Preserve behavior exactly: `/api` base, JSON headers, `credentials: 'include'`, `X-SubTeam-ID`, error shape, 204 handling |
| `frontend/src/lib/apis/{domain}.ts` | Feature API modules | namespace objects in `frontend/src/lib/api.ts` | One file per current namespace; import `request` from `./request` |
| `frontend/src/lib/apis/index.ts` | API barrel | existing `$lib/api` namespace surface | Re-export namespaces for route/component imports from `$lib/apis` |
| `frontend/src/lib/types/status.ts` | Shared status types | exported status interfaces in `frontend/src/lib/api.ts` | Used heavily by status components and tasks route |
| `frontend/src/lib/types/notification.ts` | Shared reminder types | exported reminder interfaces in `frontend/src/lib/api.ts` | Used by team/reminder settings and notification-adjacent code |
| `frontend/src/lib/types/index.ts` | Common type barrel | no direct existing analog | Re-export common shared types for clean route/component imports |
| `frontend/src/lib/api.ts` | Temporary shim | existing API entrypoint | Re-export from `$lib/apis` and `$lib/types` during migration, then delete by end of Phase 21 |

## Protected Request Pattern

Source: `frontend/src/lib/api.ts`

The extracted request wrapper must preserve these behaviors:

- `const BASE = '/api'`
- import `subTeamStore` from `$lib/stores/subTeam`
- add `Content-Type: application/json`
- subscribe once to `subTeamStore`
- add `X-SubTeam-ID` when selected sub-team has an id
- call `fetch(`${BASE}${path}`, { ...options, headers, credentials: 'include' })`
- parse non-OK JSON errors into an `Error` carrying `detail`, `status`, and `payload`
- return `undefined` for HTTP 204
- return `res.json()` otherwise

## Namespace Extraction Pattern

Each feature API module should preserve the current namespace object shape:

```ts
import { request } from './request';

export const projects = {
    list: () => request('/projects/'),
    get: (id: number) => request(`/projects/${id}`),
    create: (data: object) =>
        request('/projects/', { method: 'POST', body: JSON.stringify(data) })
};
```

Use `import type` from `$lib/types` or direct type modules when a namespace needs shared response/request types.

## Import Migration Pattern

Current value import:

```ts
import { tasks as taskApi } from '$lib/api';
```

Target value import:

```ts
import { tasks as taskApi } from '$lib/apis';
```

Current type import:

```ts
import type { CustomStatus, StatusSet } from '$lib/api';
```

Target common type import:

```ts
import type { CustomStatus, StatusSet } from '$lib/types';
```

Target internal/direct type import when clearer:

```ts
import type { StatusTransitionPair } from '$lib/types/status';
```

## Critical Importers

The final shim-removal plan must update all `$lib/api` imports in:

- `frontend/src/routes/+layout.svelte`
- `frontend/src/routes/+page.svelte`
- `frontend/src/routes/ai/+page.svelte`
- `frontend/src/routes/invite/accept/+page.svelte`
- `frontend/src/routes/milestones/+page.svelte`
- `frontend/src/routes/performance/+page.svelte`
- `frontend/src/routes/performance/[id]/+page.svelte`
- `frontend/src/routes/projects/+page.svelte`
- `frontend/src/routes/register/+page.svelte`
- `frontend/src/routes/schedule/+page.svelte`
- `frontend/src/routes/tasks/+page.svelte`
- `frontend/src/routes/team/+page.svelte`
- `frontend/src/routes/timeline/+page.svelte`
- `frontend/src/lib/stores/auth.ts`
- `frontend/src/lib/stores/notifications.ts`
- `frontend/src/lib/components/timeline/TimelineGantt.svelte`
- `frontend/src/lib/components/sprints/SprintForm.svelte`
- `frontend/src/lib/components/sprints/SprintCloseModal.svelte`
- `frontend/src/lib/components/performance/KpiWarnButton.svelte`
- `frontend/src/lib/components/tasks/AiTaskInput.svelte`
- `frontend/src/lib/components/tasks/KanbanBoard.svelte`
- `frontend/src/lib/components/statuses/*.svelte`

## Verification Patterns

- Import inventory: `rtk rg "\\$lib/api" frontend/src`
- Type modules: `rtk rg "export interface CustomStatus|export interface ReminderSettings" frontend/src/lib/types`
- Request behavior: `rtk rg "credentials: 'include'|X-SubTeam-ID|res.status === 204|BASE = '/api'" frontend/src/lib/apis/request.ts`
- API namespaces: `rtk rg "export const auth|export const tasks|export const statusSets|export const reminderSettings" frontend/src/lib/apis`
- Final absence of shim: `rtk proxy test ! -f frontend/src/lib/api.ts`

## PATTERN MAPPING COMPLETE

