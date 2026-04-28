---
phase: 25
slug: team-weekly-board-ai-summary
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-04-28
---

# Phase 25 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest + httpx AsyncClient for backend; Bun/SvelteKit check/build for frontend |
| **Config file** | `backend/tests/conftest.py`; frontend scripts in `frontend/package.json` |
| **Quick run command** | `cd backend && rtk pytest tests/test_board.py -q` |
| **Full suite command** | `cd backend && rtk pytest tests/test_board.py tests/test_notifications.py -q` plus `cd frontend && rtk bun run check && rtk bun run build` |
| **Estimated runtime** | ~3-5 minutes |

---

## Sampling Rate

- **After every backend task commit:** Run `cd backend && rtk pytest tests/test_board.py -q`
- **After summary-generation or scheduler changes:** Run `cd backend && rtk pytest tests/test_board.py tests/test_notifications.py -q`
- **After frontend `/board` changes:** Run `cd frontend && rtk bun run check` and `cd frontend && rtk bun run build`
- **After every plan wave:** Run the full suite plus a manual `/board` smoke pass
- **Before `$gsd-verify-work`:** Backend tests green, frontend check/build green, manual board checks completed
- **Max feedback latency:** 240 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 25-models-migration | 01 | 1 | BOARD-01, BOARD-02, BOARD-06 | T-25-01 / T-25-04 | Week identity and one-primary-post-per-member-per-week are enforced in persistence | import + migration parse | `rtk python -m compileall backend/app` | ❌ W0 | ⬜ pending |
| 25-primary-post-crud | 02 | 2 | BOARD-01, BOARD-07, BOARD-08 | T-25-02 | Author-only create/edit/delete for primary posts | integration | `cd backend && rtk pytest tests/test_board.py -q` | ❌ W0 | ⬜ pending |
| 25-append-entry-crud | 02 | 2 | BOARD-07, BOARD-08 | T-25-02 | Follow-up entries stay owned by the parent author only | integration | `cd backend && rtk pytest tests/test_board.py -q` | ❌ W0 | ⬜ pending |
| 25-week-query | 02 | 2 | BOARD-02 | T-25-01 | Week payload returns the selected ISO week, grouped posts, and historical choices without cross-team leakage | integration | `cd backend && rtk pytest tests/test_board.py -q` | ❌ W0 | ⬜ pending |
| 25-summary-endpoint | 03 | 2 | BOARD-04, BOARD-06 | T-25-04 / T-25-05 | On-demand summary caches, cools down for 30 minutes, and overwrites after regeneration | integration | `cd backend && rtk pytest tests/test_board.py -q` | ❌ W0 | ⬜ pending |
| 25-empty-week-short-circuit | 03 | 2 | BOARD-05 | T-25-05 | Empty weeks store `No updates this week` without AI call | integration | `cd backend && rtk pytest tests/test_board.py -q` | ❌ W0 | ⬜ pending |
| 25-scheduler-job | 03 | 2 | BOARD-05 | T-25-05 | Sunday 23:00 scheduler hook upserts summaries via the shared service | integration/unit | `cd backend && rtk pytest tests/test_board.py -q` | ❌ W0 | ⬜ pending |
| 25-frontend-markdown | 04 | 3 | BOARD-03 | T-25-03 | Preview and rendered posts sanitize markdown before `{@html}` | build + manual | `cd frontend && rtk bun run check && rtk bun run build` | ❌ W0 | ⬜ pending |
| 25-frontend-week-nav | 04 | 3 | BOARD-02 | T-25-01 | Previous/current/next and picker switch weeks without breaking state | build + manual | `cd frontend && rtk bun run check && rtk bun run build` | ❌ W0 | ⬜ pending |
| 25-frontend-summary-panel | 04 | 3 | BOARD-04, BOARD-06 | T-25-04 | Summary panel shows stored summary, empty state, cooldown state, and no-updates state correctly | build + manual | `cd frontend && rtk bun run check && rtk bun run build` | ❌ W0 | ⬜ pending |
| 25-frontend-author-actions | 04 | 3 | BOARD-07, BOARD-08 | T-25-02 | Edit/delete/add-follow-up actions render only for the author in current week | build + manual | `cd frontend && rtk bun run check && rtk bun run build` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `backend/tests/test_board.py` — coverage for primary posts, append entries, week queries, summary cooldown, empty-week short-circuit, and scheduler behavior
- [ ] Summary-service stubbing/mocking approach for AI calls documented in tests
- [ ] Manual `/board` smoke checklist recorded in execution summaries

Existing pytest infrastructure already exists; no new test framework should be introduced.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| `/board` route appears in sidebar and loads as a summary-first page | BOARD-01, BOARD-02 | Layout/navigation and scan-order are user-facing | Navigate to `/board`; confirm week navigator, summary panel, composer, then digest list. |
| Past weeks are read-only | BOARD-02, BOARD-07, BOARD-08 | UX/state interaction check | Switch to a previous week and confirm create/edit/delete/add-follow-up actions are hidden or disabled. |
| Markdown preview and render stay sanitized | BOARD-03 | Requires actual rendered HTML inspection | Enter markdown with formatting and unsafe HTML/script attempts; confirm formatting works and unsafe content does not execute. |
| Current-week summary button cools down visibly | BOARD-04, BOARD-06 | Needs end-to-end state display | Trigger summary twice within 30 minutes and confirm cached result is shown with cooldown text. |
| Empty week shows quiet no-updates states | BOARD-05 | UI copy/state check | Open a week with no posts and confirm both board and summary states match approved copy. |
| Author-only actions do not appear on another member's content | BOARD-07, BOARD-08 | Multi-user UI verification | Login as member A and member B in separate sessions; confirm B cannot edit/delete A's primary post or append entries. |

---

## Validation Sign-Off

- [ ] All BOARD requirements have automated or manual coverage.
- [ ] Backend ownership and cooldown tests pass.
- [ ] Empty-week summary path proves no AI call is required.
- [ ] Frontend check/build pass after `/board` work.
- [ ] Manual current-week and past-week board smoke tests pass.
- [ ] `nyquist_compliant: true` set in frontmatter after all checks pass.

**Approval:** pending
