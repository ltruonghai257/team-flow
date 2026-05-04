# Phase 17: Sprint & Release Reminders - Context

**Gathered:** 2026-04-26
**Status:** Ready for planning

<domain>
## Phase Boundary

TeamFlow creates automatic in-app reminders for sprint end dates and milestone due dates. Reminders are generated from sprint/milestone dates, delivered through the existing `EventNotification` table and 60-second frontend polling/bell flow, and scoped by sub-team reminder settings. This phase covers in-app reminder settings, recipient generation, duplicate prevention, approval flow for supervisor-proposed setting changes, and notification click destinations.

</domain>

<decisions>
## Implementation Decisions

### Reminder Settings Ownership
- **D-01:** Use one sub-team-level lead time setting for both sprint-end and milestone due-date reminders.
- **D-02:** Default lead time is 2 days.
- **D-03:** Add separate sub-team toggles for sprint reminders and milestone reminders.
- **D-04:** Reminder settings live on `/team` inside the sub-team management/settings area.
- **D-05:** Admins edit reminder settings for the currently active sub-team from the global switcher.
- **D-06:** Supervisors work within their own sub-team context.
- **D-07:** Members can see the team's reminder lead time read-only, but cannot change it.

### Permission and Approval Flow
- **D-08:** Admins can apply reminder setting changes directly for the active sub-team.
- **D-09:** Supervisors can propose changes to lead time and sprint/milestone reminder toggles.
- **D-10:** Supervisor-proposed changes do not take effect until an admin approves them.
- **D-11:** Admins should receive an in-app/bell notification for proposed reminder setting changes.
- **D-12:** Review and approval happen on `/team` near the sub-team reminder settings.
- **D-13:** No dedicated approvals page is required in Phase 17.
- **D-14:** Members cannot acknowledge reminders beyond the existing notification dismiss action.

### Recipient Rules
- **D-15:** Sprint reminders go to project participants plus supervisors responsible for those participants.
- **D-16:** Unless explicit project membership exists by implementation time, project participants are inferred from users assigned to tasks in the sprint/project.
- **D-17:** Milestone due-date reminders use the same awareness model: project participants plus supervisors responsible for those participants.
- **D-18:** Supervisors should receive awareness reminders even when they are not directly assigned to or participating in the project.
- **D-19:** Use the supervisor chain where the data model supports it; otherwise fall back to the immediate `sub_team.supervisor_id`.
- **D-20:** A user receives one notification per user per sprint/milestone event, even if they qualify as both participant and supervisor.

### Timing and Regeneration
- **D-21:** Sprint and milestone reminders share the same sub-team lead time value.
- **D-22:** When a sprint end date or milestone due date changes, automatically rebuild pending reminders for that event.
- **D-23:** Sent and dismissed notification rows remain historical when dates change.
- **D-24:** Participant/supervisor membership drift is handled by scheduled reconciliation rather than immediate rebuilds on every assignment or team change.
- **D-25:** The scheduler should create missing pending rows and rely on uniqueness to prevent duplicates.
- **D-26:** If the calculated reminder time is already in the past, create a pending row with `remind_at = now` so it is sent by the next scheduler pass.

### Notification Destination and Wording
- **D-27:** Sprint reminder clicks navigate to `/tasks` with the relevant sprint selected when routing/state supports it; fallback is `/tasks`.
- **D-28:** Milestone reminder clicks navigate to `/milestones`, ideally focused or highlighted on the relevant milestone; fallback is `/milestones`.
- **D-29:** Use participant-vs-supervisor wording rather than identical copy for everyone.
- **D-30:** Participants get action wording such as "Sprint X ends in 2 days. Review your remaining tasks."
- **D-31:** Supervisors and manager-chain recipients get awareness wording such as "Sprint X ends in 2 days for members you supervise."
- **D-32:** If a user qualifies as both participant and supervisor, send one notification and prefer participant wording with enough context to remain useful.
- **D-33:** Reminder notifications show both relative lead time and exact date.

### Agent's Discretion
- Exact database table and schema names for reminder settings and supervisor-proposed changes.
- Exact admin notification title/copy for approval requests, provided the notification links back to `/team`.
- Exact query strategy for deriving project participants, provided it respects the agreed fallback to task assignment when project membership does not exist.
- Exact implementation of `/tasks` sprint preselection and `/milestones` focus/highlight behavior.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Roadmap and Requirements
- `.planning/ROADMAP.md` - Phase 17 goal, dependencies, success criteria, and sequencing before Phase 18/v2.1.
- `.planning/REQUIREMENTS.md` - Historical REMIND-01/REMIND-02 status and milestone boundary notes.
- `.planning/STATE.md` - Current milestone notes indicating Phase 17 is planned before v2.1.

