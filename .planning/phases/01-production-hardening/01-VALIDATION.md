---
phase: 01
slug: production-hardening
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-04-22
---

# Phase 01 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest (to be added) |
| **Config file** | none — Wave 0 installs |
| **Quick run command** | `pytest` |
| **Full suite command** | `pytest` |
| **Estimated runtime** | ~10 seconds |

---

## Sampling Rate

- **After every task commit:** Run `pytest`
- **After every plan wave:** Run `pytest`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 10 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 01-01-01 | 01 | 1 | REQ-01 | T-01-01 | Reject weak SECRET_KEY in prod | unit | `pytest backend/tests/test_config.py` | ❌ W0 | ⬜ pending |
| 01-01-02 | 01 | 1 | REQ-01 | T-01-02 | Enforce rate limits | unit | `pytest backend/tests/test_rate_limits.py` | ❌ W0 | ⬜ pending |
| 01-01-03 | 01 | 2 | REQ-01 | T-01-03 | Prevent CORS bypass | unit | `pytest backend/tests/test_cors.py` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `backend/requirements-dev.txt` — pytest, httpx, pytest-asyncio
- [ ] `backend/tests/` — structure
- [ ] `backend/tests/conftest.py` — shared fixtures

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Migration | REQ-01 | Startup DB ops | Run app locally and verify logs for `alembic upgrade head` |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 10s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
