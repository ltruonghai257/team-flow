# Phase 24: Knowledge Sharing Scheduler - Research

**Researched:** 2026-04-28
**Domain:** FastAPI + SQLAlchemy async, PostgreSQL enum migration, EventNotification reminders, SvelteKit 5 schedule tab integration
**Confidence:** HIGH for backend and notification integration, HIGH for current schedule UI shape, MEDIUM for final visual layout pending UI-SPEC

---

<user_constraints>
## User Constraints from CONTEXT.md

### Locked Decisions

- **D-01:** Knowledge Sessions live inside the existing `/schedule` page as a dedicated tab, not a new top-level route.
- **D-02:** The Knowledge Sessions tab opens in agenda/list view by default.
- **D-03:** The tab also includes a calendar view toggle.
- **D-04:** Presenter defaults to the session creator.
- **D-05:** Presenter can be changed only to a user valid for the session scope.
- **D-06:** Admin-created org-wide sessions can use any org user as presenter. Supervisor-created sessions must use a presenter inside the supervisor's sub-team.
- **D-07:** Knowledge Sessions use selectable reminder offsets, reusing the existing schedule reminder pattern.
- **D-08:** Creation notifications fan out to users in scope, and reminders reuse `EventNotification` plus APScheduler.
- **D-09:** References are a freeform textarea for notes and pasted links.
- **D-10:** Tags use a chip-style input.
- **D-11:** Use a separate `KnowledgeSession` table and router, not the personal `Schedule` model.
- **D-12:** Visibility is scope-filtered: org-wide sessions for admin-created events and sub-team-only sessions for supervisor-created events.
- **D-13:** Reuse the existing notification infrastructure. Do not introduce a second reminder system.

### Claude's Discretion

- Exact agenda/calendar toggle presentation inside the Knowledge Sessions tab.
- Exact references textarea wording and validation.
- Exact chip-entry behavior for tags, provided it stays lightweight and matches current SvelteKit form patterns.

### Deferred Ideas

- Attendance tracking, recurring series, and approval workflows are out of scope.
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| KS-01 | Admin can create org-wide KS sessions with topic, description, references, presenter, session type, duration, date/time, tags | New `KnowledgeSession` model with `scope="org"`, `created_by_id`, `presenter_id`, `session_type`, `start_time`, `duration_minutes`, `references`, `tags` |
| KS-02 | Supervisor can create sub-team scoped KS sessions with the same fields | Router write path uses `require_supervisor_or_admin`; supervisor scope is derived from `get_sub_team` and persisted as `sub_team_id` |
| KS-03 | KS appears as dedicated tab inside `/schedule`, no new top-level route | Modify `frontend/src/routes/schedule/+page.svelte`; add API module and optional components, but no route file |
| KS-04 | Members see only sessions in scope | GET query returns org-wide rows plus rows where `sub_team_id == current_user.sub_team_id`; admin with no sub-team filter can see all |
| KS-05 | Members receive in-app reminder before scoped sessions | Create `EventNotification` pending rows for selected offsets and scoped recipients |
| KS-06 | Members receive in-app notification on new scoped session | Create immediate `EventNotification` rows with `status=sent` for scoped recipients on session create |
</phase_requirements>

---

## Summary

Phase 24 should add a dedicated `KnowledgeSession` domain instead of mutating personal schedules. The existing `Schedule` model is explicitly per-user (`user_id` required), and `routers/schedules.py` filters every read by `Schedule.user_id == current_user.id`. Reusing it would either hide supervisor-created sessions from members or leak personal calendar events if that filter were weakened.

The backend critical path is:

1. Add enums and model: `KnowledgeSessionType`, optional scope enum or string field, and `KnowledgeSession`.
2. Add a PostgreSQL-safe Alembic migration: extend `NotificationEventType` with `knowledge_session`, create `knowledge_sessions`, and keep the migration linear after the current v2.2 head.
3. Add schemas and router: list visible sessions, create/update/delete as supervisor/admin, validate presenter scope, and fan out notification rows.
4. Extend notification resolution: `_resolve_event` in `routers/notifications.py` must handle `knowledge_session`, or reminder UI and by-event lookups will fail.
5. Extend `/schedule`: add a Knowledge Sessions tab with separate state, agenda default, calendar toggle, scoped list, form modal, reminder chips, references textarea, and tag chips.

