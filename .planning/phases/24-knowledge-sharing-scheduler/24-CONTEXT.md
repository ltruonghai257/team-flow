# Phase 24: Knowledge Sharing Scheduler - Context

**Gathered:** 2026-04-28
**Status:** Ready for planning

<domain>
## Phase Boundary

Admins and supervisors can schedule Knowledge Sharing sessions with scoped visibility, and team members can browse those sessions inside a dedicated tab within the existing `/schedule` page while receiving in-app notifications and reminders for sessions in their scope.

</domain>

<decisions>
## Implementation Decisions

### Calendar Surface and Browsing (KS-03, KS-04)
- **D-01:** Knowledge Sessions live inside the existing `/schedule` page as a dedicated tab, not a new top-level route.
- **D-02:** The Knowledge Sessions tab opens in an **agenda/list view by default** for practical browsing of upcoming sessions.
- **D-03:** The same tab also includes a **calendar view toggle** so users can switch between agenda and date-based browsing without leaving the tab.

### Presenter Assignment Rules (KS-01, KS-02)
- **D-04:** The presenter field **defaults to the session creator** to keep session creation fast.
- **D-05:** The presenter can be changed, but only to a user who is valid for the session scope.
- **D-06:** For admin-created org-wide sessions, the presenter can be any org user. For supervisor-created sessions, the presenter must stay within the supervisor's sub-team scope.

### Reminder Delivery (KS-05, KS-06)
- **D-07:** Knowledge Sessions use **selectable reminder offsets**, reusing the existing schedule reminder pattern rather than a single fixed lead time.
- **D-08:** Session creation should fan out in-app notifications to users in scope, and reminder delivery should reuse the existing `EventNotification` plus APScheduler flow already in the app.

### References and Tags Input Style (KS-01, KS-02)
- **D-09:** References are entered in a **freeform textarea** that can contain plain notes and pasted links.
- **D-10:** Tags use a **chip-style input** rather than comma-separated plain text so browsing and filtering stays cleaner in the UI.

### Locked Carry-Forward Decisions
- **D-11:** Knowledge Sessions use a separate `KnowledgeSession` table and router, not the existing `Schedule` model, because `Schedule` is personal and `KnowledgeSession` is team-scoped.
- **D-12:** Visibility is scope-filtered: org-wide sessions for admin-created events, sub-team-only sessions for supervisor-created events.
- **D-13:** The existing notification infrastructure remains the delivery mechanism; do not introduce a second reminder system.

### Claude's Discretion
- Exact presentation of the agenda/calendar toggle inside the Knowledge Sessions tab
- Exact wording and validation rules for the references textarea
- Exact chip-entry behavior for tags, provided the final input stays lightweight and consistent with current SvelteKit form patterns

</decisions>

<specifics>
## Specific Ideas

- The new tab should feel like part of the current scheduler, not a separate mini-app bolted onto it.
- Agenda-first browsing matters more than a dense calendar-only presentation for this feature.
- Presenter assignment should be quick for common cases, but still enforce team/org scope correctly.
- Tags should stay cleaner than a raw comma-separated field, while references can remain flexible and low-friction.

</specifics>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Roadmap and Requirements
- `.planning/ROADMAP.md` - Phase 24 goal, dependency on Phase 23, and the locked success criteria for scoped scheduling, `/schedule` tab placement, and reminder behavior
- `.planning/PROJECT.md` - Milestone v2.2 feature framing for Knowledge Sharing Scheduler and the original field list for sessions
- `.planning/REQUIREMENTS.md` - KS-01 through KS-06, which define scope, visibility, tab placement, and notification requirements
- `.planning/STATE.md` - Milestone v2.2 architecture decisions already locking `KnowledgeSession`, notification enum extension, `/schedule` tab placement, and reuse of existing scheduler infrastructure

### Prior Phase Context
- `.planning/phases/23-standup-updates/23-CONTEXT.md` - Established v2.2 frontend/backend pattern for adding a new domain, route, JSON-backed data, and canonical reference expectations

