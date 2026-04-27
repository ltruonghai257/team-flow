# v2.1 Migration Guide: Open WebUI-Inspired Project Structure

**Status:** Complete — milestone v2.1 closed 2026-04-27
**Phases covered:** 19 (refactor map), 20 (backend restructure), 21 (frontend restructure), 22 (runtime + regression verification)
**Roadmap:** `.planning/ROADMAP.md`
**Backend-only path map:** [`backend/docs/MIGRATION-GUIDE-20.md`](../backend/docs/MIGRATION-GUIDE-20.md)

This guide covers the **integrated** v2.1 picture: backend package moves, frontend module reorganisation, runtime entrypoint updates, shim inventory, and the verified runbook. It is the single reference for contributors onboarding after v2.1.

---

## Old to New Import Paths

### Backend (Python)

| Old import | New canonical import | Notes |
|------------|---------------------|-------|
| `from app.main import app` | `from app.api.main import app` | High-risk shim at `backend/app/main.py`; deferred cleanup |
| `from app.config import settings` | `from app.core.config import settings` | Low-risk shim |
| `from app.database import ...` | `from app.db.database import ...` | Low-risk shim |
| `from app.limiter import limiter` | `from app.core.limiter import limiter` | Low-risk shim |
| `from app.auth import ...` | `from app.utils.auth import ...` | Low-risk shim |
| `from app.ai_client import ...` | `from app.utils.ai_client import ...` | Low-risk shim |
| `from app.email_service import ...` | `from app.utils.email_service import ...` | Low-risk shim |
| `from app.scheduler_jobs import ...` | `from app.internal.scheduler_jobs import ...` | Low-risk shim |
| `from app.websocket.manager import ...` | `from app.socket.manager import ...` | Low-risk shim |
| `from app.models import <Model>` | `from app.models import <Model>` (package) | `app/models/__init__.py` re-exports all models; import path unchanged, but source is now the package aggregate |
| `from app.schemas import <Schema>` | `from app.schemas import <Schema>` (package) | `app/schemas/__init__.py` re-exports all schemas; same shape |
| `import app.main` (uvicorn target `app.main:app`) | `app.api.main:app` | Runtime configs updated in Phase 22-01 |

### Frontend (TypeScript)

| Old import | New canonical import | Notes |
|------------|---------------------|-------|
| `$lib/api` (API call functions) | `$lib/apis` | Phase 21 moved API calls to `$lib/apis/` directory |
| `$lib/api` (status types) | `$lib/types/status` | Types extracted to `$lib/types/` in Phase 21 |
| `$lib/api` (reminder / notification types) | `$lib/types/notification` | Types extracted to `$lib/types/` in Phase 21 |
| `$lib/api` (barrel re-exports) | `$lib/types` | Aggregate type barrel at `$lib/types/index.ts` |
| `$lib/api.ts` (module file) | deleted | Phase 21-04 deleted `frontend/src/lib/api.ts`; no shim remains |

---

## Shim Ledger

Phase 22 records the **baseline callsite count** for every live backend shim. The future cleanup milestone uses these grep commands as the removal trigger: when the count drops to zero (excluding `.planning/phases/`), the shim can be deleted safely.

No shim is removed in this milestone. See CONTEXT D-04/D-05/D-14.

