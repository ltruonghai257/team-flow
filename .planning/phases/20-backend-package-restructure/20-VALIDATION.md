---
phase: 20
slug: backend-package-restructure
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-04-27
---

# Phase 20 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest |
| **Config file** | `backend/tests/conftest.py` |
| **Quick run command** | `rtk proxy python -m compileall backend/app` |
| **Full suite command** | `rtk pytest backend/tests -q` |
| **Estimated runtime** | ~60-180 seconds |

---

## Sampling Rate

- **After every risky task commit:** Run `rtk proxy python -m compileall backend/app`
- **After model/schema/import waves:** Run targeted backend pytest files touched by the wave
- **After every plan wave:** Run `rtk pytest backend/tests -q` when dependencies are available
- **Before `$gsd-verify-work`:** Full backend suite, Alembic validation, and `/health` smoke must be green or documented with blocker plus fallback
- **Max feedback latency:** 180 seconds for compile/import checks; backend test suite may exceed this locally

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 20-01-01 | 01 | 1 | BACK-01/BACK-03 | T-20-01 | App startup target remains importable | import | `rtk proxy python -m compileall backend/app` | ✅ | ⬜ pending |
| 20-01-02 | 01 | 1 | BACK-01/BACK-03 | T-20-02 | Runtime-adjacent delegates preserve imports | import | `rtk proxy python -m compileall backend/app` | ✅ | ⬜ pending |
| 20-02-01 | 02 | 2 | BACK-01/BACK-02/BACK-04 | T-20-03 | SQLAlchemy metadata remains registered | unit/import | `rtk pytest backend/tests/test_status_sets.py -q` | ✅ | ⬜ pending |
| 20-03-01 | 03 | 3 | BACK-01/BACK-02/BACK-05 | T-20-04 | Pydantic schema imports remain stable | unit/import | `rtk pytest backend/tests -q` | ✅ | ⬜ pending |
| 20-04-01 | 04 | 4 | BACK-03/BACK-05 | T-20-05 | Router registration and API paths remain stable | import/unit | `rtk pytest backend/tests -q` | ✅ | ⬜ pending |
| 20-05-01 | 05 | 5 | BACK-04/BACK-05 | T-20-06 | Alembic/runtime checks complete or document fallback | smoke | `rtk pytest backend/tests -q` | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

Existing infrastructure covers the phase:

- `backend/tests/conftest.py` — async client and DB fixtures
- `backend/alembic.ini` and `backend/alembic/env.py` — migration validation surface
- `backend/tests/*.py` — backend regression suite

No dependency installation is required by this validation strategy.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Phase 19 playbook availability | BACK-01/BACK-03 | Phase 20 depends on a completed prior phase artifact that may not exist at planning time | Before execution, confirm Phase 19 generated `19-BACKEND-MAP.md` and `19-REFACTOR-PLAYBOOK.md`; if missing, stop and complete Phase 19 first |
| Uvicorn `/health` startup smoke | BACK-03 | Requires local process lifecycle and possibly environment variables | Start `uvicorn app.main:app`, request `/health`, confirm `{"status":"ok"}`, then stop the process |
| Alembic upgrade validation | BACK-04 | May require a configured test database | Run Alembic heads/upgrade where DB config allows; otherwise record blocker and run metadata import fallback |

---

## Validation Sign-Off

- [ ] All tasks have automated verify or documented manual fallback
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all missing references
- [ ] No watch-mode flags
- [ ] Feedback latency target documented
- [ ] `nyquist_compliant: true` set in frontmatter after execution confirms validation coverage

**Approval:** pending
