# 19-FRONTEND-MAP.md
# Phase 19: Frontend Target Map

**Created:** 2026-04-27
**Phase:** 19 — Refactor Map & Safety Baseline

> **Inspiration:** Open WebUI (`open-webui/open-webui`) is used as a structural reference only.
> This is not a UI redesign. Route URLs and visual behavior must remain unchanged.
> No frontend code is moved in Phase 19.

---

## Frontend Target Structure

The target keeps `frontend/src` as the SvelteKit project root. Internal shared code is reorganized into Open WebUI-inspired groups under `src/lib/`, using TeamFlow-native names.

```
frontend/
├── package.json                         # Bun project config (stays)
├── bun.lock                             # Lockfile (stays)
├── vite.config.ts                       # Vite config (stays)
├── svelte.config.js                     # adapter-static, fallback 200.html (stays, PROTECTED)
├── playwright.config.ts                 # Playwright E2E config (stays)
├── tests/                               # Playwright E2E tests (stays, PROTECTED)
│   ├── sprint_board.spec.ts
│   ├── status_transition.spec.ts
│   └── mobile/
└── src/
    ├── app.html                         # HTML template (stays)
    ├── app.css                          # Global CSS (stays)
    ├── routes/                          # SvelteKit routes — ALL URLs PROTECTED (stays)
    │   ├── +layout.svelte               # App shell: sidebar, notification bell, WS init (stays)
    │   ├── +layout.ts                   # Client-side guard / preload (stays)
    │   ├── +page.svelte                 # / — main dashboard (stays)
    │   ├── login/+page.svelte           # /login (stays)
    │   ├── register/+page.svelte        # /register (stays)
    │   ├── invite/                      # /invite/accept (stays)
    │   ├── tasks/+page.svelte           # /tasks (stays)
    │   ├── projects/+page.svelte        # /projects (stays)
    │   ├── milestones/+page.svelte      # /milestones (stays)
    │   ├── schedule/+page.svelte        # /schedule (stays)
    │   ├── timeline/+page.svelte        # /timeline (stays)
    │   ├── team/+page.svelte            # /team (stays)
    │   ├── performance/+page.svelte     # /performance (stays)
    │   ├── performance/[id]/+page.svelte # /performance/[id] (stays)
    │   └── ai/+page.svelte              # /ai (stays)
    └── lib/
        ├── apis/                        # NEW: feature API modules (split from api.ts)
        │   ├── index.ts                 # Re-exports all namespaces + shared request
        │   ├── request.ts               # Shared request() wrapper — CENTRALIZED (see below)
        │   ├── auth.ts                  # auth namespace
        │   ├── users.ts                 # users namespace
        │   ├── projects.ts              # projects namespace
        │   ├── milestones.ts            # milestones namespace
        │   ├── sprints.ts               # sprints namespace
        │   ├── tasks.ts                 # tasks namespace (includes aiParse, aiBreakdown)
        │   ├── schedules.ts             # schedules namespace
        │   ├── notifications.ts         # notifications namespace
        │   ├── ai.ts                    # ai namespace (conversations, quickChat, projectSummary)
        │   ├── chat.ts                  # chat namespace (channels)
        │   ├── dashboard.ts             # dashboard namespace
        │   ├── performance.ts           # performance namespace (KPI endpoints)
        │   ├── timeline.ts              # timeline namespace
        │   ├── invites.ts               # invites namespace
        │   ├── status-sets.ts           # statusSets namespace
        │   └── sub-teams.ts             # sub_teams + reminderSettings namespaces
        ├── types/                       # NEW: shared TypeScript type definitions by domain
        │   ├── index.ts                 # Re-exports all domain types
        │   ├── status.ts                # StatusSetScope, CustomStatus, StatusSet,
        │   │                            #   StatusTransition, StatusTransitionPair
        │   └── notification.ts          # ReminderSettings, ReminderSettingsProposal
        ├── components/                  # STAYS — already organized by feature group
        │   ├── NotificationBell.svelte  # Top-level shared component
        │   ├── chat/                    # Chat UI components
        │   ├── performance/             # KPI/performance components (8 files)
        │   ├── sprints/                 # Sprint board components (2 files)
        │   ├── statuses/                # Status set / kanban components (7 files)
        │   ├── tasks/                   # Task card/form components (5 files)
        │   └── timeline/                # Timeline view components (2 files)
        ├── stores/                      # STAYS — already well-organized
        │   ├── auth.ts                  # Auth state store
        │   ├── chat.ts                  # Chat/WS message store
        │   ├── notifications.ts         # Notification state store
        │   └── subTeam.ts               # Active sub-team selector store
        ├── utils.ts                     # STAYS (or → utils/ if expanded, Phase 21 discretion)
        └── websocket.ts                 # STAYS — WebSocket client (connects to /ws/chat), PROTECTED
```

