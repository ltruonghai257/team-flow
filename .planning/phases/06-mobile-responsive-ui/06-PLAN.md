---
phase: 6
slug: mobile-responsive-ui
wave: 1
status: pending
created: 2026-04-23
---

# Phase 6 Plan: Mobile-Responsive UI

## Wave 1

### Plan 01: Mobile Sidebar (Hamburger Menu)
**Wave:** 1
**Objective:** Collapse fixed sidebar to hamburger toggle on mobile with overlay backdrop.

**Files modified:**
- `frontend/src/routes/+layout.svelte`

**Tasks:**
1. Add `Menu` and `X` icon imports from lucide-svelte
2. Add `sidebarOpen` reactive state (default false)
3. Replace fixed `<aside>` with conditionally shown overlay sidebar on mobile + static sidebar on md+
4. Add hamburger button to mobile top bar
5. Close sidebar on nav link click on mobile

---

## Wave 2

### Plan 02: Responsive Content Areas
**Wave:** 2
**Depends on:** Plan 01
**Objective:** Fix content areas for mobile: kanban scroll, performance table scroll, task modal, dashboard grid.

**Files modified:**
- `frontend/src/lib/components/tasks/KanbanBoard.svelte`
- `frontend/src/routes/performance/+page.svelte`
- `frontend/src/routes/tasks/+page.svelte`

**Tasks:**
1. **KanbanBoard.svelte** — ensure outer `div` has `-webkit-overflow-scrolling: touch` and min-width enforced per column (already has overflow-x-auto, verify)
2. **performance/+page.svelte** — wrap team table in `overflow-x-auto` container
3. **tasks/+page.svelte** — ensure modal max-h allows scroll on short viewports; task modal already has `max-h-[90vh] overflow-y-auto` — verify form inputs not clipped
4. **Validation** — resize browser to 375px, verify all routes render without horizontal overflow
