# Phase 22: Runtime Integration & Regression Verification - Research

**Phase:** 22 - Runtime Integration & Regression Verification
**Date:** 2026-04-27
**Status:** Complete

## Research Question

What does the planner need to know to repoint every runtime entrypoint at the refactored backend package, exercise the four-layer verification floor, and produce the v2.1 migration guide and shim ledger — without changing product behavior, UI visuals, or database schema?

## Inputs Read

- `.planning/phases/22-runtime-integration-regression-verification/22-CONTEXT.md`
- `.planning/phases/19-refactor-map-safety-baseline/19-SAFETY-BASELINE.md`
- `.planning/phases/19-refactor-map-safety-baseline/19-REFACTOR-PLAYBOOK.md`
- `.planning/phases/20-backend-package-restructure/20-CONTEXT.md`
- `.planning/phases/20-backend-package-restructure/20-SUMMARY.md`
- `.planning/phases/21-frontend-sveltekit-structure/21-04-SUMMARY.md`
- `.planning/STATE.md`, `.planning/REQUIREMENTS.md`, `.planning/ROADMAP.md`
- `supervisord.conf`, `Dockerfile`, `backend/Dockerfile`, `docker-compose.yml`
- `backend/alembic.ini`, `backend/alembic/env.py`
- `backend/app/main.py` (Phase 20 delegate), `backend/app/api/main.py`
- `scripts/setup-azure.sh`, `scripts/deploy.sh`
- `frontend/playwright.config.ts`, `frontend/tests/`

## Primary Findings

### Current Runtime Entrypoint State (post-Phase 20/21)

- Canonical FastAPI app: `app.api.main:app` (factory `create_app()` + module-level `app`).
- `backend/app/main.py` is a Phase 20 HIGH-RISK delegate: `from app.api.main import app, create_app, run_migrations`. It currently keeps the old `app.main:app` uvicorn target working.
- `supervisord.conf` `[program:uvicorn]` command line still references `app.main:app`.
- Root `Dockerfile` does not pin a uvicorn target itself — it shells out to supervisord which runs the uvicorn command above. The `backend/Dockerfile` (used by `docker-compose.yml`) ends with `CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]`.
- `scripts/setup-azure.sh` and `scripts/deploy.sh` deploy the monolith image; they do not embed an uvicorn target. App Service runs whatever `CMD` the image declares (supervisord). No code changes required in these scripts as long as supervisord is updated.
- `backend/alembic/env.py` already imports canonical paths: `from app.core.config import settings`, `from app.db.database import Base`, `import app.models`. Phase 20 SUMMARY confirms this is done.
- `backend/alembic.ini` uses `script_location = %(here)s/alembic` (relative) — runs correctly when launched from `backend/` (matches supervisord `directory=/app/backend`). No change needed.

Planning implication: Phase 22 must update **two** uvicorn targets (`supervisord.conf`, `backend/Dockerfile`) plus the no-op verification of `Dockerfile`, `docker-compose.yml`, alembic, and the deploy scripts.

### Shim Inventory (from Phase 20 SUMMARY + 21-04 SUMMARY)

Live compatibility shims that Phase 22 must inventory in the shim ledger and baseline-grep:

| Shim | Path | Delegate Target | Risk |
|------|------|-----------------|------|
| `app.main` | `backend/app/main.py` | `app.api.main` | HIGH (uvicorn target — survives until supervisord/Dockerfile updated) |
| `app.models` | `backend/app/models.py` | `app.models/` package `__init__` re-exports | shadowed by package; tests rely on aggregate exports |
| `app.schemas` | `backend/app/schemas.py` | `app.schemas/` package `__init__` re-exports | shadowed by package |
| `app.config` | `backend/app/config.py` | `app.core.config` | LOW |
| `app.database` | `backend/app/database.py` | `app.db.database` | LOW |
| `app.limiter` | `backend/app/limiter.py` | `app.core.limiter` | LOW |
| `app.auth` | `backend/app/auth.py` | `app.utils.auth` | LOW |
| `app.ai_client` | `backend/app/ai_client.py` | `app.utils.ai_client` | LOW |
| `app.email_service` | `backend/app/email_service.py` | `app.utils.email_service` | LOW |
| `app.scheduler_jobs` | `backend/app/scheduler_jobs.py` | `app.internal.scheduler_jobs` | LOW |
| `app.websocket.manager` | `backend/app/websocket/manager.py` | `app.socket.manager` | LOW |