---

## Centralized Request/Auth Behavior

**This behavior must remain centralized in `apis/request.ts` (or `apis/index.ts`) after Phase 21.**

Never split these behaviors into individual feature API modules:

| Behavior | Current Location in api.ts | Target Location |
|---|---|---|
| Base URL constant (`const BASE = '/api'`) | Top of `api.ts` | `apis/request.ts` |
| `credentials: 'include'` on all requests | `request()` function | `apis/request.ts` |
| `X-SubTeam-ID` header injection from `subTeamStore` | `request()` function | `apis/request.ts` |
| `Content-Type: application/json` header | `request()` function | `apis/request.ts` |
| Error parsing + `ApiError` construction | `request()` function | `apis/request.ts` |
| 204 No Content → `undefined` handling | `request()` function | `apis/request.ts` |

Feature API modules (`apis/auth.ts`, `apis/tasks.ts`, etc.) **must import and call `request()` from `apis/request.ts`**. They must not re-implement their own fetch calls.

---

## Current-to-Target File Map

### api.ts → apis/ Split

| Current Export | Target Module | Notes |
|---|---|---|
| `request()` (private) | `apis/request.ts` | CENTRALIZED — not re-exported to callsites; called by feature modules |
| `ApiError` interface | `apis/request.ts` | Used internally |
| `SubTeam` interface (local to request) | `apis/request.ts` OR `types/sub-team.ts` | Small, low priority |
| `auth` | `apis/auth.ts` | login uses raw fetch (form-encoded); logout + me use request() |
| `users` | `apis/users.ts` | |
| `projects` | `apis/projects.ts` | |
| `milestones` | `apis/milestones.ts` | |
| `sprints` | `apis/sprints.ts` | |
| `tasks` | `apis/tasks.ts` | Includes `aiParse`, `aiBreakdown` |
| `schedules` | `apis/schedules.ts` | |
| `notifications` | `apis/notifications.ts` | |
| `ai` | `apis/ai.ts` | Conversations, quickChat, projectSummary |
| `chat` | `apis/chat.ts` | Channels only; message flow goes through WebSocket |
| `dashboard` | `apis/dashboard.ts` | |
| `performance` | `apis/performance.ts` | KPI endpoints (kpiOverview, kpiSprint, kpiQuality, kpiMembers, kpiDrilldown, kpiWeights, updateKpiWeights, sendKpiWarningEmail) |
| `timeline` | `apis/timeline.ts` | |
| `invites` | `apis/invites.ts` | |
| `statusSets` | `apis/status-sets.ts` | Includes `getDefault`, `getEffective`, `getTransitions`, `replaceTransitions`, `createStatus`, `updateStatus`, `reorder`, `deleteStatus`, `createProjectOverride`, `revertProjectOverride` |
| `sub_teams` | `apis/sub-teams.ts` | |
| `reminderSettings` | `apis/sub-teams.ts` | Co-located with sub_teams (same domain) |

### Inline TypeScript Types → types/ Split

These types are currently defined inline in `api.ts`. Phase 21 moves them to `lib/types/`:

| Current Location in api.ts | Target Path | Type Names |
|---|---|---|
| Lines 337-374 (after statusSets section) | `lib/types/status.ts` | `StatusSetScope`, `CustomStatus`, `StatusSet`, `StatusTransition`, `StatusTransitionPair` |
| Lines 432-453 (after sub_teams section) | `lib/types/notification.ts` | `ReminderSettings`, `ReminderSettingsProposal` |

### Shared Components

Components are **already well-organized by feature group** — no renames or moves required in Phase 21.

| Current Path | Target Path | Notes |
|---|---|---|
| `lib/components/NotificationBell.svelte` | **stays** | Shared top-level component |
| `lib/components/chat/` | **stays** | Chat UI components |
| `lib/components/performance/` | **stays** | 8 performance/KPI components |
| `lib/components/sprints/` | **stays** | 2 sprint board components |
| `lib/components/statuses/` | **stays** | 7 status kanban components |
| `lib/components/tasks/` | **stays** | 5 task card/form components |
| `lib/components/timeline/` | **stays** | 2 timeline view components |

Phase 21 may optionally extract large route files into route-local component candidates (e.g., `/tasks/+page.svelte` → route-local `TaskBoard.svelte`). This is Phase 21 discretion — route URL must not change.

### Stores

| Current Path | Target Path | Notes |
|---|---|---|
| `lib/stores/auth.ts` | **stays** | |
| `lib/stores/chat.ts` | **stays** | Chat message state |
| `lib/stores/notifications.ts` | **stays** | |
| `lib/stores/subTeam.ts` | **stays** | Used by `request()` for `X-SubTeam-ID` header |

