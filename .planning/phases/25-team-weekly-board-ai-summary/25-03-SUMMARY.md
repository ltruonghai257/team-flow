# 25-03 Summary

## Completed
- Extended weekly board service for summary generation:
  - `generate_weekly_board_summary`
  - `get_summary_cooldown`
  - `upsert_weekly_board_summary`
- Implemented empty-week short-circuit summary:
  - `"No updates this week"`
- Implemented cooldown behavior for manual summary requests:
  - cached summary reused inside cooldown window
- Added summary endpoint:
  - `POST /api/board/week/summary`
- Added scheduler integration in:
  - `backend/app/internal/scheduler_jobs.py`
  - weekly job at Sunday 23:00 to generate board summaries using shared service logic.

## Verification
- `rtk proxy /Users/haila/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m pytest tests/test_board.py -q` (run from `backend/`) ✅

## Notes
- Manual and scheduled summary paths share the same service-layer generation/upsert logic.
