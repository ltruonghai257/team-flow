# Phase 2: RBAC & Role Model - Context

**Gathered:** 2026-04-22
**Status:** Ready for planning

<domain>
## Phase Boundary

Formalize the role system so supervisor-only features are enforced server-side.
This includes standardizing the role database column, adding a promotion mechanism, and enforcing role-based guards on both the frontend and backend API endpoints.

</domain>

<decisions>
## Implementation Decisions

### Database Model
- **D-01 (Role Enum):** Use a SQLAlchemy Enum column for the `role` field (`admin`, `supervisor`, `member`). This is stricter and will be added via an Alembic migration (built on Phase 1's Alembic setup).

### Backend API
- **D-02 (Initial Admin):** Use a standalone CLI script (e.g. `python -m app.scripts.create_admin`) to create the first admin/supervisor on a fresh deployment.
- **D-03 (Role Promotion):** Use a standard REST pattern `PATCH /api/users/{id}/role` to handle role assignments. Only admins can use this endpoint.
- **D-04 (Role Check Dependency):** Implement a `require_supervisor` FastAPI dependency that verifies the user role is `supervisor` or `admin`.

### Frontend
- **D-05 (Guard Pattern):** Use a hybrid approach: server-side load guards (via SvelteKit load functions) to prevent unauthorized layout requests + client-side auth store checks for immediate UI feedback.
- **D-06 (UI Display):** Display visual role badges (e.g., 'Admin', 'Supervisor') next to user names on the team directory page for clear visibility.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Requirements
- `.planning/REQUIREMENTS.md` § REQ-07 — Role-Based Access Control (RBAC) Clarification

### Backend Auth
- `backend/app/auth.py` — Location for FastAPI auth dependencies (where `require_supervisor` will go)
- `backend/app/models.py` — Where `User.role` is defined
- `backend/app/routers/users.py` — Where the promotion API will be located

### Frontend Auth
- `frontend/src/lib/stores/auth.ts` — Existing auth store with `role`
- `frontend/src/routes/+layout.svelte` — Root layout where client-side guards might hook in

</canonical_refs>

<code_context>
## Existing Code Insights

### Established Patterns
- **Auth Store:** The frontend already has an `authStore` with a `User` interface that includes a `role: string` property.
- **Backend Current User:** A `get_current_user` dependency already exists in `auth.py` verifying the JWT token.
- **Database:** `User.role` is currently a string with a default `"member"`.

### Integration Points
- Add `require_supervisor` next to `get_current_user` in `auth.py`.
- Enforce the guard on `/performance` once created.

</code_context>

<specifics>
## Specific Ideas

- The user requested "both" for the frontend guard, meaning we should prevent unauthorized pages from loading via SSR but also ensure client side checks via the auth store work smoothly.
- Role badges should be clearly visible in the UI (Tailwind styling).

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 02-rbac-role-model*
*Context gathered: 2026-04-22*
