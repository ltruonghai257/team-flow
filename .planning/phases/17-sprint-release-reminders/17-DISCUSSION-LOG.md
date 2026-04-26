# Phase 17: Sprint & Release Reminders - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md - this log preserves the alternatives considered.

**Date:** 2026-04-26
**Phase:** 17-sprint-release-reminders
**Areas discussed:** Reminder settings surface, Sprint recipient rules, Timing and regeneration, Notification destination and wording

---

## Reminder Settings Surface

| Question | Options | User's choice / result |
|----------|---------|------------------------|
| Where should the lead-time setting live? | Sub-team settings only; Separate sprint and milestone settings per sub-team; Per project or per sprint override; Agent decide | Agent decide: one sub-team-level lead time, default 2 days, used for both sprint and milestone reminders. |
| Where should that setting be managed in the UI? | Team page; Schedule page; Projects or milestones; Agent decide | Agent decide: `/team`, inside sub-team management/settings. |
| How should admins behave with the global sub-team switcher? | Active sub-team only; All sub-teams table; Global default plus overrides; Agent decide | Agent decide: admin edits the active switched sub-team; supervisor edits own sub-team. |
| Should members see or change this setting? | No visibility; Read-only visibility; Personal opt-out; Agent decide | Members see lead time read-only and cannot change it. |
| Who can grant/change reminder behavior? | Supervisor/admin only; Supervisor/admin manage, members acknowledge; Members opt out; Agent decide | Supervisor/admin manage; members only dismiss notifications. |
| Should reminders have enable/disable toggles? | Always enabled; Team-level toggle; Separate toggles; Agent decide | Separate toggles for sprint reminders and milestone reminders. |
| Who can change toggles? | Supervisor/admin only; Admin only; Supervisor proposes, admin approves; Agent decide | Include supervisor proposal and admin approval workflow. |
| Where do admins review proposals? | Team page; Notification bell; Dedicated approvals page; Agent decide | Agent decide: bell notification alerts the admin; `/team` is the review/apply surface. |

**Notes:** The user asked about grant permissions and third-party integrations such as Microsoft Teams webhooks. Third-party delivery was identified as a separate delivery-channel capability and deferred.

---

## Sprint Recipient Rules

| Question | Options | User's choice / result |
|----------|---------|------------------------|
| Who should receive sprint-end reminders? | Assigned participants; Whole sub-team; Project members only; Agent decide | Project participants plus supervisors who lead those participants. If explicit project membership does not exist, infer participants from assigned tasks. |
| Should milestone due-date reminders use the same recipient rule? | Same rule; Whole project sub-team; Supervisors only; Agent decide | Agent decide with clarification: use same awareness model; supervisors should know the release date even when they do not join the project. |
| How should duplicates be handled? | One notification per user per event; Separate role-based notifications; Agent decide | Agent decide: one notification per user per event. |
| Direct supervisor only or supervisor chain? | Direct sub-team supervisor only; Supervisor chain; Agent decide | Use supervisor chain where supported; otherwise immediate `sub_team.supervisor_id`. |

**Notes:** The user gave an example where A and B are in sub-teams C and D, supervisors E and F lead those members, and A/B are in project G. Both E and F should receive awareness reminders.

---

## Timing and Regeneration

| Question | Options | User's choice / result |
|----------|---------|------------------------|
| Same lead time for sprint and milestone reminders? | Same lead time; Separate lead times; Agent decide | Agent decide: one shared lead time. |
| What happens when sprint/milestone dates change? | Rebuild pending reminders automatically; Only future generation uses new date; Ask supervisor/admin; Agent decide | Agent decide: rebuild pending reminders automatically; keep sent/dismissed historical rows. |
| What happens when participants/supervisors change? | Rebuild automatically; Scheduled reconciliation only; Manual refresh; Agent decide | Agent decide: scheduled reconciliation only. |
| What if reminder time is already in the past? | Send immediately; Skip it; Send at next scheduler pass; Agent decide | Agent decide: create pending row with `remind_at = now`; scheduler sends it on the next pass. |

**Notes:** Date edits are immediate rebuild triggers; assignment/team drift is handled by periodic reconciliation to keep implementation less invasive.

---

## Notification Destination and Wording

| Question | Options | User's choice / result |
|----------|---------|------------------------|
| Where should sprint reminder clicks go? | Tasks sprint board; Project page; No deep link; Agent decide | `/tasks` with the relevant sprint selected when possible; otherwise `/tasks`. |
| Where should milestone reminder clicks go? | Milestones page; Project page; Timeline page; Agent decide | Agent recommended `/milestones`; user accepted recommendation request. |
| How should wording differ by role? | Same wording; Participant vs supervisor wording; Detailed role-specific wording; Agent decide | Agent recommended participant vs supervisor wording; user chose agent decide. |
| Show lead time, exact due date, or both? | Both; Relative only; Exact date only; Agent decide | Both. |

**Notes:** The user asked for recommendations and rationale for milestone destination. Recommendation was `/milestones` because it is the current management surface and more actionable than `/timeline` or `/projects`.

---

## Agent's Discretion

- One shared sub-team lead time for sprint and milestone reminders.
- `/team` as the reminder settings surface.
- Active sub-team-only admin editing through the global switcher.
- No dedicated approvals page; bell notification plus `/team` review.
- One notification per user per event.
- Rebuild pending rows on date change, scheduled reconciliation for membership drift.
- Past-due calculated reminder times become pending rows with `remind_at = now`.
- Milestone reminder destination is `/milestones`.
- Participant vs supervisor notification wording.

## Deferred Ideas

- Third-party notification delivery via Microsoft Teams/webhooks with permission/grant controls.
- Personal member opt-out for sprint/milestone reminders.
- Dedicated approvals page.
- Separate lead times for sprint reminders and milestone reminders.
