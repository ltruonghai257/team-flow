---
phase: 15
slug: custom-kanban-statuses
status: draft
nyquist_compliant: true
wave_0_complete: false
created: 2026-04-26
---

# Phase 15 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest for backend; Svelte check and Playwright for frontend smoke coverage |
| **Config file** | `backend/tests/conftest.py`; `frontend/playwright.config.ts`; `frontend/package.json` |
| **Quick run command** | `cd backend && pytest tests/test_tasks.py tests/test_status_sets.py` |
| **Full suite command** | `cd backend && pytest && cd ../frontend && bun run check` |
| **Estimated runtime** | ~90 seconds |

---

## Sampling Rate

- **After every task commit:** Run the quickest relevant backend test or `cd frontend && bun run check` for frontend-only edits.
- **After every plan wave:** Run `cd backend && pytest && cd ../frontend && bun run check`.
- **Before `$gsd-verify-work`:** Full suite must be green.
- **Max feedback latency:** 120 seconds.

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 15-01-01 | 01 | 1 | STATUS-03 | T-15-01 | Migration preserves task rows and `completed_at` | migration/test | `cd backend && pytest tests/test_status_sets.py` | ❌ W0 | ⬜ pending |
| 15-01-02 | 01 | 1 | STATUS-03, STATUS-04 | T-15-02 | `Task.custom_status_id` and `CustomStatus.is_done` exist without dropping `Task.status` | compile/test | `python -m compileall backend/app` | ✅ | ⬜ pending |
| 15-02-01 | 02 | 2 | STATUS-01 | T-15-03 | Members cannot mutate status sets; supervisors/admins scoped correctly | API test | `cd backend && pytest tests/test_status_sets.py` | ❌ W0 | ⬜ pending |
| 15-02-02 | 02 | 2 | STATUS-02 | T-15-04 | Project overrides inherit, copy, map, and revert safely | API test | `cd backend && pytest tests/test_status_sets.py` | ❌ W0 | ⬜ pending |
| 15-02-03 | 02 | 2 | STATUS-04 | T-15-05 | `completed_at` follows old/new `is_done` transitions | API test | `cd backend && pytest tests/test_tasks.py tests/test_status_sets.py` | ❌ W0 | ⬜ pending |
| 15-03-01 | 03 | 3 | STATUS-01, STATUS-02 | T-15-06 | Frontend API sends existing auth/sub-team headers through shared request wrapper | typecheck | `cd frontend && bun run check` | ✅ | ⬜ pending |
| 15-04-01 | 04 | 4 | STATUS-01, STATUS-02 | T-15-07 | `/tasks` and `/projects` use DB statuses and do not expose unsafe delete behavior | typecheck/manual | `cd frontend && bun run check` | ✅ | ⬜ pending |
| 15-05-01 | 05 | 5 | STATUS-01, STATUS-02, STATUS-03, STATUS-04 | T-15-08 | End-to-end status workflows pass automated checks and manual UAT | full | `cd backend && pytest && cd ../frontend && bun run check` | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `backend/tests/test_status_sets.py` — fixtures and API tests for status set create/update/reorder/archive/delete/project override behavior.
- [ ] `backend/tests/test_tasks.py` — task create/update tests for legacy status mapping, `custom_status_id`, and `completed_at` transitions.
- [ ] Existing `backend/tests/conftest.py` — reuse app/database fixtures; add helpers only if needed.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Drag-and-drop status reorder feels immediate on `/tasks` and `/projects` | STATUS-01, STATUS-02 | Existing frontend test coverage is mobile-smoke oriented, not full DnD business workflow coverage | Login as supervisor, reorder statuses, refresh, verify same order and board columns update |
| Project override revert prompts for unmatched slug fallback | STATUS-02 | Requires user decision path that is cumbersome to express without full browser fixtures | Create project override, rename one slug-equivalent status so it no longer matches, revert, verify fallback prompt blocks silent migration |
| Archive behavior hides status from new selections while existing tasks retain it | STATUS-01 | Needs visual confirmation across create/edit forms and existing cards | Archive assigned status, open task create/edit forms, verify archived status is hidden from selectors and existing task still displays archived status |

---

## Validation Sign-Off

- [x] All tasks have planned automated verification or Wave 0 dependencies.
- [x] Sampling continuity: no 3 consecutive tasks without automated verify.
- [x] Wave 0 covers all missing backend test files.
- [x] No watch-mode flags.
- [x] Feedback latency target is under 120 seconds.
- [x] `nyquist_compliant: true` set in frontmatter.

**Approval:** approved 2026-04-26