The frontend critical path is the tab-state split. Current `/schedule` has one modal (`showModal`), one edit target (`editingSchedule`), one `form`, and one `formReminders` array. KS work must not reuse those variables for session editing, because tab switches and source-specific edits would leak personal schedule state into KS forms.

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|--------------|----------------|-----------|
| Session visibility scope | Backend | Frontend labels | Scope is security-sensitive; never rely on hidden buttons |
| Presenter eligibility | Backend | Frontend select options | Backend rejects invalid presenter IDs; frontend narrows choices for ergonomics |
| Creation notification fanout | Backend | Scheduler delivery | Rows are created at POST time for all scoped recipients |
| Reminder delivery | Backend | Existing scheduler | `EventNotification` rows move pending to sent through `process_due_notifications` |
| Agenda/calendar browsing | Frontend | Backend date filtering | UI owns toggle state; API can accept optional start/end filters |
| Tag chip input | Frontend | Backend normalization | Frontend controls chip behavior; backend stores normalized tags |
| References notes/links | Frontend | Backend storage | Freeform text stored as-is; render as plain text or safe linkified text only if sanitized |

---

## Recommended Project Structure

```text
backend/app/
├── models/
│   ├── enums.py              # add KnowledgeSessionType and NotificationEventType.knowledge_session
│   ├── knowledge.py          # KnowledgeSession
│   └── __init__.py           # re-export KnowledgeSession and enum
├── schemas/
│   ├── knowledge.py          # KnowledgeSessionCreate/Update/Out
│   └── __init__.py           # export schemas
├── routers/
│   ├── knowledge_sessions.py # /api/knowledge-sessions
│   └── notifications.py      # _resolve_event branch for knowledge_session
└── api/main.py               # include_router(knowledge_sessions.router)

frontend/src/
├── lib/apis/
│   ├── knowledge-sessions.ts # API module
│   └── index.ts              # export knowledgeSessions
├── lib/components/knowledge/
│   ├── SessionForm.svelte
│   └── SessionCard.svelte
└── routes/schedule/+page.svelte
```

---

## Implementation Patterns

### Pattern 1: Separate Model from Personal Schedule

Use a new table with its own scope semantics. Do not add a discriminator to `schedules`.

Recommended columns:

| Column | Notes |
|--------|-------|
| `id` | Integer PK |
| `topic` | Required title shown in agenda/calendar |
| `description` | Optional text |
| `references` | Freeform text, nullable |
| `presenter_id` | FK to users, required or defaulted to creator |
| `session_type` | Enum: `presentation`, `demo`, `workshop`, `qa` |
| `start_time` | DateTime, required |
| `duration_minutes` | Positive int |
| `tags` | String or JSON array; JSON is cleaner for chip input |
| `scope` | `org` or `sub_team`, or inferred from nullable `sub_team_id` |
| `sub_team_id` | Null for org-wide, set for supervisor-scoped sessions |
| `created_by_id` | FK to users |
| `created_at`, `updated_at` | Standard timestamps |

### Pattern 2: Scope Filtering

Use `get_sub_team` for current context, but handle admin-with-no-filter explicitly.

```python
stmt = select(KnowledgeSession).order_by(KnowledgeSession.start_time)

if current_user.role == UserRole.admin and sub_team is None:
    # Admin global view: no scope filter.
    pass
elif sub_team is not None:
    stmt = stmt.where(
        or_(
            KnowledgeSession.sub_team_id.is_(None),
            KnowledgeSession.sub_team_id == sub_team.id,
        )
    )
else:
    stmt = stmt.where(KnowledgeSession.sub_team_id.is_(None))
```

For members, `get_sub_team` resolves their team. For supervisors, it resolves their assigned team. For admins, the `X-SubTeam-ID` header narrows the view, and no header means org-wide/global visibility.

### Pattern 3: Presenter Validation

Presenter selection is a write-time security rule.

- Admin org-wide session: presenter can be any active user.
- Admin sub-team-filtered session: presenter should be in the selected sub-team unless creating an org-wide session.
- Supervisor session: presenter must be active and in the supervisor's sub-team.
- Default presenter is `current_user.id` when `presenter_id` is missing.

The frontend can load users from `GET /api/users/`, which already applies sub-team filtering through `get_sub_team`, but backend validation is still mandatory.

### Pattern 4: Notification Rows for Creation and Reminders

The current notification system does not need a new scheduler. It needs a new event type and rows.

- Creation notifications: create rows with `status=sent`, `remind_at=now`, `offset_minutes=0`, one per scoped recipient.
- Reminder notifications: create rows with `status=pending` unless `start_time - offset <= now`, in which case `status=sent`.
- Preserve existing sent/dismissed rows on update when session time changes, following the sprint/milestone reminder tests.

The `NotificationEventType` enum needs `knowledge_session`, and `_resolve_event` must return `(topic, start_time)` for visible sessions. `frontend/src/lib/apis/notifications.ts` must widen its event type union from `'schedule' | 'task'` to include `'knowledge_session'`.

### Pattern 5: `/schedule` Tab Isolation

Current state variables for personal schedule events:

- `scheduleList`
- `showModal`
- `editingSchedule`
- `form`
- `formReminders`

