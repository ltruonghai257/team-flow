# 25-01 Summary

## Completed
- Added weekly board persistence models in `backend/app/models/board.py`:
  - `WeeklyPost`
  - `WeeklyPostAppend`
  - `WeeklyBoardSummary`
- Added one-primary-post-per-author-per-week uniqueness:
  - `uq_weekly_posts_author_week`
- Added one-summary-per-subteam-per-week uniqueness:
  - `uq_weekly_board_summary_week`
- Exported board models through aggregate model surface:
  - `backend/app/models/__init__.py`
- Added board schemas in `backend/app/schemas/board.py`:
  - `WeeklyPostCreate`, `WeeklyPostUpdate`
  - `WeeklyPostAppendCreate`, `WeeklyPostAppendUpdate`, `WeeklyPostAppendOut`
  - `WeeklyPostOut`, `WeeklyBoardSummaryOut`
  - `WeeklyBoardWeekOptionOut`, `WeeklyBoardWeekResponse`
- Exported board schemas through aggregate schema surface:
  - `backend/app/schemas/__init__.py`
- Added Alembic migration:
  - `backend/alembic/versions/aa11bb22cc33_add_weekly_board_tables.py`

## Verification
- `rtk python -m compileall backend/app` ✅
- `cd backend && rtk python -c "from app.models import WeeklyPost, WeeklyPostAppend, WeeklyBoardSummary; from app.schemas import WeeklyPostCreate, WeeklyBoardWeekResponse; print('board contracts ok')"` ✅

## Notes
- Weekly board tables, indexes, and constraints are now versioned and importable from app aggregate surfaces.