### WebSocket Client

| Current Path | Target Path | Notes |
|---|---|---|
| `lib/websocket.ts` | **stays** | PROTECTED — connects to `/ws/chat`; used by `+layout.svelte` and `stores/chat.ts` |

### Route Files

All route files **stay in their current locations**. Route URLs are PROTECTED.

| Route URL | Current File | Notes |
|---|---|---|
| `/` | `routes/+page.svelte` | |
| `/login` | `routes/login/+page.svelte` | |
| `/register` | `routes/register/+page.svelte` | |
| `/invite/accept` | `routes/invite/` | Invite acceptance flow |
| `/tasks` | `routes/tasks/+page.svelte` | |
| `/projects` | `routes/projects/+page.svelte` | |
| `/milestones` | `routes/milestones/+page.svelte` | |
| `/schedule` | `routes/schedule/+page.svelte` | |
| `/timeline` | `routes/timeline/+page.svelte` | |
| `/team` | `routes/team/+page.svelte` | |
| `/performance` | `routes/performance/+page.svelte` | |
| `/performance/[id]` | `routes/performance/[id]/+page.svelte` | Individual member detail |
| `/ai` | `routes/ai/+page.svelte` | AI task input |
| `+layout.svelte` | `routes/+layout.svelte` | App shell + WS init |
| `+layout.ts` | `routes/+layout.ts` | Guard |

### Config and Build Files

| Current Path | Target Path | Notes |
|---|---|---|
| `frontend/svelte.config.js` | **stays** | PROTECTED — `adapter-static`, `fallback: '200.html'` |
| `frontend/vite.config.ts` | **stays** | |
| `frontend/package.json` | **stays** | |
| `frontend/bun.lock` | **stays** | |
| `frontend/playwright.config.ts` | **stays** | |
| `frontend/tests/` | **stays** | |

---

## Migration Slices

Phase 21 executes the frontend restructure in small, verifiable slices. Each slice names the files it touches and the protected behavior it verifies after completion.

### Slice Order

| # | Slice Name | Files | Verification After Slice |
|---|---|---|---|
| F0 | **Non-moving prep: import inventory** | No file moves | `cd frontend && bun run check` (if deps available); grep all `from '$lib/api'` imports to produce a full importer map |
| F1 | **Create `lib/types/` with status and notification types** | New: `lib/types/status.ts`, `lib/types/notification.ts`, `lib/types/index.ts`; remove type definitions from `api.ts` | `bun run check`; confirm no type errors at callsites |
| F2 | **Extract shared `request.ts` wrapper** | New: `lib/apis/request.ts` with `request()`, `ApiError`, base URL, credentials, and sub-team header logic; keep `api.ts` importing from it | `bun run check`; verify no behavioral change to requests |
| F3 | **Extract feature API modules in batches** | New: `lib/apis/{domain}.ts` files (one batch: low-coupling modules like `timeline`, `dashboard`, `schedule`; second batch: high-usage modules like `tasks`, `performance`, `auth`) | `bun run check` after each batch; verify Svelte route files still import correctly |
| F4 | **Create `lib/apis/index.ts` barrel export** | New: `lib/apis/index.ts` re-exporting all namespaces | `bun run check`; update route/component imports from `$lib/api` to `$lib/apis` |
| F5 | **Update all route and component imports** | Update all `import ... from '$lib/api'` in routes and components to use `$lib/apis` or `$lib/apis/{domain}` | `bun run check`; confirm old `api.ts` can be removed or kept as re-export shim |
| F6 | **Route-local component extraction (optional)** | Extract large page-level logic into route-local components for any page where it improves readability — Phase 21 discretion | `bun run check`; visual smoke check affected routes |
| F7 | **Final Svelte check, build, and smoke** | No new moves | `bun run check`; `bun run build`; manual smoke checklist from 19-SAFETY-BASELINE.md; Playwright E2E if stack running |

### Slice Dependencies

```
F0 → F1 → F2 → F3 → F4 → F5 → F6 (optional) → F7
```

### Protected Behavior Each Slice Must Not Break

| Slice | Protected Behavior |
|---|---|
| All | Route URLs unchanged (no page reload breaks) |
| All | Login cookie flow (`credentials: 'include'`); `X-SubTeam-ID` header still sent |
| F1 | TypeScript types remain compatible at all callsites |
| F2 | `request()` behavior identical: auth, sub-team header, error handling, 204 handling |
| F3, F4, F5 | All API calls still reach the same backend endpoints |
| F5 | Stores that import from `$lib/api` still work (auth store, chat store, notifications store) |
| F7 | `bun run build` succeeds; adapter-static produces `build/` with `200.html` fallback |
| F7 | Playwright E2E tests pass (sprint_board, status_transition, mobile) |
