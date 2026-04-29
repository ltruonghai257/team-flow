---
phase: 29
slug: scoped-team-visibility-leadership-rbac
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-04-29
---

# Phase 29 - Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest + Playwright |
| **Config file** | `backend/pyproject.toml`, `frontend/playwright.config.ts` |
| **Quick run command** | `cd backend && rtk uv run pytest tests/test_visibility.py -q` |
| **Full suite command** | `cd backend && rtk uv run pytest tests/test_visibility.py tests/test_sub_teams.py tests/test_projects.py tests/test_tasks.py tests/test_timeline.py tests/test_milestones.py tests/test_board.py tests/test_knowledge_sessions.py -q && cd ../frontend && bun run check && bun x playwright test tests/navigation-groups.spec.ts tests/team-visibility.spec.ts --workers=1` |
| **Estimated runtime** | ~150 seconds |

---

## Sampling Rate

- **After every task commit:** Run the focused check named in that task.
- **After every plan wave:** Run the backend scoped regression check for backend waves, and frontend check for the frontend/seed wave.
- **Before `$gsd-verify-work`:** Full suite must be green.
- **Max feedback latency:** 180 seconds.

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 29-01-01 | 01 | 1 | VIS-01, VIS-02, VIS-03, VIS-04, VIS-07 | T-29-01, T-29-02 | Shared role and scope helpers return only allowed users/teams for each role | backend API/unit | `cd backend && rtk uv run pytest tests/test_visibility.py -q` | W0 | pending |
| 29-02-01 | 02 | 2 | VIS-02, VIS-03, VIS-04, VIS-06 | T-29-03, T-29-04 | Leadership role assignment and invite scope are manager-controlled and member-management is scoped | backend API | `cd backend && rtk uv run pytest tests/test_visibility.py tests/test_sub_teams.py -q` | W0 | pending |
| 29-03-01 | 03 | 3 | VIS-01, VIS-02, VIS-03, VIS-04, VIS-05 | T-29-05, T-29-06 | People-aware data endpoints do not leak out-of-scope records through list or detail endpoints | backend API | `cd backend && rtk uv run pytest tests/test_visibility.py tests/test_projects.py tests/test_tasks.py tests/test_timeline.py tests/test_milestones.py tests/test_board.py tests/test_knowledge_sessions.py -q` | W0 | pending |
| 29-04-01 | 04 | 4 | VIS-01, VIS-02, VIS-03, VIS-04, VIS-05, VIS-06, VIS-07 | T-29-07 | Frontend roles/navigation/team UI and demo seed data match the backend visibility contract | frontend/browser/seed | `cd frontend && bun run check && bun x playwright test tests/navigation-groups.spec.ts tests/team-visibility.spec.ts --workers=1 && cd ../backend && python -m app.scripts.seed_demo` | W0 | pending |

*Status: pending / green / red / flaky*

---

## Wave 0 Requirements

- [ ] `backend/tests/test_visibility.py` - shared fixtures and assertions for VIS-01 through VIS-07.
- [ ] `frontend/tests/team-visibility.spec.ts` - mocked-browser coverage for role-aware navigation and `/team` affordances.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Manager/supervisor/assistant manager/member demo walkthrough | VIS-01 through VIS-07 | Browser tests can assert affordances, but a quick human scan catches role-language and scope-selector mistakes | Reseed demo data, log in as each demo role, and confirm visible nav, `/team`, `/timeline`, `/milestones`, `/updates`, `/board`, and `/schedule` match the role scope. |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies.
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify.
- [ ] Wave 0 covers all MISSING references.
- [ ] No watch-mode flags.
- [ ] Feedback latency < 180s.
- [ ] `nyquist_compliant: true` set in frontmatter once tests exist and pass.

**Approval:** pending