Add separate KS state:

- `activeTab: 'calendar' | 'knowledge'`
- `knowledgeSessions`
- `knowledgeViewMode: 'agenda' | 'calendar'`
- `showKnowledgeModal`
- `editingKnowledgeSession`
- `knowledgeForm`
- `knowledgeReminderOffsets`
- `knowledgeTags`

On tab switch, close both modal families and clear edit targets. Calendar events can include KS items, but editing controls must remain source-specific.

---

## Build Order

1. **Backend data contract and migration**
   - Add `KnowledgeSessionType`, `NotificationEventType.knowledge_session`, `KnowledgeSession`, schemas, migration.
   - Verify import wiring and migration chain.

2. **Backend router and notification fanout**
   - Add `/api/knowledge-sessions`.
   - Implement scope-filtered list, create/update/delete, presenter validation, creation fanout, reminder fanout.
   - Extend `_resolve_event`.

3. **Frontend API and schedule tab**
   - Add `knowledge-sessions.ts` and export it.
   - Extend `/schedule` with dedicated tab state, agenda default, calendar toggle, form, cards, tags, references, reminder chips.

4. **Verification and hardening**
   - Add backend tests for scope visibility, presenter validation, create fanout, reminders, and notification resolution.
   - Run backend pytest subset and frontend build.
   - Manual browser check for `/schedule` tab state isolation.

---

## Common Pitfalls

### Pitfall 1: Reusing `Schedule`

`Schedule` is personal. Every `GET /api/schedules/` read filters by the current user's `user_id`. Do not use it for KS sessions.

### Pitfall 2: Missing Notification Resolver Branch

Adding the enum value is not enough. `_resolve_event` currently supports only `schedule` and `task` for manual reminders. Without a `knowledge_session` branch, notification creation and by-event checks fail.

### Pitfall 3: PostgreSQL Enum Migration Runs in a Transaction

PostgreSQL enum value additions are sensitive. The migration must use the existing project-safe pattern for enum changes and must be verified against PostgreSQL, not just SQLite.

### Pitfall 4: Creation Notifications Duplicate on Update

Creation fanout should happen on POST only. PATCH should adjust pending reminders if times/offsets change, but it should not re-announce the session to every scoped user unless explicitly requested.

### Pitfall 5: Frontend Modal State Leak

Do not reuse `showModal`, `editingSchedule`, `form`, or `formReminders` for KS sessions. Separate state prevents stale personal event data from appearing in KS forms after tab switches.

### Pitfall 6: Frontend-Only Scope Enforcement

Hiding create/edit buttons for members is useful UX, but not security. Router write endpoints must enforce supervisor/admin access and presenter scope.

### Pitfall 7: Tags Stored as a Raw Comma String Despite Chip UI

Chip UI is easier to keep honest if tags are stored as JSON list. If a string is chosen for consistency with `Task.tags`, normalize and split carefully in the API client so duplicate/blank chips do not persist.

---

## Don't Hand-Roll

| Problem | Avoid | Use Instead |
|---------|-------|-------------|
| Reminder scheduler | A second APScheduler job for KS reminders | Existing `EventNotification` rows plus `process_due_notifications` |
| Auth and role checks | Manual JWT parsing | `Depends(get_current_user)` and `require_supervisor_or_admin` |
| Sub-team context | Custom header parsing | Existing `get_sub_team` dependency |
| Toasts | Custom notification widget | Existing `svelte-sonner` toast pattern |
| Icons | Inline SVG | `lucide-svelte` |
| Date rendering | Custom formatter | Existing date-fns and `formatDateTime` helpers |

---

## Open Questions

1. **Can supervisors edit/delete their own sessions only, or any session in their sub-team?**
   - Recommendation: supervisor can edit/delete sessions they created inside their sub-team; admin can edit/delete all. This prevents one supervisor from rewriting another supervisor's plan if role scopes expand later.

2. **Should creation notifications include the presenter only or all scoped members?**
   - Requirement KS-06 says members receive a notification when a new session in their scope is created. So fan out to all scoped members, including presenter and creator, unless the UI later decides creator self-notifications are noise.

3. **Tags storage type**
   - Recommendation: JSON list for `tags`, because CONTEXT.md locked chip-style entry. If using `String` for consistency with `Task.tags`, the plan must include normalization and duplicate removal.

---

## Validation Architecture

> `workflow.nyquist_validation` is enabled by init config. This section exists so `24-VALIDATION.md` can be derived without a second research pass.

### Test Framework

| Property | Value |
|----------|-------|
| Backend framework | pytest with httpx AsyncClient |
| Backend quick command | `rtk uv run pytest backend/tests/test_knowledge_sessions.py -q` |
| Backend broader command | `rtk uv run pytest backend/tests/test_notifications.py backend/tests/test_knowledge_sessions.py -q` |
| Frontend command | `cd frontend && bun run build` |
| Manual check | Browser walkthrough of `/schedule` Knowledge Sessions tab |