| Shim | Location | Delegate Target | Risk | Removal Trigger | Baseline Grep | Baseline callsite count |
|------|----------|-----------------|------|-----------------|---------------|------------------------|
| `app.main` | `backend/app/main.py` | `app.api.main` | HIGH | All runtime entrypoints reference `app.api.main:app` AND `rtk rg "from app\.main import\|import app\.main\|app\.main:app" --glob '!.planning/phases/**' --glob '!backend/app/main.py'` count is zero; verified by Plan 22-01 | `rtk rg "from app\.main import\|import app\.main\|app\.main:app" --glob '!.planning/phases/**' --glob '!backend/app/main.py' -l` | 4 files (README.md, backend/docs/MIGRATION-GUIDE-20.md, backend/tests/test_package_structure.py, backend/tests/conftest.py) |
| `app.config` | `backend/app/config.py` | `app.core.config` | LOW | `rtk rg "from app\.config import\|import app\.config" --glob '!.planning/phases/**' --glob '!backend/app/config.py'` count is zero | `rtk rg "from app\.config import\|import app\.config" --glob '!.planning/phases/**' --glob '!backend/app/config.py' -l` | 2 files (backend/docs/MIGRATION-GUIDE-20.md, backend/tests/test_package_structure.py) |
| `app.database` | `backend/app/database.py` | `app.db.database` | LOW | `rtk rg "from app\.database import\|import app\.database" --glob '!.planning/phases/**' --glob '!backend/app/database.py'` count is zero | `rtk rg "from app\.database import\|import app\.database" --glob '!.planning/phases/**' --glob '!backend/app/database.py' -l` | 4 files (backend/tests/test_package_structure.py, backend/app/models.py, backend/app/scripts/create_admin.py, backend/app/scripts/seed_demo.py) |
| `app.limiter` | `backend/app/limiter.py` | `app.core.limiter` | LOW | `rtk rg "from app\.limiter import\|import app\.limiter" --glob '!.planning/phases/**' --glob '!backend/app/limiter.py'` count is zero | `rtk rg "from app\.limiter import\|import app\.limiter" --glob '!.planning/phases/**' --glob '!backend/app/limiter.py' -l` | 0 files |
| `app.auth` | `backend/app/auth.py` | `app.utils.auth` | LOW | `rtk rg "from app\.auth import\|import app\.auth" --glob '!.planning/phases/**' --glob '!backend/app/auth.py'` count is zero | `rtk rg "from app\.auth import\|import app\.auth" --glob '!.planning/phases/**' --glob '!backend/app/auth.py' -l` | 2 files (backend/app/scripts/seed_demo.py, backend/app/scripts/create_admin.py) |
| `app.ai_client` | `backend/app/ai_client.py` | `app.utils.ai_client` | LOW | `rtk rg "from app\.ai_client import\|import app\.ai_client" --glob '!.planning/phases/**' --glob '!backend/app/ai_client.py'` count is zero | `rtk rg "from app\.ai_client import\|import app\.ai_client" --glob '!.planning/phases/**' --glob '!backend/app/ai_client.py' -l` | 0 files |
| `app.email_service` | `backend/app/email_service.py` | `app.utils.email_service` | LOW | `rtk rg "from app\.email_service import\|import app\.email_service" --glob '!.planning/phases/**' --glob '!backend/app/email_service.py'` count is zero | `rtk rg "from app\.email_service import\|import app\.email_service" --glob '!.planning/phases/**' --glob '!backend/app/email_service.py' -l` | 0 files |
| `app.scheduler_jobs` | `backend/app/scheduler_jobs.py` | `app.internal.scheduler_jobs` | LOW | `rtk rg "from app\.scheduler_jobs import\|import app\.scheduler_jobs" --glob '!.planning/phases/**' --glob '!backend/app/scheduler_jobs.py'` count is zero | `rtk rg "from app\.scheduler_jobs import\|import app\.scheduler_jobs" --glob '!.planning/phases/**' --glob '!backend/app/scheduler_jobs.py' -l` | 1 file (backend/tests/test_package_structure.py) |
| `app.websocket.manager` | `backend/app/websocket/manager.py` | `app.socket.manager` | LOW | `rtk rg "from app\.websocket\.manager import\|import app\.websocket\.manager" --glob '!.planning/phases/**' --glob '!backend/app/websocket/manager.py'` count is zero | `rtk rg "from app\.websocket\.manager import\|import app\.websocket\.manager" --glob '!.planning/phases/**' --glob '!backend/app/websocket/manager.py' -l` | 3 files (backend/docs/MIGRATION-GUIDE-20.md, backend/tests/test_package_structure.py, backend/app/routers/websocket.py) |
| `app.models` (module shim) | `backend/app/models.py` | `app.models/` package `__init__` | MEDIUM | `from app.models import` callers naturally resolve through the package; shim can be removed when confirmed no direct `app.models` module-level attribute access bypasses the package | `rtk rg "from app\.models import" --glob '!.planning/phases/**' --glob '!backend/app/models/__init__.py' -l` | 31 files (all routers, services, tests, scripts — see grep output) |
| `app.schemas` (module shim) | `backend/app/schemas.py` | `app.schemas/` package `__init__` | MEDIUM | Same as `app.models` — resolves through package aggregate; shim removal safe when no bypass found | `rtk rg "from app\.schemas import" --glob '!.planning/phases/**' --glob '!backend/app/schemas/__init__.py' -l` | 19 files (all routers, utils, tests — see grep output) |
| `frontend/src/lib/api.ts` | deleted in Phase 21-04 | `$lib/apis`, `$lib/types` | n/a | REMOVED in Phase 21-04; baseline count = 0 | n/a | 0 |

---

## Runtime Runbook

All commands verified during Phase 22 verification floor (evidence: `.planning/phases/22-runtime-integration-regression-verification/22-VERIFICATION.md`).

### Backend (local dev)

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.api.main:app --host 127.0.0.1 --port 8000 --reload
```

> **Note:** `app.main:app` still works during the v2.1 milestone via the Phase 20 delegate at `backend/app/main.py`, but it is deprecated. New deployments and runbooks should reference `app.api.main:app` exclusively.

### Frontend (local dev)

```bash
cd frontend
bun install
bun run dev       # → http://localhost:5173
bun run check     # type-check (0 errors at v2.1 close)
bun run build     # production static build → frontend/build/ (adapter-static, 200.html SPA fallback)
bunx playwright test   # E2E suite (mobile-chrome project)
```

### Docker compose (local stack)

```bash
docker compose up --build
```

`docker-compose.yml` builds `backend/Dockerfile` (CMD: `uvicorn app.api.main:app --host 0.0.0.0 --port 8000`) and exposes backend on `:8000` and frontend on `:3000`. PostgreSQL on `:5432`.

### Monolith image (Azure App Service)

```bash
# Provision (one time)
export DB_ADMIN_PASS="<secure>"
./scripts/setup-azure.sh

# Build + deploy
./scripts/deploy.sh
```

The monolith image runs `supervisord` which starts nginx + `uvicorn app.api.main:app` (port 8000 internal, 80 external via nginx). App Service `WEBSITES_PORT=80`.

### Persistent environment / config notes

- `app.core.config.settings` is the canonical settings object; `app.config` import remains a delegate.
- No new environment variables were introduced by the v2.1 milestone.
- Alembic `env.py` loads canonical metadata (`from app.db.database import Base`, `import app.models`); existing migration history is unchanged.
- `RUN_MIGRATIONS=true` still triggers `alembic upgrade head` in the lifespan (via `app.api.main` startup).

### Evidence

Verification floor evidence: `.planning/phases/22-runtime-integration-regression-verification/22-VERIFICATION.md`.
