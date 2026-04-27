---
phase: 22
slug: runtime-integration-regression-verification
status: draft
nyquist_compliant: true
wave_0_complete: true
created: 2026-04-27
---

# Phase 22 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Backend framework** | pytest (existing, `backend/tests/`) |
| **Frontend type-check** | `svelte-check` via `bun run check` |
| **Frontend build** | `vite build` via `bun run build` |
| **E2E framework** | Playwright (`frontend/playwright.config.ts`, mobile-chrome project) |
| **Quick run command (backend)** | `cd backend && python -m pytest -q` |
| **Quick run command (frontend)** | `cd frontend && bun run check` |
| **Full E2E command** | `cd frontend && bunx playwright test` |
| **Estimated runtime** | ~30s pytest + ~15s check + ~10s build + ~60s playwright |

---

## Sampling Rate

- **After every task commit:** Run the task's `<verify>` command.
- **After every plan wave:** Run the relevant suite (backend pytest, frontend check+build, or Playwright).
- **Before phase signoff:** All four verification layers green and recorded in `22-VERIFICATION.md`.
- **Max feedback latency:** ~30 seconds (pytest is the longest fast loop).

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 22-01-01 | 01 | 1 | RUN-01 | T-22-01 | Uvicorn target resolves to canonical app | static | `rtk rg "app\.api\.main:app" supervisord.conf` | ✅ | ⬜ pending |
| 22-01-02 | 01 | 1 | RUN-01 | T-22-01 | Backend container CMD points at canonical app | static | `rtk rg "app\.api\.main:app" backend/Dockerfile` | ✅ | ⬜ pending |
| 22-01-03 | 01 | 1 | RUN-01, BACK-04 | T-22-02 | Alembic env still resolves canonical metadata | runtime | `cd backend && python -c "from alembic.config import Config; from alembic import command; command.current(Config('alembic.ini'))"` | ✅ | ⬜ pending |
| 22-01-04 | 01 | 1 | RUN-01 | T-22-01 | Compose + Azure scripts still align with canonical entrypoint | static | `rtk rg "app\.main:app" Dockerfile docker-compose.yml scripts/` | ✅ (no matches expected outside comments) | ⬜ pending |
| 22-02-01 | 02 | 2 | VERIFY-01 | T-22-03 | Backend pytest passes after entrypoint update | unit/integration | `cd backend && python -m pytest -q` | ✅ | ⬜ pending |
| 22-02-02 | 02 | 2 | VERIFY-02, RUN-02 | T-22-03 | Frontend type-check clean | type | `cd frontend && bun run check` | ✅ | ⬜ pending |
| 22-02-03 | 02 | 2 | VERIFY-02, RUN-02 | T-22-03 | Frontend production build succeeds | build | `cd frontend && bun run build` | ✅ | ⬜ pending |
| 22-02-04 | 02 | 2 | VERIFY-01, VERIFY-02 | T-22-03 | Verification floor results recorded | doc | `rtk rg "## Backend pytest|## Frontend check|## Frontend build" .planning/phases/22-runtime-integration-regression-verification/22-VERIFICATION.md` | ✅ | ⬜ pending |
| 22-03-01 | 03 | 2 | VERIFY-03 | T-22-04 | Playwright run passes (or fallback documented) | e2e | `cd frontend && bunx playwright test --reporter=list` | ✅ | ⬜ pending |
| 22-03-02 | 03 | 2 | VERIFY-03 | T-22-04 | Manual smoke: login + session + board | manual | curl/browser session recorded in `22-VERIFICATION.md` | ✅ | ⬜ pending |
| 22-03-03 | 03 | 2 | VERIFY-03 | T-22-04 | Manual smoke: AI input + WebSocket + scheduler + /health | manual | curl/wscat/browser session recorded in `22-VERIFICATION.md` | ✅ | ⬜ pending |
| 22-04-01 | 04 | 3 | VERIFY-04 | T-22-05 | Migration guide created with three required sections | doc | `rtk rg "## Old to New Import Paths|## Shim Ledger|## Runtime Runbook" docs/MIGRATION-V2.1.md` | ✅ | ⬜ pending |
| 22-04-02 | 04 | 3 | VERIFY-04 | T-22-05 | Shim ledger baselines recorded with grep counts | doc | `rtk rg "Baseline callsite count" docs/MIGRATION-V2.1.md` | ✅ | ⬜ pending |
| 22-04-03 | 04 | 3 | VERIFY-04 | T-22-05 | README + backend/CLAUDE.md point to migration guide | doc | `rtk rg "MIGRATION-V2.1" README.md backend/CLAUDE.md` | ✅ | ⬜ pending |
| 22-04-04 | 04 | 3 | RUN-01, RUN-02, RUN-03, VERIFY-01..04 | T-22-05 | Final signoff block in `22-VERIFICATION.md` | doc | `rtk rg "## Final Signoff|Phase 22 verified" .planning/phases/22-runtime-integration-regression-verification/22-VERIFICATION.md` | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

Existing infrastructure covers all phase requirements: pytest, svelte-check, vite, Playwright, and project structure tests are already installed by Phase 20-05 / 21-04. No Wave 0 install needed.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| WebSocket `/ws/chat` connection | VERIFY-03 | No Playwright coverage; needs auth cookie + websocket client | Log in, capture cookie, connect with `wscat` or browser devtools, send message, confirm ack/echo. Record snippet in `22-VERIFICATION.md`. |
| Scheduler tick / reminder generation | VERIFY-03 | Time-bound; needs running app + DB | After app startup, confirm scheduler log line. Insert a sprint reminder fixture (or wait one tick), poll `/api/notifications`, observe row. Record in `22-VERIFICATION.md`. |
| AI task input | VERIFY-03 | Calls external AI provider; not in Playwright | Hit `/api/ai/breakdown` (or equivalent) with seeded prompt; record HTTP status + first sub-task. If provider key missing, document blocker + fallback (mock client log). |
| `/health` | VERIFY-03 | Trivial; included for completeness | `curl http://localhost:8000/health` → `{"status":"ok"}`. Record in `22-VERIFICATION.md`. |
| Login + session | VERIFY-03 | Already covered by Playwright in CI but recorded manually as well | `POST /api/auth/token` then `GET /api/auth/me`. Record both responses (status only, redact tokens). |
| Task board load | VERIFY-03 | Visual confirmation outside Playwright | Navigate `/tasks`, confirm board renders columns and tasks. Record screenshot path or one-line note. |

If any smoke is environment-blocked, document the exact blocker and the strongest fallback that ran (CONTEXT D-11).

---

## Validation Sign-Off

- [ ] All tasks have `<verify>` automated checks or fall back to documented manual recording.
- [ ] Sampling continuity: every plan wave runs at least one automated check.
- [ ] Wave 0 not required (existing infrastructure).
- [ ] No watch-mode flags used in CI commands.
- [ ] Feedback latency < 30s for the per-task quick command.
- [ ] `nyquist_compliant: true` set in frontmatter.

**Approval:** pending — set to `approved YYYY-MM-DD` after Plan 22-04 records final signoff.