Frontend shims: Phase 21-04 deleted `frontend/src/lib/api.ts`; no frontend shim remains. The shim ledger entry for it is "removed in Phase 21".

CONTEXT.md D-04/D-05/D-14: Phase 22 leaves these shims in place. Each row in the shim ledger gets a removal trigger (e.g., "callsite count outside `.planning/phases/` is zero") and an exact grep command. Phase 22 records the **current baseline count** for each shim so the future cleanup milestone has an objective trigger.

### Test / Verification Surface

- Backend pytest suite: `backend/tests/` has 11 test files including `test_package_structure.py` (20 import/identity tests added in Phase 20-05). Run from `backend/` with `pytest` or `python -m pytest`.
- Frontend: `cd frontend && bun run check` and `cd frontend && bun run build`. Phase 21-04 confirmed both pass post-refactor.
- Playwright: `frontend/playwright.config.ts` has `mobile-chrome` project with `webServer: bun run dev` on port 5173. Tests: `sprint_board.spec.ts`, `status_transition.spec.ts`, plus `mobile/` directory. Run with `cd frontend && bun run test:e2e` (verify exact script in `frontend/package.json`) or `bunx playwright test`.
- Manual smoke (no Playwright coverage): WebSocket `/ws/chat` connection, scheduler tick (reminder generation), AI task input (`/api/ai/*`), `/health`.

### Verification Reality

This planning shell does not have `bun`, `pytest`, `docker`, or `az` on PATH for autonomous runs during planning. Plans must:

- Issue the canonical commands.
- For each, allow the executor to document the exact blocker and run the strongest available fallback (e.g., `python -m compileall`, manual node-based check, or recording the failure).
- Treat "executed in CI" or "executed locally with logs captured" as equivalent for fallback purposes per CONTEXT D-11.

### Migration Guide Anchor

CONTEXT D-12 requires three sections in `docs/MIGRATION-V2.1.md`:

1. **Old → new import path table** — covers backend (`app.config` → `app.core.config`, etc.) and frontend (`$lib/api` → `$lib/apis` + `$lib/types`).
2. **Shim ledger** — one row per shim with location, delegate target, owner, removal trigger, baseline grep command, baseline callsite count.
3. **Runtime runbook** — exact commands to start backend (`uvicorn app.api.main:app`), frontend (`bun run dev`, `bun run build`), `docker compose up`, and the Azure-style monolith image build/run.

D-13 places the file at `docs/MIGRATION-V2.1.md` (repo root `docs/`, persists past milestone archival). `README.md` and `backend/CLAUDE.md` get a one-line pointer.

`backend/docs/MIGRATION-GUIDE-20.md` already exists from Phase 20-05 — Phase 22 can reference it but should not duplicate its contents in `docs/MIGRATION-V2.1.md`. The new guide covers the **integrated** v2.1 picture (backend + frontend + runtime + shims).

## Risks and Mitigations

