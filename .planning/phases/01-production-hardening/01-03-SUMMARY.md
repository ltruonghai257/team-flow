# Plan 01-03 Summary: Replace datetime.utcnow()

**Status:** Complete  
**Completed:** 2026-04-22

## What Was Built

Replaced all `datetime.utcnow()` calls with `datetime.now(timezone.utc).replace(tzinfo=None)` across 8 files:

- `backend/app/models.py` — all 14 Column `default`/`onupdate` lambdas
- `backend/app/auth.py` — `create_access_token` expiry calculation
- `backend/app/routers/tasks.py` — `completed_at`, `updated_at` assignments + AI parse date prompt
- `backend/app/routers/dashboard.py` — `now` variable
- `backend/app/routers/notifications.py` — status comparison + `now` variable in bulk create
- `backend/app/routers/websocket.py` — presence tracking, heartbeat response, DM `last_message_at`
- `backend/app/routers/ai.py` — `quick_chat` return timestamp
- `backend/app/scheduler_jobs.py` — due notification query filter

## Pattern Used

```python
datetime.now(timezone.utc).replace(tzinfo=None)
```

Preserves naive UTC timestamps in DB — no schema migration needed (D-10 from CONTEXT.md).

## Verification

- `grep -r "utcnow" backend/app/ --include="*.py"` → no results ✓
