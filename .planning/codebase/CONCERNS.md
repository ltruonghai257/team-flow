# Codebase Concerns

**Analysis Date:** 2026-04-28

## Tech Debt

**Backend Package Restructure:**
- Issue: Ongoing migration of monolithic `models.py`, `schemas.py`, and massive routers to a modular package structure. Redundant modules exist (e.g., `app/models.py` alongside `app/models/` and `app/schemas.py` alongside `app/schemas/`).
- Files: `backend/app/models.py`, `backend/app/schemas.py`, `backend/app/routers/performance.py`
- Impact: Context fragmentation, cognitive load, and risk of importing from the legacy monolithic files instead of the new modular ones.
- Fix approach: Complete the backend package restructure phase, fully migrating all legacy models/schemas to the domain-driven directories (`app/models/`, `app/schemas/`) and deleting the monolithic files.

**Frontend Type Safety Loss (`any` overuse):**
- Issue: Heavy use of `any` types throughout SvelteKit page routes for API responses and component state, bypassing TypeScript validation for core domain objects (Projects, Tasks, KPIs).
- Files: `frontend/src/routes/performance/+page.svelte`, `frontend/src/routes/timeline/+page.svelte`, `frontend/src/routes/team/+page.svelte`
- Impact: Brittle UI components that are prone to runtime errors if API contracts change or are misunderstood by the developer.
- Fix approach: Export strong TypeScript interfaces from API client modules and strictly type all `$state` declarations. Remove `// eslint-disable-next-line @typescript-eslint/no-explicit-any` from `frontend/src/lib/apis/request.ts` if possible.

**Massive Monolithic Svelte Components:**
- Issue: Complex page routes attempting to manage global state, API fetching, deeply nested local state, and complex UI rendering all in one file.
- Files: `frontend/src/routes/tasks/+page.svelte` (>1100 lines), `frontend/src/routes/team/+page.svelte` (>800 lines)
- Impact: Hard to maintain, difficult to test, and high risk of regression on UI changes.
- Fix approach: Break down massive pages into smaller feature components in `lib/components/` and extract state logic into Svelte 5 runes (`$state` / `$derived`) in separate `.svelte.ts` context files.

## Known Bugs

**Not detected:**
- Symptoms: N/A
- Files: N/A
- Trigger: N/A
- Workaround: N/A

## Security Considerations

**Hardcoded Secrets in Source / Test Defaults:**
- Risk: Exposing default test credentials or database passwords. The config currently defaults to `postgres:password@localhost`.
- Files: `backend/app/core/config.py`, `backend/app/scripts/seed_demo.py`, `backend/app/scripts/create_admin.py`
- Current mitigation: Environment variables are supported, but defaults are insecure.
- Recommendations: Ensure `.env.example` handles safe defaults and avoid committing explicit passwords even in seed scripts (use environment variables exclusively).

## Performance Bottlenecks

**Sequential API Fetches in Performance Dashboard:**
- Problem: The performance dashboard kicks off multiple API requests (`kpiSprint`, `kpiQuality`, `kpiMembers`) heavily utilizing the backend.
- Files: `frontend/src/routes/performance/+page.svelte`
- Cause: Unoptimized fetch requests in the frontend and potentially heavy synchronous processing or missing indexes on the backend.
- Improvement path: Introduce caching on the backend to avoid re-computing complex metrics on every page load. Ensure database queries for KPIs are optimized.

**Backend Router Bloat:**
- Problem: `routers/performance.py` and other routers contain complex logic and large payloads.
- Files: `backend/app/routers/performance.py`, `backend/app/routers/statuses.py`, `backend/app/routers/tasks.py`
- Cause: Missing service layer for heavy data aggregation.
- Improvement path: Extract complex database querying and data shaping into dedicated service classes in `app/services/` (as part of the backend restructure).

## Fragile Areas

**Frontend Data Consistency:**
- Files: `frontend/src/routes/timeline/+page.svelte`, `frontend/src/routes/tasks/+page.svelte`
- Why fragile: Data updates (like changing a task's status) manually patch the local client state arrays instead of using a robust normalized store or refetching optimally.
- Safe modification: Carefully trace state mutations when updating task attributes to ensure all UI views update properly.
- Test coverage: Requires end-to-end or integration tests to ensure optimistic UI updates match backend reality.

## Scaling Limits

**Rate Limiting Storage:**
- Current capacity: Single-instance only (in-memory).
- Limit: Will fail or be inconsistent if the backend scales horizontally across multiple pods or workers.
- Scaling path: Follow the `TODO` in `backend/app/core/limiter.py` to upgrade to Redis-backed storage for multi-instance deployments.

## Dependencies at Risk

**Not detected:**
- Risk: N/A
- Impact: N/A
- Migration plan: N/A

## Missing Critical Features

**Not detected:**
- Problem: N/A
- Blocks: N/A

## Test Coverage Gaps

**Unit and Integration testing for massive UI components:**
- What's not tested: Complex state interactions and conditional rendering in the main tasks and timeline pages.
- Files: `frontend/src/routes/tasks/+page.svelte`, `frontend/src/routes/timeline/+page.svelte`
- Risk: High risk of subtle UI bugs during refactoring of these large components.
- Priority: High

---

*Concerns audit: 2026-04-28*