### Milestone Research
- `.planning/research/ARCHITECTURE.md` - Existing research for `knowledge_sessions`, router shape, calendar integration options, and file-level implementation targets
- `.planning/research/FEATURES.md` - Feature-level product expectations and prior recommendation to keep Knowledge Sessions separate from personal schedules
- `.planning/research/PITFALLS.md` - Critical risks around team-scoped sessions, notification enum migration, and calendar tab state isolation
- `.planning/research/STACK.md` - Existing stack guidance for calendar integration, reminders, and lightweight frontend additions for v2.2

### Backend Integration Points
- `backend/app/routers/schedules.py` - Current personal schedule router; must remain personal-calendar scoped and should not be repurposed for Knowledge Sessions
- `backend/app/models/work.py` - Existing `Schedule` model proving why a team-scoped session model must stay separate
- `backend/app/models/notifications.py` - EventNotification model and reminder settings pattern to reuse for creation notifications and reminder fanout
- `backend/app/models/enums.py` - `NotificationEventType` definition; planning must account for adding `knowledge_session`
- `backend/app/internal/scheduler_jobs.py` - Current APScheduler jobs pattern that should continue driving reminder delivery
- `backend/app/routers/notifications.py` - Existing notification endpoints and event resolution logic that Knowledge Sessions must integrate with
- `backend/app/utils/auth.py` - `get_sub_team` and role helpers that define org-wide vs sub-team visibility behavior
- `backend/app/routers/users.py` - Current scoped user listing pattern relevant to presenter selection

### Frontend Integration Points
- `frontend/src/routes/schedule/+page.svelte` - Current scheduler page, modal patterns, event aggregation, and the exact location where the new Knowledge Sessions tab must integrate
- `frontend/src/lib/apis/schedules.ts` - Existing personal schedule API module; useful as a shape reference, but not the same domain
- `frontend/src/lib/apis/notifications.ts` - Existing notification/reminder API surface that the Knowledge Sessions UI should align with
- `frontend/src/lib/stores/subTeam.ts` - Admin sub-team selection behavior that affects scoped session browsing and supervisor/admin creation flows

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `frontend/src/routes/schedule/+page.svelte`: already has month-grid rendering, upcoming list behavior, modal patterns, and reminder chip UI that can inform the new Knowledge Sessions tab
- `backend/app/models/notifications.py` + `backend/app/routers/notifications.py`: already support event-based reminder rows and bell delivery without new infrastructure
- `backend/app/internal/scheduler_jobs.py`: already flips due notifications from `pending` to `sent` on an interval, so KS reminders can plug into the same pipeline
- `backend/app/utils/auth.py:get_sub_team`: already encapsulates admin/all-teams vs supervisor/sub-team context rules

### Established Patterns
- New feature domains get their own router and model instead of overloading a nearby domain
- Write access is role-gated in routers; read access is filtered by role and sub-team context
- Frontend API access goes through `frontend/src/lib/apis/*`
- Existing schedule reminders use selectable offset chips rather than a single hardcoded reminder

### Integration Points
- New backend pieces likely connect through `backend/app/api/main.py`, `backend/app/models/__init__.py`, and a dedicated `backend/app/routers/knowledge_sessions.py`
- The `/schedule` page will need a third event source beside personal schedules and task due dates
- Notification event resolution must learn how to resolve knowledge session titles/times for the bell and reminder flows
- Presenter selection should reuse existing user-loading patterns while respecting admin/sub-team scope rules

### Architectural Constraints
- Do not weaken the existing personal schedule visibility rules in `routers/schedules.py`
- Do not create a second notification scheduler or a parallel reminder mechanism
- Keep the new UI inside `/schedule`; this phase does not get a new top-level route

</code_context>

<deferred>
## Deferred Ideas

- The pending todo `2026-04-26-status-transition-graph-workflow.md` remains unrelated to Knowledge Sharing Scheduler and was not folded into this phase.
- Attendance tracking, recurring knowledge-session series, and approval workflows remain outside this phase's scope.

</deferred>

---

*Phase: 24-knowledge-sharing-scheduler*
*Context gathered: 2026-04-28*
