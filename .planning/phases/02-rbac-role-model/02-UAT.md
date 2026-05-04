---
status: testing
phase: 02-rbac-role-model
source: [01-SUMMARY.md, 02-SUMMARY.md]
started: "2026-04-22T23:55:00.000Z"
updated: "2026-04-22T23:55:00.000Z"
---

## Current Test

number: 1
name: Cold Start Smoke Test
expected: |
  Kill any running backend server. Start it fresh (docker-compose up or uvicorn directly).
  The server should boot without errors — no import errors, no alembic failures, no startup crashes.
  A basic API call (e.g. GET /api/users/ with a valid token, or GET /docs) returns a live response.
awaiting: user response

## Tests

### 1. Cold Start Smoke Test
expected: Kill any running backend server. Start it fresh (docker-compose up or uvicorn directly). The server should boot without errors — no import errors, no alembic failures, no startup crashes. A basic API call (e.g. GET /api/users/ with a valid token, or GET /docs) returns a live response.
result: [pending]

### 2. Role Promotion API — Admin can promote a user
expected: |
  As an admin, send PATCH /api/users/{user_id}/role with body {"role": "supervisor"}.
  The response is 200 with the updated user showing "role": "supervisor".

result: [pending]

### 3. Role Promotion API — Non-admin is blocked (403)
expected: |
  As a member or supervisor, send PATCH /api/users/{user_id}/role.
  The response is 403 Forbidden with detail "Admin access required".

result: [pending]

### 4. require_supervisor blocks member access
expected: |
  Any endpoint protected by require_supervisor (e.g. the performance dashboard endpoint when built,
  or by direct API test) returns 403 when called by a user with role "member".
  A supervisor or admin can call the same endpoint successfully.

result: [pending]

### 5. Team page — Role badges visible
expected: |
  Navigate to /team in the browser.
  Users with role "admin" show a blue badge labelled "Admin".
  Users with role "supervisor" show a purple badge labelled "Supervisor".
  Users with role "member" show a gray "member" badge.

result: [pending]

### 6. Route guard — Member redirected from /performance
expected: |
  While logged in as a member, navigate to /performance in the browser.
  The app immediately redirects to / (dashboard).
  A supervisor or admin visiting /performance is NOT redirected.

result: [pending]

### 7. create_admin.py — Script runs without errors
expected: |
  From backend/, run: python -m app.scripts.create_admin --help  (or set env vars and run it).
  The script launches without syntax errors or import crashes.
  If run with valid env vars (ADMIN_EMAIL, ADMIN_USERNAME, ADMIN_FULL_NAME, ADMIN_PASSWORD),
  it creates or promotes a user to admin and prints a confirmation message.

result: [pending]

## Summary

total: 7
passed: 0
issues: 0
pending: 7
skipped: 0

## Gaps

[none yet]
