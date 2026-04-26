# Phase 17: Sprint & Release Reminders - Research

## RESEARCH COMPLETE

## Scope Summary

Phase 17 should extend the existing in-app notification system instead of creating a new delivery channel. The existing `EventNotification` table, `process_due_notifications()` scheduler job, 60-second frontend polling, and `NotificationBell.svelte` already provide the delivery path. The missing pieces are durable sub-team reminder settings, supervisor proposal/approval state, reminder recipient generation, duplicate prevention, date-change rebuild hooks, and click routing for sprint/milestone reminders.

## Current System Findings

- `backend/app/models.py` has `NotificationEventType` with only `schedule` and `task`; Phase 17 needs sprint and milestone event types.
- `EventNotification` stores `event_type`, `event_ref_id`, `user_id`, title/date caches, `remind_at`, `offset_minutes`, and status.
- Current notification APIs allow multiple offsets for a single schedule/task event by replacing rows per `(user_id, event_type, event_ref_id)` and then creating one row per offset. A global unique constraint on `(event_type, event_ref_id, user_id)` would break this existing behavior.
- `backend/app/scheduler_jobs.py` only flips pending rows to sent. It does not reconcile missing reminder rows.
- `Sprint` has nullable `end_date` and belongs to `Milestone`; `Milestone` has required `due_date` and belongs to `Project`; `Project` has nullable `sub_team_id`.
- Project participation is not modeled directly. The accepted fallback is task assignment: project/sprint/milestone participants are users assigned to tasks in that scope.
- `SubTeam` has `supervisor_id`; there is no deeper supervisor-chain model in current code, so Phase 17 should fall back to the immediate sub-team supervisor.
- `/team` already has a sub-team management tab and is the right surface for reminder settings and approval review.
- `frontend/src/lib/api.ts` centralizes API calls and already forwards `X-SubTeam-ID` for admin active sub-team scope.
- `NotificationBell.svelte` currently routes `schedule` to `/schedule` and all other notifications to `/tasks`; sprint/milestone routing must be made explicit.

## Recommended Architecture

### Backend Persistence

Add two focused models:

- `SubTeamReminderSettings`: one row per sub-team, default lead time 2 days, sprint reminder toggle, milestone reminder toggle, timestamps.
- `ReminderSettingsProposal`: supervisor-submitted pending setting changes, approved/rejected by admin, linked to sub-team and proposer/reviewer.

Extend `NotificationEventType` with:

- `sprint_end`
- `milestone_due`
- `reminder_settings_proposal`

Use an Alembic migration for all schema changes.

### Duplicate Prevention

Do not add a global unique constraint on `(event_type, event_ref_id, user_id)`, because existing schedule/task reminders support multiple offsets. Instead, add a partial unique index for generated sprint/milestone reminders only:

`event_type IN ('sprint_end', 'milestone_due')` on `(event_type, event_ref_id, user_id)`

This satisfies Phase 17 duplicate prevention without regressing existing schedule/task reminder offsets.

### Reminder Generation

Create a backend service module, for example `backend/app/services/reminder_notifications.py`, to keep scheduler and routers thin. It should provide:

- settings get/create helper with defaults
- participant resolution from task assignments
- supervisor recipient resolution via participant sub-teams
- recipient dedupe with participant wording preferred when a user is both participant and supervisor
- pending-row rebuild for a single sprint or milestone
- scheduled reconciliation for all eligible future sprint/milestone dates

The service should preserve sent/dismissed rows when dates change and delete/rebuild only pending rows for the affected generated event.

If calculated `remind_at` is already in the past, create the pending row with `remind_at = now` so the existing scheduler sends it on the next pass.

### Date Change Hooks

Call rebuild helpers from:

- `backend/app/routers/sprints.py` after create/update when `end_date` exists or changes
- `backend/app/routers/milestones.py` after create/update when `due_date` exists or changes

Keep hooks best-effort within the same transaction/session. Do not create notifications for sprint/milestone rows without the needed project/sub-team path.

### Settings and Approval API

Expose reminder settings through sub-team settings endpoints because `/team` already uses `sub_teams` APIs and admin sub-team context headers:

- members can read current reminder settings
- admins can update settings directly for the active sub-team
- supervisors can create a proposal for their sub-team
- admins can list pending proposals and approve/reject them

On proposal creation, create an `EventNotification` for admin users with `event_type = reminder_settings_proposal` and `event_ref_id = proposal.id`. The bell click can route to `/team`.

### Frontend

Extend `frontend/src/lib/api.ts` with reminder settings/proposal functions under `sub_teams` or a new `reminders` API object. Add UI inside `frontend/src/routes/team/+page.svelte` near the Sub-Teams tab:

- current lead time and toggles
- admin direct edit for active sub-team
- supervisor proposal form
- member read-only display
- admin proposal review list

Keep the UI operational and restrained; no dedicated approvals page.

Extend notification types and routing:

- `sprint_end` navigates to `/tasks?sprint_id={event_ref_id}` if the tasks route supports it, otherwise `/tasks`
- `milestone_due` navigates to `/milestones?milestone_id={event_ref_id}` if the milestones route supports focus, otherwise `/milestones`
- `reminder_settings_proposal` navigates to `/team`

If query params are not yet consumed by those pages, adding them is optional as long as the fallback routes work.

## Validation Architecture

Use existing backend pytest style plus Python compile checks.

Recommended automated checks:

- `python -m compileall backend/app`
- `cd backend && pytest tests/test_notifications.py tests/test_sub_teams.py tests/test_sprints.py`

Recommended test files:

- `backend/tests/test_notifications.py` for reminder generation, recipient dedupe, partial uniqueness, and past reminders
- `backend/tests/test_sub_teams.py` for settings/proposal permissions
- `backend/tests/test_sprints.py` or `backend/tests/test_milestones.py` for date-change rebuild hooks

Frontend verification:

- `cd frontend && bun run check`
- Manual smoke: update reminder settings on `/team`, submit supervisor proposal, approve as admin, verify bell routing.

## Planning Risks

- The roadmap parser currently fails `roadmap.get-phase 17` even though ROADMAP.md contains Phase 17. Plan from the ROADMAP.md phase section and the phase context.
- A global notification unique constraint would regress schedule/task multi-offset reminders. Use a partial generated-reminder unique index.
- Existing tests appear inconsistent around status codes and fixture definitions; executors should record test infrastructure blockers exactly if pytest cannot run.
- Sprints can have nullable `end_date`. Reminder generation must skip sprints without an end date.
