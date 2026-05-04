---
phase: 28
slug: milestone-planning-decisions
status: green
nyquist_compliant: true
wave_0_complete: true
created: 2026-04-29
---

# Phase 28 - Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest + Playwright |
| **Config file** | `backend/pyproject.toml`, `frontend/playwright.config.ts` |
| **Quick run command** | `cd backend && rtk uv run pytest tests/test_milestones.py -q` |
| **Full suite command** | `cd backend && rtk uv run pytest tests/test_milestones.py tests/test_timeline.py tests/test_tasks.py -q && cd ../frontend && bun run check && bun x playwright test tests/milestones.spec.ts --workers=1` |
| **Estimated runtime** | ~90 seconds |

---

## Sampling Rate

- **After every task commit:** Run the plan's focused backend or frontend quick check.
- **After every plan wave:** Run `cd backend && rtk uv run pytest tests/test_milestones.py tests/test_timeline.py tests/test_tasks.py -q && cd ../frontend && bun run check`.
- **Before `$gsd-verify-work`:** Full suite must be green.
- **Max feedback latency:** 120 seconds.

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 28-01-01 | 01 | 1 | ML-03, ML-04 | T-28-01 | Decision endpoints require an authenticated user and valid milestone/task ownership by existing project scope | backend API | `cd backend && rtk uv run pytest tests/test_milestones.py -q` | W0 | green |
| 28-02-01 | 02 | 2 | ML-01, ML-02, ML-04 | T-28-02 | Enriched milestone responses do not leak tasks outside existing project/sub-team visibility rules | backend API | `cd backend && rtk uv run pytest tests/test_milestones.py tests/test_timeline.py tests/test_tasks.py -q` | W0 | green |
| 28-03-01 | 03 | 3 | ML-01, ML-02, ML-03 | T-28-03 | Milestone command view uses existing authenticated API calls and does not expose inline task mutation controls | frontend/browser | `cd frontend && bun run check && bun x playwright test tests/milestones.spec.ts --workers=1` | W0 | green |
| 28-04-01 | 04 | 4 | ML-01, ML-02, ML-03, ML-04 | T-28-04 | Regression suite proves planning-state, task rollup, and decision UI paths remain covered | regression | `cd backend && rtk uv run pytest tests/test_milestones.py tests/test_timeline.py tests/test_tasks.py -q && cd ../frontend && bun run check && bun x playwright test tests/milestones.spec.ts --workers=1` | W0 | green |

*Status: pending / green / red / flaky*

---

## Wave 0 Requirements

- [x] `backend/tests/test_milestones.py` - backend fixtures and assertions for ML-01 through ML-04.
- [x] `frontend/tests/milestones.spec.ts` - mocked-browser coverage for lanes, expansion, task links, and decision controls.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Responsive visual scan of four planning-state lanes | ML-01 | Browser tests can assert presence but not supervisor scan quality | Open `/milestones` at desktop and mobile widths; confirm Planned, Committed, Active, and Completed are visible/stacked and active/risky cards are expanded by default. |

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies.
- [x] Sampling continuity: no 3 consecutive tasks without automated verify.
- [x] Wave 0 covers all MISSING references.
- [x] No watch-mode flags.
- [x] Feedback latency < 120s.
- [x] `nyquist_compliant: true` set in frontmatter once tests exist and pass.

**Approval:** green
