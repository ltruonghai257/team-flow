# Plan 16-06 Summary: KPI Warning Email + Real Seed Data

## Status: Complete

## What was added

### KPI Warning Email (supervisor-only)
- **Backend** `POST /api/performance/kpi/warning-email` — supervisor can send a warning email to any member in their sub-team with a Fair (60–79) or At Risk (<60) KPI score. Endpoint validates score band, checks sub-team membership, and sends HTML email via `fastapi_mail`.
- **Schemas** `KPIWarningEmailRequest`, `KPIWarningEmailResponse` added to `app/schemas.py`.
- **Email service** `send_kpi_warning_email` + `_build_kpi_warning_html` added to `app/email_service.py` — two distinct email templates (friendly for Fair, serious for At Risk).
- **Frontend** `KpiWarnButton.svelte` — warn button with confirmation modal and optional custom message, shown on Fair/At Risk scorecards in supervisor view only.
- **Frontend** `sendKpiWarningEmail` API method added to `frontend/src/lib/api.ts`.

### Real Seed Data (replaces all fake/demo fallback)
- **Sub-team** "Engineering Team" created; supervisor and all 5 members assigned.
- **StatusSet + CustomStatuses** (To Do / In Progress / In Review / Done[is_done=True] / Blocked) — KPI endpoints now resolve `is_done` correctly.
- **Projects** scoped to sub-team (`sub_team_id`) so KPI sub-team filter works.
- **KPI-targeted tasks** per member producing realistic score distribution (verified via live API):

| Member | Score | Band |
|---|---|---|
| Alice Chen | 93 | 🟢 Good |
| La Truong Hai | 74 | 🟡 Fair |
| Carol Davis | 68 | 🟡 Fair |
| Bob Kim | 67 | 🟡 Fair |
| Doan Duc Kien | 36 | 🔴 At Risk |

- **UI** — removed `DEMO_OVERVIEW` fallback constant and `isDemo` state from `/performance`; page now shows real data only or "No overview data available" when empty.

## Verification Results

### Compile & Type Checks
- `python -m compileall app -q` → exit 0 ✅
- `bun run check` → 4 pre-existing errors (login/milestones/register), 0 new ✅

### Live API (backend running, seeded DB)
- `GET /api/performance/kpi/overview` → 5 scorecards with correct scores ✅
- `POST /api/performance/kpi/warning-email` for Doan Duc Kien (At Risk) → `{"sent":true,"level":"at_risk","recipient_email":"doanduckien.2001@gmail.com"}` ✅
- All 8 KPI routes present: weights(×2), warning-email, overview, sprint, quality, members, drilldown ✅

## Commits
- `8d8d60f` feat(demo): add latruonghai and doanduckien as Fair-score members in seed and demo scorecards
- `41cae31` fix(demo): set Doan Duc Kien to At Risk (48) and add to needs_attention
- `049a82f` refactor(seed+ui): real data only — SubTeam/StatusSet/KPI tasks; remove DEMO_OVERVIEW fallback
