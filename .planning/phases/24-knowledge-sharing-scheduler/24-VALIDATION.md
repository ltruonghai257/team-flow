---
phase: 24
slug: knowledge-sharing-scheduler
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-04-28
---

# Phase 24 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest + httpx AsyncClient for backend; Bun/SvelteKit build for frontend |
| **Config file** | `backend/tests/conftest.py`; frontend uses `frontend/package.json` scripts |
| **Quick run command** | `rtk uv run pytest backend/tests/test_knowledge_sessions.py -q` |
| **Full suite command** | `rtk uv run pytest backend/tests/test_notifications.py backend/tests/test_knowledge_sessions.py -q` and `cd frontend && bun run build` |
| **Estimated runtime** | ~2-4 minutes |

---

## Sampling Rate

- **After every backend task commit:** Run `rtk uv run pytest backend/tests/test_knowledge_sessions.py -q`
- **After notification changes:** Run `rtk uv run pytest backend/tests/test_notifications.py backend/tests/test_knowledge_sessions.py -q`
- **After frontend `/schedule` changes:** Run `cd frontend && bun run build`
- **After every plan wave:** Run the full suite command plus a manual `/schedule` smoke pass
- **Before `$gsd-verify-work`:** Backend tests green, frontend build green, manual checks completed
- **Max feedback latency:** 240 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 24-test-fixtures | 01 | 0 | KS-01, KS-02, KS-04 | T-24-01 / T-24-02 | Fixtures cover admin, supervisor, two sub-teams, members, presenter candidates | integration | `rtk uv run pytest backend/tests/test_knowledge_sessions.py -q` | ❌ W0 | ⬜ pending |
| 24-migration-model | 01 | 1 | KS-01, KS-02 | T-24-05 | `KnowledgeSession` stores scope separately from personal `Schedule` | import + migration parse | `cd backend && python -m alembic check` | ❌ W0 | ⬜ pending |
| 24-enum-migration | 01 | 1 | KS-05, KS-06 | T-24-04 | `NotificationEventType.knowledge_session` exists and migration is PostgreSQL-safe | migration + integration | `rtk uv run pytest backend/tests/test_notifications.py backend/tests/test_knowledge_sessions.py -q` | ❌ W0 | ⬜ pending |
| 24-router-create-admin | 02 | 1 | KS-01, KS-06 | T-24-02 / T-24-04 | Admin can create org-wide session and scoped creation notifications are sent | integration | `rtk uv run pytest backend/tests/test_knowledge_sessions.py -q` | ❌ W0 | ⬜ pending |
| 24-router-create-supervisor | 02 | 1 | KS-02 | T-24-02 / T-24-03 | Supervisor can create only sub-team scoped sessions with in-scope presenter | integration | `rtk uv run pytest backend/tests/test_knowledge_sessions.py -q` | ❌ W0 | ⬜ pending |
| 24-router-list-scope | 02 | 1 | KS-04 | T-24-01 | Member sees org-wide plus own sub-team sessions, not sibling sub-team sessions | integration | `rtk uv run pytest backend/tests/test_knowledge_sessions.py -q` | ❌ W0 | ⬜ pending |
| 24-router-reminders | 02 | 1 | KS-05 | T-24-04 | Selected reminder offsets create bounded `EventNotification` rows | integration | `rtk uv run pytest backend/tests/test_notifications.py backend/tests/test_knowledge_sessions.py -q` | ❌ W0 | ⬜ pending |
| 24-notification-resolve | 02 | 1 | KS-05, KS-06 | T-24-01 | `_resolve_event` resolves visible KS sessions and rejects hidden ones | integration | `rtk uv run pytest backend/tests/test_notifications.py backend/tests/test_knowledge_sessions.py -q` | ❌ W0 | ⬜ pending |
| 24-frontend-api | 03 | 2 | KS-01, KS-02, KS-04 | T-24-05 | API client sends fields but backend derives/validates scope | build | `cd frontend && bun run build` | ❌ W0 | ⬜ pending |
| 24-schedule-tab | 03 | 2 | KS-03 | T-24-01 | `/schedule` contains Knowledge Sessions tab; no new route added | build + manual | `cd frontend && bun run build` | ❌ W0 | ⬜ pending |
| 24-agenda-calendar-toggle | 03 | 2 | KS-03, KS-04 | T-24-01 | Agenda default and calendar toggle render only scoped sessions | build + manual | `cd frontend && bun run build` | ❌ W0 | ⬜ pending |
| 24-session-form | 03 | 2 | KS-01, KS-02 | T-24-03 / T-24-06 | Form validates presenter scope, references render safely, tags normalize | build + manual | `cd frontend && bun run build` | ❌ W0 | ⬜ pending |
| 24-tab-state-isolation | 03 | 2 | KS-03 | T-24-05 | Personal schedule modal state cannot leak into KS form state | manual | Browser walkthrough | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `backend/tests/test_knowledge_sessions.py` — integration tests for scope visibility, presenter validation, session creation, creation notifications, reminders, and notification resolution.
- [ ] Test fixture helpers for two sub-teams, admin, two supervisors or one supervisor plus sibling team, and members.
- [ ] Manual smoke checklist added to the execution summary after frontend work.

Existing backend pytest infrastructure exists, so no new test framework should be introduced.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Knowledge Sessions tab is inside `/schedule`, with no new top-level route | KS-03 | Route/nav placement is user-facing | Navigate to `/schedule`; confirm tab exists and no separate nav link/route was added. |
| Agenda view opens by default and calendar view toggle works | KS-03 | Visual/interaction check | Open tab; confirm agenda list is default; switch to calendar and back. |
| Personal schedule modal state does not leak into KS session form | KS-03 | Svelte local state interaction | Open a personal event edit modal, switch tabs, open KS form; confirm values are empty/defaulted correctly. Repeat in reverse. |
| Member cannot create or edit sessions | KS-02, KS-04 | Role-based UI check | Login as member; confirm create/edit/delete controls are absent and direct API write returns 403. |
| Supervisor presenter list is sub-team scoped | KS-02 | UX plus API validation | Login as supervisor; open create form; confirm sibling-team users are not selectable. Try API POST with sibling presenter and confirm 403. |
| References and tags round-trip cleanly | KS-01 | Form data and rendering check | Create session with multi-line references and several tag chips; refresh; confirm values persist and display without layout breakage. |
| Reminder offsets fire through existing bell | KS-05 | Requires time-based notification transition | Create near-future session with short reminder offset; wait for scheduler tick or call job; confirm bell notification appears. |

---

## Validation Sign-Off

- [ ] All KS requirements have automated or manual verification coverage.
- [ ] Backend scope and presenter validation tests pass.
- [ ] Notification fanout and reminder tests pass.
- [ ] Frontend build passes after `/schedule` changes.
- [ ] Manual state-isolation smoke test passes.
- [ ] `nyquist_compliant: true` set in frontmatter after all checks pass.

**Approval:** pending
