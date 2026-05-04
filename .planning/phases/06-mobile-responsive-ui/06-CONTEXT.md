# Phase 6: Mobile-Responsive UI - Context

**Gathered:** 2026-04-23
**Status:** Executed inline (no subagents)

<domain>
## Phase Boundary

Make TeamFlow fully usable on 375px+ mobile viewports without changing desktop behaviour.
No new features — responsiveness pass only.

</domain>

<decisions>
## Implementation Decisions

### Sidebar
- **D-01:** Sidebar is `fixed` + `translate-x-full` on mobile, slides in on tap. On `md+` it is `static` and always visible (unchanged desktop behaviour).
- **D-02:** Backdrop (`bg-black/60`) overlays content when sidebar is open; tap-to-close. `Escape` key also closes.
- **D-03:** Every nav link fires `closeSidebar()` on click — sidebar auto-closes after navigation on mobile.
- **D-04:** Mobile top bar is `md:hidden` — hamburger + TeamFlow logo + NotificationBell. Fixed at top of the main content column. Desktop sees no top bar.

### Content Areas
- **D-05:** All route pages use `p-4 md:p-6` (or `p-4 md:p-8` for performance) — 4px base padding on mobile.
- **D-06:** Task creation modal uses `max-h-[92dvh]` (dynamic viewport height) so it never clips behind the mobile keyboard.
- **D-07:** KanbanBoard outer div gets `touch-action: pan-x pan-y` for reliable horizontal swipe on iOS. Column `max-h` accounts for mobile top bar: `calc(100vh-270px)` on mobile, `calc(100vh-220px)` on `md+`.
- **D-08:** Performance table already had `overflow-x-auto` — no change needed. Header stat cards use `flex-wrap` for small viewports.
- **D-09:** AI page conversation sidebar is `hidden sm:flex` — hidden on phones, visible from 640px+. AI chat area takes full width on mobile.
- **D-10:** AI page outer container uses `h-[calc(100dvh-48px)]` on mobile (48px = top bar height) so chat doesn't overflow.

### Claude's Discretion
- Drag-and-drop in Kanban still works on mobile touch via `svelte-dnd-action`'s built-in touch support.
- No state persistence for sidebar open/closed — always starts closed on mobile.

</decisions>

<canonical_refs>
## Canonical References

- `.planning/REQUIREMENTS.md` § REQ-06 — Mobile UI acceptance criteria
- `frontend/src/routes/+layout.svelte` — sidebar + mobile top bar
- `frontend/src/lib/components/tasks/KanbanBoard.svelte` — touch-action + max-h
- `frontend/src/routes/ai/+page.svelte` — two-panel chat layout

</canonical_refs>

---

*Phase: 06-mobile-responsive-ui*
*Context gathered: 2026-04-23*
