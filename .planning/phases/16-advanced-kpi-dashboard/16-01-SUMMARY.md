# Plan 16-01 Summary: Backend Persistence & KPI Contracts

## Status: Complete

## What Was Built

- **`KPIWeightSettings` model** added to `backend/app/models.py` — persists per-sub-team KPI weights with defaults summing to 100.
- **14 KPI schemas** added to `backend/app/schemas.py`: `KPIWeightSettingsOut`, `KPIWeightSettingsUpdate`, `KPIFilterOptions`, `KPIReason`, `KPIScoreBreakdown`, `KPIMemberScorecard`, `KPIChartPoint`, `KPIChartSeries`, `KPIOverviewResponse`, `KPISprintResponse`, `KPIQualityResponse`, `KPIMembersResponse`, `KPIDrilldownTask`, `KPIDrilldownResponse`.
- **Alembic migration** `b1c2d3e4f5a6_add_kpi_weight_settings.py` — creates `kpi_weight_settings` table, applied successfully.
- **Weight endpoints** added to `backend/app/routers/performance.py`:
  - `GET /api/performance/kpi/weights`
  - `PATCH /api/performance/kpi/weights`
  - `_get_or_create_kpi_weights` helper.

## Verification

- Prerequisites confirmed: `Sprint`, `sprint_id`, `custom_status_id`, `is_done` all exist in `models.py`.
- `alembic upgrade head` → exit 0.
- `python -m compileall backend/app` → exit 0.

## Commit

`aa80801` feat(16-01): add KPIWeightSettings model, KPI schemas, weight endpoints, and migration
