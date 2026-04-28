# Phase 26: Navigation Information Architecture - Research

**Date:** 2026-04-29
**Scope:** Existing TeamFlow frontend navigation patterns only
**Research depth:** Level 0 - codebase pattern audit

## Summary

Phase 26 does not need external library research. The work stays inside the current SvelteKit layout, existing `lucide-svelte` icons, and the established Playwright/mobile test setup.

## Current Code Findings

### Navigation Source of Truth
- `frontend/src/routes/+layout.svelte` currently owns the full navigation structure as a flat `navItems` array.
- Active route detection already uses pathname equality plus prefix matching for non-root routes.
- Desktop and mobile already share one sidebar/drawer shell, so the grouped IA should be refactored inside the same file path instead of introducing new routes.

### Role-Aware Behavior
- `frontend/src/lib/stores/auth.ts` exposes `isSupervisor`, which currently gates Performance access.
- `+layout.svelte` also redirects non-privileged users away from `/performance` and `/admin`.
- Phase 26 should preserve this behavior while moving visibility rules into grouped nav metadata so Phase 29 can extend it.

### Mobile Interaction Baseline
- `sidebarOpen` already controls the mobile drawer.
- `closeSidebar()` already runs on link clicks and backdrop clicks.
- The grouped child links can reuse this behavior; parent rows should toggle expansion only and not navigate.

### Existing Test Coverage
- `frontend/tests/mobile/sidebar.spec.ts` already verifies drawer open/close and child-link navigation.
- The frontend toolchain supports:
  - `bun run check`
  - `bun run build`
  - `bunx playwright test ...`

## Planning Implications

1. Extract grouped navigation metadata into a dedicated frontend module so route grouping, role predicates, and future Phase 29 scope metadata have one source of truth.
2. Keep the rendering refactor centered in `frontend/src/routes/+layout.svelte` to preserve all current auth, notification, and mobile-shell behavior.
3. Extend Playwright coverage instead of inventing manual-only regression steps, then add one final visual verification checkpoint for the grouped UI.

## Constraints

- Keep public URLs unchanged.
- Keep `NotificationBell` placement intact in desktop sidebar and mobile top bar.
- Keep admin sub-team switcher behavior intact.
- Hide unauthorized items entirely; do not show disabled nav rows.
- Hide parent groups when every child is filtered out.

## Recommendation

Plan the phase in three steps:
1. Navigation data model and filtering helpers
2. Shared desktop/mobile grouped rendering in `+layout.svelte`
3. Regression coverage and final visual verification
