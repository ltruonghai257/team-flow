# Phase 8: User Invite & Team Management - Context

**Gathered:** 2026-04-23
**Status:** Ready for planning

<domain>
## Phase Boundary

Deliver a full team management system: a 5-level role model (admin/manager/supervisor/SLM/member), multi-team support (Team + TeamMember tables), email-based invite flow with token + 6-digit validation code (72h expiry), direct-add for existing users, and team-scoped performance visibility. Teams hold users; tasks/projects remain globally visible. Invite and team management UI lives on the existing `/team` page.

</domain>

<decisions>
## Implementation Decisions

### Role Model
- **D-01:** 5-role hierarchy: `admin` > `manager` > `supervisor` = `SLM` (peer, tier 3) > `member`
  - `admin` — system-wide access, all teams, all performance data
  - `manager` — creates teams, invites users, sees all teams' performance
  - `supervisor` — tier-3 peer of SLM; manages their own team(s), invites users to their team, sees only their team(s)' performance
  - `SLM` (Subject Line Manager) — same permissions as supervisor; different job title, same role level
  - `member` — base role, no performance dashboard access
- **D-02:** Extend existing `UserRole` enum via Alembic migration (do NOT drop existing values). Add `manager` and `SLM` to the enum. Keep `admin`, `supervisor`, `member` as-is. Existing supervisor users automatically become tier-3 supervisors.
- **D-03:** Backend dependency additions:
  - `require_manager_or_above()` — allows `admin`, `manager`
  - `require_any_management()` — allows `admin`, `manager`, `supervisor`, `SLM` (all tiers 1–3)
  - Existing `require_supervisor()` in `auth.py` maps to `require_any_management()` for backward compat

### Team Model
- **D-04:** Add `Team` table: `id`, `name`, `description`, `created_by` (FK → users), `created_at`
- **D-05:** Add `TeamMember` table: `id`, `team_id` (FK → teams), `user_id` (FK → users), `role_in_team` (nullable string, e.g. "lead"), `joined_at`
- **D-06:** Teams do NOT scope tasks or projects — all tasks/projects remain globally visible. Teams are used only for invite grouping and performance scoping.
- **D-07:** Only `admin` and `manager` can CREATE a new team (`POST /api/teams`)
- **D-08:** `supervisor` and `SLM` can invite users to teams they lead (where they are a TeamMember with `role_in_team = "lead"`) but cannot create new teams

### Invite Flow
- **D-09:** Add `TeamInvite` table: `id`, `team_id` (FK → teams), `email`, `token` (UUID, unique), `validation_code` (6-digit string), `role` (UserRole enum — stores what role the invited user will receive), `invited_by` (FK → users), `status` (`pending` / `accepted` / `revoked`), `expires_at` (72h from creation), `created_at`
- **D-10:** `POST /api/teams/invite` — create invite, generate token + 6-digit code, send email (or log in dev), return `{invite_id, email, expires_at}`
- **D-11:** `GET /api/invites/validate?token=…` — return invite metadata (team name, inviter name, email, role, status). Used by the accept page to pre-fill context before submission.
- **D-12:** `POST /api/invites/accept` — body: `{token, validation_code, username, password, full_name}`. Validates token + code, creates user account with the role stored on the invite, creates TeamMember record, marks invite `accepted`.
- **D-13:** After account creation via invite: show a **success page** with a link to `/login`. No auto-login — user logs in manually.
- **D-14:** Role assignment at invite time — invite modal includes a role selector (`member` / `supervisor` / `SLM`). Manager role cannot be assigned via invite (must be set by admin post-creation via existing `PATCH /api/users/{id}/role`).

### Email Delivery
- **D-15:** Use `fastapi-mail` library — add to `requirements.txt`. Configure via env vars: `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASS`, `SMTP_FROM`.
- **D-16:** Dev mode (`ENVIRONMENT=development`): skip SMTP entirely, log token + code to backend console.
- **D-17:** Email content (production): team name, inviter's full name, the 6-digit validation code (prominent), and a direct accept link (`https://<app>/invite/accept?token=…`). Both in one email.

### Direct-Add (Existing Users)
- **D-18:** `POST /api/teams/add` — body: `{team_id, user_id}`. Supervisor/admin/manager can directly add an existing active user to a team. Creates a `TeamMember` record immediately. No email sent.
- **D-19:** "Add Member" button on `/team` opens a **modal with two tabs**: "Invite New" and "Add Existing". Clean single entry point.
- **D-20:** "Add Existing" tab: searchable dropdown of active users not already on the team. Selecting one submits `POST /api/teams/add`.

### Pending Invites Management
- **D-21:** Pending invites displayed as a **section on the existing `/team` page** (below the member cards grid, collapsible). Visible to `admin`, `manager`, `supervisor`, `SLM` roles only.
- **D-22:** Each invite row shows: email, role, inviter name, expiry time, status badge (`Pending` / `Expired` / `Revoked`). **Both active and expired invites shown** — expired ones have an "Expired" badge.
- **D-23:** Actions per invite: **Revoke** (marks status = `revoked`) and **Resend** (generates a new token + code, resets `expires_at` to 72h from now, sends fresh email). Resend works on both pending and expired invites.
- **D-24:** Backend endpoints: `DELETE /api/invites/{id}` (revoke), `POST /api/invites/{id}/resend` (resend)

