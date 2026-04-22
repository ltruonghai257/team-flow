# Phase 2: RBAC & Role Model - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-22
**Phase:** 2-rbac-role-model
**Areas discussed:** Role Enum Implementation, Initial Admin Setup, Frontend Guard Pattern, Role Promotion API, Role UI Display

---

## Role Enum Implementation

| Option | Description | Selected |
|--------|-------------|----------|
| SQLAlchemy Enum | Stricter, but requires alembic Enum migration. (Recommended since we are doing Alembic setup in Phase 1 anyway) | ✓ |
| Pydantic string validation | Keep DB as String, validate at API schema boundary. Easier migrations, less strict in raw DB. | |

**User's choice:** SQLAlchemy Enum
**Notes:** None

---

## Initial Admin Setup

| Option | Description | Selected |
|--------|-------------|----------|
| Env Var on Startup | On startup, check if INIT_ADMIN_EMAIL env var is set. If no user exists with it, create an admin user. | |
| CLI Script | Create a CLI script (e.g. python -m app.scripts.create_admin). (Recommended: Explicit, only runs when needed) | ✓ |
| One-Time Setup Endpoint | Provide a one-time setup endpoint that locks itself after the first admin is created. | |

**User's choice:** CLI Script
**Notes:** None

---

## Frontend Guard Pattern

| Option | Description | Selected |
|--------|-------------|----------|
| Client-side redirect | Check role in page component after mount. Easier, but flashes UI before redirect. | |
| Server-side load guard | Use layout load function or SvelteKit hooks to prevent sending the page at all. (Recommended for security/UX) | |

**User's choice:** "both"
**Notes:** Free-text response indicated both approaches should be combined (SSR prevention + client-side auth store checks).

---

## Role Promotion API

| Option | Description | Selected |
|--------|-------------|----------|
| PATCH /api/users/{id}/role | Standard REST patch endpoint. (Recommended: Keeps API clean) | ✓ |
| POST /api/users/{id}/promote | A custom action endpoint specifically for roles. | |

**User's choice:** PATCH /api/users/{id}/role
**Notes:** None

---

## Role UI Display

| Option | Description | Selected |
|--------|-------------|----------|
| Show badges | Display clear role badges (Admin, Supervisor) next to names. (Recommended for clarity) | ✓ |
| Hide roles | Hide roles from general view; only admins can see them. | |

**User's choice:** Show badges
**Notes:** None

---

## Claude's Discretion

None.

## Deferred Ideas

None.
