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
| **Framework** | Python import checks + SvelteKit `svelte-check` |
| **Config file** | `backend/alembic.ini`, `frontend/package.json` |
| **Quick run command** | `cd backend && python -c "from app.models import TaskType; from app.routers.tasks import router; print('task type OK')"` |
| **Full suite command** | `cd frontend && bun run check` |
| **Estimated runtime** | ~30-90 seconds |

---

## Sampling Rate

- **After backend model/schema/router work:** Run backend import check.
- **After migration work:** Run `rg -n "tasktype|TaskType|type = Column" backend/app backend/alembic/versions`.
- **After frontend UI work:** Run `cd frontend && bun run check`.
- **Before `$gsd-verify-work`:** Backend import check and frontend check must be green.
- **Max feedback latency:** 90 seconds.

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 12-01-01 | 01 | 1 | TYPE-01, TYPE-03 | T-12-01 | Invalid type values are rejected or coerced before persistence | import/grep | `cd backend && python -c "from app.models import TaskType; from app.schemas import TaskCreate, TaskOut; print('task type imports OK')"` | yes | pending |
| 12-01-02 | 01 | 1 | TYPE-01, TYPE-03 | T-12-02 | Migration gives existing tasks non-null `task` type | grep | `rg -n "tasktype|server_default='task'|server_default=sa.text\\('task'\\)" backend/alembic/versions` | yes | pending |
| 12-01-03 | 01 | 2 | TYPE-02 | T-12-03 | Type filter only accepts fixed type values | import/grep | `cd backend && python -c "from app.routers.tasks import router; print('tasks router OK')"` | yes | pending |
| 12-01-04 | 01 | 3 | TYPE-01, TYPE-02 | N/A | Type controls and badges are keyboard-readable and text-labeled | typecheck | `cd frontend && bun run check` | yes | pending |
| 12-01-05 | 01 | 4 | TYPE-01, TYPE-02 | N/A | AI suggestions remain user-confirmable before create | typecheck | `cd frontend && bun run check` | yes | pending |

*Status: pending / green / red / flaky*

---

## Wave 0 Requirements

Existing infrastructure covers this phase:

- Alembic is already configured.
- `frontend/package.json` already provides `bun run check`.
- No new testing framework is required for Phase 12.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Type selector placement | TYPE-01 | Visual placement is not covered by import/type checks | Open New Task and Edit Task modals; confirm `Type` appears beside `Status` and `Priority`. |
| Icon plus label badges | TYPE-02 | Visual density and badge wrapping need UI review | Confirm list, Kanban, and Agile views show text-labeled task type badges without overflow. |
| Multi-select type filter | TYPE-02 | Requires interactive filter behavior review | Select two type chips and confirm list, Kanban, and Agile views only show matching task types. |
| AI suggestion confirmation | TYPE-01 | Requires checking user review step | Run AI parse or breakdown and confirm suggested type appears in editable controls before create. |

---

## Validation Sign-Off

- [x] All tasks have automated verify or manual review steps.
- [x] Sampling continuity: no 3 consecutive tasks without automated verify.
- [x] Wave 0 covers all missing references.
- [x] No watch-mode flags.
- [x] Feedback latency < 90s.
- [x] `nyquist_compliant: true` set in frontmatter.

**Approval:** approved 2026-04-24
