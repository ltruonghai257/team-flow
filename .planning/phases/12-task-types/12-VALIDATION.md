---
phase: 12
slug: task-types
status: approved
nyquist_compliant: true
wave_0_complete: true
created: 2026-04-24
---

# Phase 12 - Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Python `py_compile` + ripgrep acceptance checks + Playwright |
| **Config file** | `backend/alembic.ini`, `frontend/package.json`, `frontend/playwright.config.ts` |
| **Quick run command** | `python -m py_compile backend/app/models.py backend/app/schemas.py backend/app/routers/tasks.py backend/alembic/versions/7b9f1c2d3e4a_add_task_type.py` |
| **Full suite command** | `cd frontend && bun x playwright test tests/mobile/task-types.spec.ts --project=mobile-chrome` |
| **Estimated runtime** | ~5-15 seconds |

---

## Sampling Rate

- **After backend model/schema/router work:** Run backend syntax and acceptance checks.
- **After migration work:** Run `rg -n "tasktype|TaskType|type = Column" backend/app backend/alembic/versions`.
- **After frontend UI work:** Run focused Playwright task type coverage.
- **Before `$gsd-verify-work`:** Backend checks and focused Playwright coverage must be green.
- **Max feedback latency:** 90 seconds.

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 12-01-01 | 01 | 1 | TYPE-01, TYPE-03 | T-12-01 | Invalid type values are rejected or coerced before persistence | syntax/grep | `python -m py_compile backend/app/models.py backend/app/schemas.py backend/app/routers/tasks.py backend/alembic/versions/7b9f1c2d3e4a_add_task_type.py` | yes | green |
| 12-01-02 | 01 | 1 | TYPE-01, TYPE-03 | T-12-02 | Migration gives existing tasks non-null `task` type | grep | `rg -n "TaskType|type = Column\\(Enum\\(TaskType\\)|tasktype|server_default" backend/app backend/alembic/versions` | yes | green |
| 12-01-03 | 01 | 2 | TYPE-02 | T-12-03 | Type filter only accepts fixed type values | grep | `rg -n "Invalid task type filter|Task.type.in_|valid_type" backend/app/routers/tasks.py` | yes | green |
| 12-01-04 | 01 | 3 | TYPE-01, TYPE-02 | N/A | Type controls and badges are keyboard-readable and text-labeled | Playwright | `cd frontend && bun x playwright test tests/mobile/task-types.spec.ts --project=mobile-chrome` | yes | green |
| 12-01-05 | 01 | 4 | TYPE-01, TYPE-02 | N/A | AI suggestions remain user-confirmable before create | Playwright | `cd frontend && bun x playwright test tests/mobile/task-types.spec.ts --project=mobile-chrome` | yes | green |

*Status: pending / green / red / flaky*

---

## Wave 0 Requirements

Existing infrastructure covers this phase:

- Alembic is already configured.
- `frontend/package.json` already provides `bun run check`.
- No new testing framework is required for Phase 12.

---

## Manual-Only Verifications

All phase behaviors have automated verification through `frontend/tests/mobile/task-types.spec.ts`.

---

## Validation Audit 2026-04-24

| Metric | Count |
|--------|-------|
| Gaps found | 0 |
| Resolved | 0 |
| Escalated | 0 |

Automated evidence:

- `python -m py_compile backend/app/models.py backend/app/schemas.py backend/app/routers/tasks.py backend/alembic/versions/7b9f1c2d3e4a_add_task_type.py` passed.
- `rg -n "TaskType|type = Column\\(Enum\\(TaskType\\)|tasktype|server_default|Invalid task type filter|Task.type.in_|valid_type" backend/app backend/alembic/versions` passed.
- `cd frontend && bun x playwright test tests/mobile/task-types.spec.ts --project=mobile-chrome` passed with 4 tests.

---

## Validation Sign-Off

- [x] All tasks have automated verify or manual review steps.
- [x] Sampling continuity: no 3 consecutive tasks without automated verify.
- [x] Wave 0 covers all missing references.
- [x] No watch-mode flags.
- [x] Feedback latency < 90s.
- [x] `nyquist_compliant: true` set in frontmatter.

**Approval:** approved 2026-04-24
