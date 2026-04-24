---
phase: 13
slug: multi-team-hierarchy-timeline-visibility
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-04-24
---

# Phase 13 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 7.x |
| **Config file** | backend/pytest.ini (existing) |
| **Quick run command** | `pytest backend/tests/ -x -v` |
| **Full suite command** | `pytest backend/tests/ -v` |
| **Estimated runtime** | ~5 seconds |

---

## Sampling Rate

- **After every task commit:** Run `pytest backend/tests/ -x -v`
- **After every plan wave:** Run `pytest backend/tests/ -v`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 10 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 13-01-01 | 01 | 1 | TEAM-01 | T-13-01 | Admin can only create/modify sub-teams they have access to | integration | `pytest backend/tests/test_sub_teams.py::test_admin_crud_sub_team -x` | ❌ W0 | ⬜ pending |
| 13-01-02 | 01 | 1 | TEAM-02 | T-13-02 | User.sub_team_id FK enforced, no orphan users | unit | `pytest backend/tests/test_models.py::test_user_sub_team_fk -x` | ❌ W0 | ⬜ pending |
| 13-02-01 | 02 | 1 | TEAM-03 | T-13-03 | Project.sub_team_id FK enforced, projects scoped to sub-team | integration | `pytest backend/tests/test_projects.py::test_project_sub_team_scoping -x` | ❌ W0 | ⬜ pending |
| 13-03-01 | 03 | 1 | TEAM-04 | T-13-04 | Supervisor endpoints reject cross-team data access | integration | `pytest backend/tests/test_performance.py::test_supervisor_scoping -x` | ❌ W0 | ⬜ pending |
| 13-03-02 | 03 | 1 | TEAM-05 | T-13-05 | Admin can switch sub-teams via header, sees org-wide aggregates | integration | `pytest backend/tests/test_dashboard.py::test_admin_all_teams -x` | ❌ W0 | ⬜ pending |
| 13-04-01 | 04 | 1 | VIS-01 | T-13-06 | Timeline filters to member's assigned projects only | integration | `pytest backend/tests/test_timeline.py::test_member_timeline_visibility -x` | ❌ W0 | ⬜ pending |
| 13-04-02 | 04 | 1 | VIS-02 | T-13-07 | Timeline filters to supervisor's sub-team projects | integration | `pytest backend/tests/test_timeline.py::test_supervisor_timeline_visibility -x` | ❌ W0 | ⬜ pending |
| 13-04-03 | 04 | 1 | VIS-03 | T-13-08 | Timeline shows all projects for admin, respects X-SubTeam-ID header | integration | `pytest backend/tests/test_timeline.py::test_admin_timeline_visibility -x` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `backend/tests/test_sub_teams.py` — stubs for TEAM-01
- [ ] `backend/tests/test_timeline.py` — stubs for VIS-01, VIS-02, VIS-03
- [ ] `backend/tests/test_projects.py` — stubs for TEAM-03
- [ ] `backend/tests/test_performance.py` — stubs for TEAM-04
- [ ] `backend/tests/test_dashboard.py` — stubs for TEAM-05
- [ ] `backend/tests/conftest.py` — shared fixtures for sub-team test data
- Framework install: None (pytest already installed)

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Admin global switcher UI placement and styling | D-09, D-10 | Visual design judgment | Navigate as admin, verify switcher appears in nav/sidebar, test switching updates all pages |
| Sub-team management UI on /team page | D-05, D-06, D-07, D-08 | Visual design judgment | Navigate to /team as admin, verify Sub-Teams tab/section exists, test create/rename/reassign flows |
| Timeline empty state for member with zero tasks | Claude's Discretion | Edge case UX | Create member with no assigned tasks, navigate to /timeline, verify empty state message |

*If none: "All phase behaviors have automated verification."*

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 10s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
