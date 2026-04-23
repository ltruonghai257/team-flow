# Phase 8: User Invite & Team Management - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-23
**Phase:** 08-user-invite-team-management
**Areas discussed:** Email delivery, Invite acceptance UX, Pending invites management, Direct-add vs invite flow differences, Role model extension

---

## Email Delivery

| Option | Description | Selected |
|--------|-------------|----------|
| fastapi-mail + SMTP env vars | Add fastapi-mail to requirements.txt; configurable via SMTP_* env vars | ✓ |
| Raw smtplib (no new dependency) | Built-in Python library, more boilerplate | |
| SendGrid HTTP API | REST API, ties to one provider | |

**User's choice:** fastapi-mail + SMTP env vars
**Notes:** Dev environment (ENVIRONMENT=development) logs token + code to console — no real SMTP. Email contains code + accept link in one email.

---

## Invite Acceptance UX

| Option | Description | Selected |
|--------|-------------|----------|
| Code entry first, then account setup | Two-step flow | |
| All fields on one page | Single form: code + username + password | ✓ |
| Auto-validate from URL | Skip code entry if code in URL params | |

**User's choice:** All fields on one page
**Notes:** Expired/invalid token shows error page with mailto link to inviter. After successful creation: success page → manual login (no auto-login).

---

## Pending Invites Management

| Option | Description | Selected |
|--------|-------------|----------|
| Section on existing /team page | Collapsible section below member cards | ✓ |
| Separate tab on /team page | Members tab + Invites tab | |

**User's choice:** Section on existing /team page

| Action | Description | Selected |
|--------|-------------|----------|
| Revoke only | Single revoke action | |
| Revoke + Resend | Both actions available | ✓ |

**User's choice:** Revoke + Resend — resend generates new token/code, resets 72h expiry.

| Visibility | Description | Selected |
|-----------|-------------|----------|
| Show all (pending + expired) | Expired have badge + Resend available | ✓ |
| Active only | Filter out expired automatically | |

**User's choice:** Show all with status labels.

---

## Direct-Add vs Invite Flow

| Option | Description | Selected |
|--------|-------------|----------|
| One button, two tabs in modal | 'Add Member' button → modal with Invite New / Add Existing tabs | ✓ |
| Two separate buttons | Side-by-side buttons, each opens own modal | |

**User's choice:** One button, two tabs inside modal.

| Role assignment | Description | Selected |
|----------------|-------------|----------|
| Role selector in invite modal | member/supervisor/SLM selectable at invite time | ✓ |
| Always invite as member | Role changed post-creation | |

**User's choice:** Role selector in invite modal (member/supervisor/SLM; admin excluded from invite assignment).

| Team model | Description | Selected |
|------------|-------------|----------|
| Direct-add activates deactivated user | No schema change | |
| Invite-only | Skip direct-add | |
| Full Team + TeamMember model | Team tables, membership tracking | ✓ |

**User's choice:** Full Team + TeamMember tables. Tasks/projects stay globally visible.

**Depth decision:** Multiple teams within the org (supervisor creates teams for department-level grouping). Tasks/projects do NOT become team-scoped.

---

## Role Model Extension

| Option | Description | Selected |
|--------|-------------|----------|
| admin / supervisor / SLM / member | 4 roles | |
| admin / manager / supervisor═SLM / member | 4-tier, manager added | ✓ |

**User's choice:** admin > manager > (supervisor = SLM, peer) > member
- SLM, supervisor, and assistant_manager are the same permission tier (user confirmed "same level")
- Final model: admin / manager / supervisor / SLM / member (5 enum values)

| Migration | Description | Selected |
|-----------|-------------|----------|
| Extend existing enum (Alembic ALTER TYPE) | Add manager + SLM, keep existing values | ✓ |
| Full re-model | Drop and replace enum | |

**Performance scoping:**
- admin + manager: see all teams
- supervisor + SLM: see only their led team(s)

**Team creation:**
- admin + manager only can CREATE teams
- supervisor + SLM + manager + admin can all INVITE to teams they lead

---

## Claude's Discretion

- Modal tab component (reuse existing modal pattern)
- Email HTML template design
- Token/code generation implementation details
- Alembic migration sequencing

## Deferred Ideas

- Auto-login after invite acceptance
- Team-scoped task/project visibility
- Admin role via invite modal
- Multi-team dashboard aggregation for managers
