---
phase: 21
slug: frontend-sveltekit-structure
status: ready
nyquist_compliant: true
wave_0_complete: true
created: 2026-04-27
---

# Phase 21 - Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | SvelteKit `svelte-check`, Vite production build, Playwright E2E where stack is available |
| **Config file** | `frontend/package.json`, `frontend/tsconfig.json`, `frontend/svelte.config.js`, `frontend/playwright.config.ts` |
| **Quick run command** | `cd frontend && bun run check` |
| **Full suite command** | `cd frontend && bun run check && bun run build` |
| **Estimated runtime** | ~30-120 seconds depending on dependency cache |

---

## Sampling Rate

- **After every task commit:** Run `cd frontend && bun run check` when Bun is available.
- **After every plan wave:** Run `cd frontend && bun run check && bun run build` when Bun is available.
- **Before `$gsd-verify-work`:** Full suite must be green or exact local-environment blocker must be documented with fallback evidence.
- **Max feedback latency:** 120 seconds.

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 21-01-01 | 01 | 1 | FRONT-01 | T-21-01 | No source moves before importer map is known | grep | `rtk rg "\\$lib/api" frontend/src` | yes | pending |
| 21-01-02 | 01 | 1 | FRONT-03 | T-21-02 | Shared types move without circular imports | typecheck | `cd frontend && bun run check` | yes | pending |
| 21-02-01 | 02 | 1 | FRONT-02 | T-21-03 | Request behavior remains centralized | grep/typecheck | `rtk rg "credentials: 'include'|X-SubTeam-ID|res.status === 204|BASE = '/api'" frontend/src/lib/apis/request.ts` | yes | pending |
| 21-03-01 | 03 | 2 | FRONT-01, FRONT-02 | T-21-04 | Feature API namespaces preserve endpoints | typecheck | `cd frontend && bun run check` | yes | pending |
| 21-04-01 | 04 | 3 | FRONT-02, FRONT-03, FRONT-04, FRONT-05 | T-21-05 | No `$lib/api` shim remains; route URLs unchanged | grep/build | `rtk rg "\\$lib/api" frontend/src` and `cd frontend && bun run build` | yes | pending |

---

## Wave 0 Requirements

Existing infrastructure covers all phase requirements:

- `frontend/package.json` contains `check` and `build` scripts.
- `frontend/tsconfig.json` extends SvelteKit generated config with `strict: true`.
- `frontend/svelte.config.js` configures `$lib` alias and adapter-static fallback `200.html`.
- `frontend/tests/` contains Playwright specs for sprint board, status transitions, mobile, sidebar, status roles, task modal, and task types.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Frontend route behavior | FRONT-04, FRONT-05 | Build/typecheck cannot prove visual behavior stayed unchanged | With stack running, visit `/`, `/tasks`, `/projects`, `/milestones`, `/team`, `/timeline`, `/performance`, `/schedule`, `/ai`, `/login`, `/register`, and `/invite/accept`; confirm pages load and no visual redesign was introduced |
| Sub-team header | FRONT-02 | Requires runtime request inspection as admin | Switch sub-team as admin and confirm API requests still include `X-SubTeam-ID` |
| Notification polling | FRONT-02 | Requires authenticated runtime state | Confirm notification bell can call `/api/notifications/pending` and dismiss items |

---

## Validation Sign-Off

- [x] All planned tasks have automated verify commands or explicit environment-blocker fallback.
- [x] Sampling continuity: no 3 consecutive tasks without automated verify.
- [x] Wave 0 covers all missing references.
- [x] No watch-mode flags.
- [x] Feedback latency target is under 120 seconds.
- [x] `nyquist_compliant: true` set in frontmatter.

**Approval:** approved 2026-04-27

