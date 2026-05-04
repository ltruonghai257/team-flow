---
wave: 2
depends_on:
  - 01-PLAN.md
requirements: [REQ-07]

files_modified:
  - frontend/src/lib/stores/auth.ts
  - frontend/src/routes/+layout.svelte
  - frontend/src/routes/team/+page.svelte
  - frontend/src/routes/+layout.ts
autonomous: true
---

# Phase 2 - Frontend Guard Pattern & UI Display

## Objective
Enforce role checks on the frontend using SvelteKit server-side load guards and client-side auth store checks. Visually display role badges on the team directory page.

## Requirements Addressed
- REQ-07 (Role-Based Access Control Clarification)

## Tasks

```xml
<task>
  <description>Update Frontend Auth Store and Types</description>
  <read_first>
    - frontend/src/lib/stores/auth.ts
  </read_first>
  <action>
    In `frontend/src/lib/stores/auth.ts`, update the `User` interface so `role` is typed as `'admin' | 'supervisor' | 'member'` instead of `string`.
    Add derived stores: `isAdmin` and `isSupervisor` based on `currentUser.role`.
    Export these derived stores for use in components.
  </action>
  <acceptance_criteria>
    `frontend/src/lib/stores/auth.ts` contains `isAdmin = derived(...)`
    `frontend/src/lib/stores/auth.ts` contains `isSupervisor = derived(...)`
    The `User` interface role is strictly typed.
  </acceptance_criteria>
</task>

<task>
  <description>Implement Route Guards in SvelteKit</description>
  <read_first>
    - frontend/src/routes/+layout.svelte
    - frontend/src/routes/+layout.ts
  </read_first>
  <action>
    Add a check in `frontend/src/routes/+layout.svelte` (client-side) that monitors `currentUser` and the current `$page.url.pathname`.
    If the path starts with `/performance` (or `/admin`), check if the user has supervisor/admin privileges using the stores created above. If they don't, redirect to `/` using `goto('/')`.
    (Since SSR auth requires passing cookies which might not be set up yet for SvelteKit API proxy, focus on client-side store checks in `+layout.svelte` using SvelteKit's `beforeNavigate` or a reactive statement `$: if ($currentUser && !isAdmin && $page.url.pathname === '/performance') goto('/')`).
  </action>
  <acceptance_criteria>
    `frontend/src/routes/+layout.svelte` imports SvelteKit's `goto` and `page` store.
    It contains logic to redirect unauthorized users away from `/performance`.
  </acceptance_criteria>
</task>

<task>
  <description>Display Role Badges on Team Page</description>
  <read_first>
    - frontend/src/routes/team/+page.svelte
  </read_first>
  <action>
    In `frontend/src/routes/team/+page.svelte`, locate where the user's name is displayed in the list/grid.
    Add a Tailwind badge next to the name if the user's role is `admin` or `supervisor`.
    Example: `{#if user.role === 'admin'}<span class="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded-full">Admin</span>{/if}`
    Use different colors for `supervisor` (e.g., `bg-purple-100 text-purple-800`).
  </action>
  <acceptance_criteria>
    `frontend/src/routes/team/+page.svelte` contains HTML elements for role badges.
    The badges conditionally render based on `user.role`.
  </acceptance_criteria>
</task>
```

## Verification
- Attempt to navigate to `/performance` as a member; verify redirect to `/`.
- Navigate to `/team` and verify that Admin and Supervisor badges are visible on users with those roles.
## Must Haves
- [ ] Frontend routes guard based on role from auth store
- [ ] Visual UI display of badges on team members