### Performance Dashboard Scoping
- **D-25:** `/performance` dashboard — data filtered by role:
  - `admin` and `manager`: see **all teams' performance** (existing behavior, now team-aware)
  - `supervisor` and `SLM`: see **only performance of members in teams they lead** (`TeamMember.role_in_team = "lead"` for that user's `team_id`)
  - `member`: redirected away from `/performance` (existing behavior)
- **D-26:** `GET /api/dashboard/performance` — accepts optional `?team_id=N` filter. For supervisor/SLM, backend enforces team_id must be one of their led teams (403 if not). For admin/manager, any team_id is accepted (or all teams if omitted).

### Frontend Routes
- **D-27:** New route: `/invite/accept` — public page (no auth required). Renders a single form with fields: validation code, username, full name, password, confirm password. Submits to `POST /api/invites/accept`.
- **D-28:** `/team` page extended: "Add Member" button (top right, management roles only), pending invites section (management roles only), team selector if user leads multiple teams.

### Claude's Discretion
- Modal tab component implementation (reuse any existing modal pattern in the codebase)
- Exact email HTML template design
- TeamInvite token generation method (use `secrets.token_urlsafe(32)` for token, `str(random.randint(100000, 999999))` for 6-digit code)
- Pagination or limit on pending invites list
- Whether to add indexes on `TeamMember(team_id, user_id)` and `TeamInvite(token)` — both should be indexed

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Existing Auth & RBAC
- `backend/app/auth.py` — existing `require_supervisor()`, `get_current_user()` dependency patterns to extend
- `backend/app/models.py` — existing `UserRole` enum, `User` model; new roles added here
- `backend/app/routers/users.py` — existing `PATCH /{id}/role` endpoint pattern; `require_admin` usage

### Requirements
- `.planning/REQUIREMENTS.md` § REQ-07 — original RBAC acceptance criteria (now extended by this phase)

### Existing Frontend Patterns
- `frontend/src/routes/team/+page.svelte` — base team page to extend with invite UI and pending invites section
- `frontend/src/routes/+layout.svelte` — role-based nav guard pattern
- `frontend/src/lib/api.ts` — API client pattern for new invite/team endpoints
- `frontend/src/lib/stores/auth.ts` — auth store with user role; used for conditional UI rendering

### Existing Backend Patterns
- `backend/app/routers/` — router structure pattern (one file per domain); new `teams.py` and `invites.py` routers follow this
- `backend/app/config.py` — env var pattern for new SMTP_* settings

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `require_supervisor()` in `auth.py` — extend or alias to `require_any_management()` for new role tier
- `require_admin()` in `auth.py` — extend or alias to `require_manager_or_above()`
- `User.is_active` flag — used by direct-add to filter eligible users in the "Add Existing" dropdown
- `hash_password()` / `create_access_token()` in `auth.py` — reused by `POST /api/invites/accept` to create user and optionally issue token

### Established Patterns
- All routers use `AsyncSession = Depends(get_db)` with `select()` queries — follow same pattern in `teams.py` and `invites.py`
- `datetime.now(timezone.utc).replace(tzinfo=None)` — established timestamp pattern throughout models
- `pydantic[email]` already in `requirements.txt` — email validation available for invite schemas
- Frontend uses `toast` (svelte-sonner) for success/error feedback — use same pattern in invite UI

### Integration Points
- `backend/app/main.py` — new `teams` and `invites` routers must be registered here
- `backend/app/schemas.py` — new Pydantic schemas for `TeamCreate`, `TeamMemberAdd`, `InviteCreate`, `InviteAccept`, `InviteOut` go here
- Alembic `alembic/versions/` — new migration file needed for: `UserRole` enum extension + `teams` table + `team_members` table + `team_invites` table
- `/performance` route + `GET /api/dashboard/performance` — team-scoped filtering added for supervisor/SLM roles

</code_context>

<specifics>
## Specific Ideas

- Role hierarchy explicitly: `admin` > `manager` > (`supervisor` = `SLM`, peer tier) > `member`
- Teams are ORGANIZATIONAL GROUPING ONLY — tasks/projects stay globally visible, no team_id FK on project/task
- SLM and supervisor have IDENTICAL permissions — different job titles, not different access levels
- Performance scoping: supervisor/SLM see only members of teams where they hold `role_in_team = "lead"` in TeamMember
- The `manager` role is new (tier 2, above supervisor). Only admin and manager can CREATE teams. All management roles (incl. supervisor/SLM) can invite to teams they lead.
- Invite email: code + link in one email. Dev environment logs to console only.
- Accept flow: single-page form (code + username + full_name + password), then success page → manual login.
- Pending invites: show all statuses (pending + expired), with Revoke and Resend actions.

</specifics>

<deferred>
## Deferred Ideas

- Auto-login after invite acceptance (decided against for v1 — manual login after success page)
- Team-scoped task/project visibility (explicitly deferred — teams are grouping only in this phase)
- Admin role assignable via invite modal (deferred — admin must be set post-creation by admin)
- Multi-team dashboard aggregation view for managers (deferred to a future dashboard phase)

</deferred>

---

*Phase: 08-user-invite-team-management*
*Context gathered: 2026-04-23*
