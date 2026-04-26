---
phase: 17
slug: sprint-release-reminders
status: draft
nyquist_compliant: true
wave_0_complete: false
created: 2026-04-26
---

# Phase 17 - Validation Strategy

## Test Infrastructure

| Property | Value |
|----------|-------|
| Framework | pytest |
| Config file | `backend/pytest.ini` or backend test defaults |
| Quick run command | `python -m compileall backend/app` |
| Full suite command | `cd backend && pytest tests/test_notifications.py tests/test_sub_teams.py tests/test_sprints.py` |
| Estimated runtime | ~60 seconds |

## Sampling Rate

- After every task commit: run `python -m compileall backend/app`
- After backend reminder service/API plans: run the relevant focused pytest file if dependencies are installed
- After frontend plan: run `cd frontend && bun run check`
- Before `$gsd-verify-work`: full backend focused suite plus frontend check must be green or blockers recorded
- Max feedback latency: 90 seconds

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 17-01-01 | 01 | 1 | REMIND-01/02 | T-17-01 | Settings are scoped by sub-team | unit/API | `cd backend && pytest tests/test_sub_teams.py` | existing | pending |
| 17-01-02 | 01 | 1 | REMIND-01/02 | T-17-02 | Partial uniqueness avoids duplicate generated reminders without breaking schedule/task offsets | unit | `cd backend && pytest tests/test_notifications.py` | W0 | pending |
| 17-02-01 | 02 | 2 | REMIND-01/02 | T-17-03 | Recipients are deduped and supervisor visibility is scoped | unit | `cd backend && pytest tests/test_notifications.py` | W0 | pending |
| 17-03-01 | 03 | 3 | REMIND-01/02 | T-17-04 | Date changes rebuild pending reminders only | API/unit | `cd backend && pytest tests/test_sprints.py tests/test_notifications.py` | W0 | pending |
| 17-04-01 | 04 | 4 | REMIND-01/02 | T-17-05 | Supervisor proposals cannot directly change settings | API/UI | `cd backend && pytest tests/test_sub_teams.py` | existing | pending |
| 17-05-01 | 05 | 5 | REMIND-01/02 | T-17-06 | Bell routes generated reminder types to expected surfaces | frontend | `cd frontend && bun run check` | existing | pending |

## Wave 0 Requirements

- [ ] `backend/tests/test_notifications.py` - generated reminder service and duplicate prevention tests
- [ ] `backend/tests/test_sub_teams.py` - extend settings/proposal permission tests
- [ ] `backend/tests/test_sprints.py` or `backend/tests/test_milestones.py` - date-change rebuild coverage

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Bell toast and route behavior | REMIND-01/02 | Requires running frontend app and notification polling | Create/schedule reminder rows, wait for poll, click sprint/milestone/proposal notifications |
| Admin active sub-team selection | REMIND-01/02 | Depends on global switcher state | Switch active sub-team as admin, update reminder settings, confirm only that sub-team changes |

## Validation Sign-Off

- [ ] All tasks have automated or explicit manual verification
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers missing notification tests
- [ ] No watch-mode flags
- [ ] Feedback latency under 90 seconds
- [x] `nyquist_compliant: true` set in frontmatter

Approval: pending
