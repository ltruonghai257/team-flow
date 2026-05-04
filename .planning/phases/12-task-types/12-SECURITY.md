---
phase: 12
slug: task-types
status: verified
threats_open: 0
asvs_level: 1
created: 2026-04-24
---

# Phase 12 — Security

> Per-phase security contract: threat register, accepted risks, and audit trail.

---

## Trust Boundaries

| Boundary | Description | Data Crossing |
|----------|-------------|---------------|
| Browser to API | Task create/edit/filter requests pass user-selected task type values to FastAPI. | Task metadata, including type filters and task payload fields. |
| AI output to API/UI | AI parse and breakdown responses may include task type suggestions from model output. | Untrusted model-generated JSON fields. |
| Database migration | Existing task rows receive the new non-null task type column during Alembic upgrade. | Persisted task records and schema enum values. |

---

## Threat Register

| Threat ID | Category | Component | Disposition | Mitigation | Status |
|-----------|----------|-----------|-------------|------------|--------|
| T-12-01 | Tampering | Task create/update and AI parse/breakdown | mitigate | `TaskType` enum is enforced in Pydantic schemas; AI parse only copies valid values; AI breakdown defaults missing/invalid type to `task`. Evidence: `backend/app/schemas.py`, `backend/app/routers/tasks.py`. | closed |
| T-12-02 | Availability / Integrity | Alembic migration for existing tasks | mitigate | Migration creates fixed `tasktype` enum and adds `tasks.type` as `nullable=False` with `server_default="task"`, preventing null existing rows. Evidence: `backend/alembic/versions/7b9f1c2d3e4a_add_task_type.py`. | closed |
| T-12-03 | Tampering / Injection | Task list type filter | mitigate | `types` query param is split and converted through `TaskType(raw_type)` before `Task.type.in_(...)`; invalid values return `HTTPException(status_code=422)`. Evidence: `backend/app/routers/tasks.py`. | closed |

---

## Accepted Risks Log

No accepted risks.

---

## Security Audit Trail

| Audit Date | Threats Total | Closed | Open | Run By |
|------------|---------------|--------|------|--------|
| 2026-04-24 | 3 | 3 | 0 | Codex |

---

## Sign-Off

- [x] All threats have a disposition (mitigate / accept / transfer)
- [x] Accepted risks documented in Accepted Risks Log
- [x] `threats_open: 0` confirmed
- [x] `status: verified` set in frontmatter

**Approval:** verified 2026-04-24