### Prior Phase Context
- `.planning/phases/13-multi-team-hierarchy-timeline-visibility/13-CONTEXT.md` - Sub-team scoping, admin global switcher, and supervisor context decisions.
- `.planning/phases/14-sprint-model/14-CONTEXT.md` - Sprint model, sprint date behavior, milestone relationship, and task/sprint integration.
- `.planning/phases/16-advanced-kpi-dashboard/16-CONTEXT.md` - Per-sub-team settings precedent and supervisor-focused dashboard context.

### Existing Notification System
- `backend/app/models.py` - `NotificationEventType`, `NotificationStatus`, `EventNotification`, `SubTeam`, and user/sub-team relationships.
- `backend/app/routers/notifications.py` - Current task/schedule notification APIs and ownership checks.
- `backend/app/scheduler_jobs.py` - Existing APScheduler job that flips due notifications from pending to sent.
- `backend/app/schemas.py` - Current notification schemas and expected response shape.
- `frontend/src/lib/stores/notifications.ts` - 60-second frontend polling and toast callback behavior.
- `frontend/src/lib/components/NotificationBell.svelte` - Notification list, dismiss behavior, and click destination pattern.

### Sprint and Milestone Surfaces
- `backend/app/routers/sprints.py` - Sprint CRUD and date fields.
- `backend/app/routers/milestones.py` - Milestone CRUD and due date fields.
- `frontend/src/lib/components/sprints/SprintForm.svelte` - Sprint date UI and warnings.
- `frontend/src/routes/milestones/+page.svelte` - Current milestone management surface.
- `frontend/src/routes/tasks/+page.svelte` - Target route for sprint reminder click-through.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `EventNotification`: Existing persistence model for pending/sent/dismissed in-app reminders; Phase 17 should extend it rather than create a separate notification system.
- `process_due_notifications()`: Existing scheduler job can be expanded or paired with a reconciliation job for sprint/milestone reminders.
- `notificationStore`: Existing frontend polling already detects newly sent notifications and triggers toasts.
- `NotificationBell.svelte`: Existing bell UI handles unread notifications, dismiss, and click navigation.
- `/team` page and sub-team context: Existing management surface and Phase 13 global switcher model are the right home for reminder settings.

### Established Patterns
- Notification delivery is in-app only and polling-based; no push, email, or third-party delivery in Phase 17.
- Backend uses FastAPI routers, SQLAlchemy async sessions, and `get_current_user`/sub-team dependencies.
- Admin global sub-team context is passed through `X-SubTeam-ID` in frontend API calls.
- Sprints belong to milestones, milestones belong to projects, and projects belong to sub-teams.
- The current notification event enum only supports `schedule` and `task`; Phase 17 needs sprint/milestone event types or an equivalent typed model.

### Integration Points
- `backend/app/models.py`: Add reminder settings, approval/proposal persistence, event types, and uniqueness constraints needed for one notification per user per event.
- `backend/app/scheduler_jobs.py`: Add generation/reconciliation for sprint and milestone reminder rows.
- `backend/app/routers/notifications.py`: Extend notification behavior for sprint/milestone events and proposal notifications as needed.
- `backend/app/routers/sprints.py` and `backend/app/routers/milestones.py`: Rebuild pending reminders when relevant dates change.
- `backend/app/routers/sub_teams.py` or an adjacent settings endpoint: Expose read-only settings to members and editable/proposable settings to supervisors/admins.
- `frontend/src/routes/team/+page.svelte`: Add reminder settings display, supervisor proposal UI, and admin approval UI.
- `frontend/src/lib/components/NotificationBell.svelte`: Route sprint/milestone clicks to `/tasks` and `/milestones` with contextual targeting where supported.

</code_context>

<specifics>
## Specific Ideas

- Supervisors must be aware of release/milestone dates even when they are not directly on the project.
- Example recipient model: if A and B are in different sub-teams, both assigned to project G, then the supervisors for both sub-teams should receive awareness reminders.
- Third-party delivery via Microsoft Teams/webhooks is useful later, but Phase 17 should not expand beyond in-app notifications.
- Proposal approval should feel lightweight: bell notification alerts the admin, `/team` is where the admin reviews and applies the setting change.

</specifics>

<deferred>
## Deferred Ideas

- Third-party notification delivery via Microsoft Teams/webhooks with permission/grant controls belongs in a future phase.
- Personal member opt-out for sprint/milestone reminders is out of scope for Phase 17.
- Dedicated approvals page is out of scope for Phase 17.
- Separate lead times for sprint and milestone reminders are out of scope for Phase 17.

</deferred>

---

*Phase: 17-Sprint & Release Reminders*
*Context gathered: 2026-04-26*