### Phase Requirements to Test Map

| Req ID | Behavior | Test Type | Target |
|--------|----------|-----------|--------|
| KS-01 | Admin creates org-wide session with all fields and creation notifications fan out | integration | `backend/tests/test_knowledge_sessions.py` |
| KS-02 | Supervisor creates sub-team session; invalid out-of-team presenter is rejected | integration | `backend/tests/test_knowledge_sessions.py` |
| KS-03 | `/schedule` contains Knowledge Sessions tab and no new top-level route | frontend build + manual | `frontend/src/routes/schedule/+page.svelte` |
| KS-04 | Member sees org-wide plus own sub-team sessions, not other sub-team sessions | integration | `backend/tests/test_knowledge_sessions.py` |
| KS-05 | Reminder rows are created with selected offsets and become sent through existing scheduler | integration | `backend/tests/test_knowledge_sessions.py`, `backend/tests/test_notifications.py` |
| KS-06 | Immediate creation notifications are `sent` for scoped recipients | integration | `backend/tests/test_knowledge_sessions.py` |

### Wave 0 Gaps

- Add `backend/tests/test_knowledge_sessions.py` with fixtures for admin, supervisor, two sub-teams, members, presenter candidates, and session factories.
- Add or extend notification tests for `NotificationEventType.knowledge_session` resolution.
- Ensure frontend build is part of verification because `/schedule` is a large Svelte page with shared state risk.

### Manual-Only Verifications

- Login as member and confirm create/edit controls are absent in the Knowledge Sessions tab.
- Login as supervisor and confirm presenter options are limited to the supervisor's sub-team.
- Switch between personal calendar and Knowledge Sessions tabs while modals are open and confirm form state does not leak.
- Create a session with references and chips, refresh, and confirm values render correctly.

---

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|------------------|
| V2 Authentication | Yes | All endpoints use `Depends(get_current_user)` |
| V4 Access Control | Yes | Scope-filtered reads, supervisor/admin writes, presenter validation |
| V5 Input Validation | Yes | Pydantic schemas validate duration, session type, times, tags, references |
| V7 Error Handling | Yes | Return 403 for forbidden scope/write attempts without exposing hidden sessions |

### STRIDE Threat Register

| Threat ID | Category | Component | Mitigation |
|-----------|----------|-----------|------------|
| T-24-01 | Information Disclosure | Session list endpoint | Filter reads to org-wide plus current sub-team scope |
| T-24-02 | Elevation of Privilege | Create/update/delete endpoints | Require supervisor/admin and validate creator scope |
| T-24-03 | Tampering | Presenter assignment | Reject presenter IDs outside the allowed scope |
| T-24-04 | Denial of Service | Notification fanout | Keep fanout bounded to scoped active users and avoid duplicate pending rows |
| T-24-05 | Spoofing/Tampering | Client-provided scope fields | Server derives supervisor scope and ignores or validates client-submitted scope |
| T-24-06 | Stored XSS | References field | Render references as text unless explicit sanitization/linkification is added |

---

## Sources

### Primary

- `.planning/phases/24-knowledge-sharing-scheduler/24-CONTEXT.md`
- `.planning/REQUIREMENTS.md`
- `.planning/ROADMAP.md`
- `.planning/STATE.md`
- `.planning/research/ARCHITECTURE.md`
- `.planning/research/PITFALLS.md`
- `backend/app/routers/schedules.py`
- `backend/app/models/work.py`
- `backend/app/models/enums.py`
- `backend/app/models/notifications.py`
- `backend/app/routers/notifications.py`
- `backend/app/internal/scheduler_jobs.py`
- `backend/app/utils/auth.py`
- `backend/app/routers/users.py`
- `backend/app/api/main.py`
- `frontend/src/routes/schedule/+page.svelte`
- `frontend/src/lib/apis/schedules.ts`
- `frontend/src/lib/apis/notifications.ts`

### Secondary

- `.planning/phases/23-standup-updates/23-CONTEXT.md`
- `.planning/phases/23-standup-updates/23-RESEARCH.md`
- `backend/tests/test_notifications.py`

---

## Metadata

**Confidence breakdown:**

- Backend model/router path: HIGH, based on direct code inspection.
- Notification integration: HIGH, based on direct inspection of notification router, model, scheduler, and tests.
- Frontend tab risk: HIGH, based on current `/schedule` local state shape.
- Final visual layout: MEDIUM until `24-UI-SPEC.md` is generated.

**Research date:** 2026-04-28
**Valid until:** 2026-05-28

## RESEARCH COMPLETE
