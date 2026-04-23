---
phase: "08"
slug: "user-invite-team-management"
status: complete
nyquist_compliant: true
wave_0_complete: true
created: "2026-04-24"
---

# Validation: User Invite & Team Management (Phase 8)

## Completed Tasks

### Wave 1: Backend Model & Migration
- [x] `TeamInvite` model with `email`, `role`, `token` (unique), `validation_code`, `status`, `expires_at`
- [x] Alembic migration for `team_invites` table
- [x] `InviteStatus` enum: pending, accepted, expired, cancelled

### Wave 2: Backend API & Email
- [x] `POST /api/teams/invite` — send invite with 6-digit code + token (72h expiry)
- [x] `POST /api/teams/add` — direct-add existing user (supervisor/admin only)
- [x] `GET /api/invites/validate?token=…` — validate token + return metadata
- [x] `POST /api/invites/accept` — accept with code → create user + set cookie
- [x] `GET /api/invites/pending` — list pending invites (supervisor/admin only)
- [x] `DELETE /api/invites/{id}` — cancel pending invite
- [x] Email service integration with `send_invite_email()`
- [x] Rate limiting on invite endpoint (`10/hour`)

### Wave 3: Frontend Invite Acceptance
- [x] `/invite/accept?token=…` page with validation code entry + account setup form
- [x] Auto-validate token on page load, show inviter name + role
- [x] Password validation (≥8 chars, match confirmation)
- [x] Auto-login after acceptance via access_token cookie

## Verification Results

### Backend
- Invite token uses `secrets.token_urlsafe(32)` — cryptographically secure.
- Validation code uses `secrets.randbelow` for 6-digit generation.
- All invite endpoints protected by `require_supervisor_or_admin`.
- Expired invites automatically rejected with 400 status.

### Frontend
- Invite acceptance page handles invalid/expired tokens gracefully.
- Form validates passwords and submits to `/api/invites/accept`.
- Successful acceptance redirects to dashboard with authenticated session.

## Next Steps

- Milestone 1 exit criteria review.