| Risk | Why It Matters | Mitigation |
|------|----------------|------------|
| Uvicorn target update breaks live container | `app.main:app` and `app.api.main:app` resolve to the same FastAPI instance today, but a typo, missed config, or stale image could black-hole the App Service | Update supervisord and `backend/Dockerfile` together; verify `import app.api.main; app.api.main.app` resolves; rebuild and run smoke locally before push |
| Alembic migrations regress | Migration history must remain intact; an env.py path drift would silently no-op autogenerate | Verify `alembic current` and `alembic upgrade head` succeed; confirm `target_metadata` resolves through `app.db.database.Base` and registers all 22 models via `import app.models` |
| Shim deletion attempted in Phase 22 | CONTEXT D-04/D-14 explicitly defers shim removal | Plan tasks must only **inventory** shims and record baselines — no `rm` operations on shim files |
| Smoke check skipped silently | VERIFY-03 requires six flows; AI input and WebSocket are easy to forget | Plan 22-03 lists every flow as its own subtask with a recorded result row in `22-VERIFICATION.md` |
| Migration guide drift from reality | Doc may quote stale commands if commands aren't actually run | Each runbook command in `docs/MIGRATION-V2.1.md` must have been executed (or fallback documented) during Plan 22-02 / 22-03 |
| Adding a new dependency to fix a blocked smoke | Violates RUN-03 | Document any blocked smoke as a fallback per D-11 instead of installing a new package |

## Validation Architecture

### Automated Checks

- `rtk rg "app\.api\.main:app" supervisord.conf backend/Dockerfile` finds canonical target after Plan 22-01.
- `rtk rg "app\.main:app" supervisord.conf backend/Dockerfile Dockerfile` returns no matches outside comments after Plan 22-01.
- `cd backend && python -m pytest -q` exits 0 (VERIFY-01).
- `cd frontend && bun run check` exits 0 with no new errors (VERIFY-02).
- `cd frontend && bun run build` exits 0 (VERIFY-02).
- `cd frontend && bunx playwright test` (or project script) exits 0; HTML report path captured.
- `python -c "from app.api.main import app; print([r.path for r in app.router.routes].count('/health'))"` returns at least 1 from `backend/`.
- `cd backend && alembic current` and `cd backend && alembic check` (or `alembic heads`) succeed.
- `rtk rg "from app\.main|import app\.main|app\.main:app" --glob '!.planning/**' --glob '!backend/app/main.py'` records baseline for shim ledger.
- `test -f docs/MIGRATION-V2.1.md` (VERIFY-04).
- `rtk rg "MIGRATION-V2.1" README.md backend/CLAUDE.md` finds the pointer lines.

### Manual / Focused Smoke (Plan 22-03 records each in `22-VERIFICATION.md`)

- Login: `POST /api/auth/token` with seeded user → 200 + `access_token` cookie.
- Session: `GET /api/auth/me` with cookie → 200 + user payload.
- Task board load: `/tasks` route renders with active sub-team and pulls tasks.
- AI task input: AI breakdown endpoint accepts a prompt and returns sub-tasks.
- WebSocket chat: connect to `ws://.../ws/chat?token=...`, send a message, receive ack.
- Scheduler/notifications: confirm scheduler started in logs and `/api/notifications` polls return current rows.
- Health: `GET /health` → `{"status":"ok"}`.

If a smoke is environment-blocked, record blocker + the next-best fallback that ran (D-11).

## Planner Guidance

- Phase 22 is **runtime + verification + docs**. No source moves except to fix import bugs found during verification.
- Wave plan: Plan 22-01 (entrypoint update) → Plans 22-02 and 22-03 in parallel (verification floor) → Plan 22-04 (migration guide, shim ledger, signoff).
- Every plan must include `<threat_model>` because security enforcement defaults to enabled.
- Do **not** create a UI-SPEC; ROADMAP says `UI hint: no` and CONTEXT forbids visual changes.
- Do **not** schedule shim deletions; CONTEXT defers them.
- Pin `22-VERIFICATION.md` as the single signoff artifact (D-10) and `docs/MIGRATION-V2.1.md` as the persistent guide (D-13).
- All four verification layers (backend pytest, frontend check+build, Playwright, manual smoke) are mandatory; no plan may declare done without all four recorded.
- Use `rtk` prefix for grep/search commands per project AGENTS.md.

## RESEARCH COMPLETE
