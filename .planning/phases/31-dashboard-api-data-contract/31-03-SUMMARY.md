# Plan 31-03 Summary: Extend Dashboard Tests

## Objective
Extend backend/tests/test_dashboard.py with pytest async tests covering all D-16 scenarios: role-conditional payload shape for member and supervisor roles, field presence validation, my_tasks urgency sort, and recent_activity scoping.

## Tasks Completed

### Task 1: Replace test_dashboard.py with D-16 role-conditional and shape tests
- Replaced entire file content with 5 new tests following the pattern from test_visibility.py
- Added helper function `_make_user` to create users inline with `db.add` + `await db.flush()`
- Added helper function `_token` using `create_access_token({"sub": str(user.id)})` pattern
- **Test 1 - test_member_dashboard_shape:** Creates member_user, asserts my_tasks and recent_activity present, team_health and kpi_summary keys absent (not null)
- **Test 2 - test_supervisor_dashboard_shape:** Creates supervisor_user, asserts all 4 keys present with correct shape, kpi_summary has avg_score, completion_rate, needs_attention_count
- **Test 3 - test_my_tasks_urgency_sort:** Creates overdue task (due_date = now - 1 day) and upcoming task (due_date = now + 3 days), asserts first item has is_overdue: true
- **Test 4 - test_my_tasks_excludes_done:** Creates active task and done task, asserts my_tasks has length 1 (only active task)
- **Test 5 - test_recent_activity_shape:** Creates StandupPost with field_values and task_snapshot, asserts activity item has all required fields and author_name matches
- All tests use `@pytest.mark.asyncio` decorator
- All tests have `db_session: AsyncSession` and `async_client: AsyncClient` fixtures
- All tests commit with `await db_session.commit()` before HTTP requests
- StandupPost uses JSON columns (field_values dict, task_snapshot list) - works in SQLite for tests

## Deviations
- Fixed missing `timezone` import in services/kpi.py discovered during test run
- Added `response_model_exclude_none=True` to dashboard route decorator to ensure team_health and kpi_summary keys are absent (not null) for member role - Pydantic's ConfigDict exclude alone wasn't sufficient for FastAPI response serialization

## Key Files Created/Modified
- **Modified:** `backend/app/services/kpi.py` (added timezone import)
- **Modified:** `backend/app/routers/dashboard.py` (added response_model_exclude_none=True)
- **Modified:** `backend/tests/test_dashboard.py` (removed 12 lines, added 221 lines - complete replacement)

## Self-Check: PASSED
- `cd backend && rtk uv run pytest tests/test_dashboard.py -v` exits 0
- 5 tests present and all pass
- `test_member_dashboard_shape` asserts `"team_health" not in data`
- `test_supervisor_dashboard_shape` asserts `"team_health" in data` and `"kpi_summary" in data`
- `test_my_tasks_urgency_sort` asserts first item has `is_overdue: true`
- `test_my_tasks_excludes_done` asserts done task is excluded
