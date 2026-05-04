---
phase: 14-sprint-model
reviewed: 2026-04-26T07:25:57Z
depth: standard
files_reviewed: 2
files_reviewed_list:
  - backend/alembic/versions/6ff5de88b5d6_add_sprint_model.py
  - backend/app/models.py
findings:
  critical: 2
  warning: 0
  info: 0
  total: 2
status: issues_found
---

# Phase 14: Code Review Report

**Reviewed:** 2026-04-26T07:25:57Z
**Depth:** standard
**Files Reviewed:** 2
**Status:** issues_found

## Summary

Reviewed the sprint model and migration at standard depth. The model additions are internally consistent, but the Alembic downgrade path is not reliable: the tasks-to-sprints foreign key is created without a stable name and then dropped with `None`, and the PostgreSQL enum type created for sprint status is left behind after downgrade.

## Critical Issues

### CR-01: Unnamed Sprint Foreign Key Cannot Be Reliably Dropped

**File:** `backend/alembic/versions/6ff5de88b5d6_add_sprint_model.py:37`
**Issue:** The migration creates the `tasks.sprint_id` foreign key with `op.create_foreign_key(None, ...)`, then attempts to drop it with `op.drop_constraint(None, ...)` on line 44. On PostgreSQL, the database assigns an implementation-specific constraint name, and Alembic cannot reliably emit a downgrade for a constraint named `None`. This can break rollback of this migration.
**Fix:**
```python
op.create_foreign_key(
    "fk_tasks_sprint_id",
    "tasks",
    "sprints",
    ["sprint_id"],
    ["id"],
)

# downgrade
op.drop_constraint("fk_tasks_sprint_id", "tasks", type_="foreignkey")
```

### CR-02: Downgrade Leaves `sprintstatus` Enum Type Behind

**File:** `backend/alembic/versions/6ff5de88b5d6_add_sprint_model.py:47`
**Issue:** The `sprints.status` column creates the PostgreSQL enum type `sprintstatus`, but the downgrade only drops the table and never drops the enum type. After downgrading, the schema still contains `sprintstatus`; a later re-upgrade can fail when the migration tries to create the same enum type again.
**Fix:**
```python
sprintstatus = sa.Enum("planned", "active", "closed", name="sprintstatus")

def upgrade() -> None:
    bind = op.get_bind()
    sprintstatus.create(bind, checkfirst=True)
    op.create_table(
        "sprints",
        # ...
        sa.Column("status", sprintstatus, nullable=True),
        # ...
    )

def downgrade() -> None:
    op.drop_constraint("fk_tasks_sprint_id", "tasks", type_="foreignkey")
    op.drop_column("tasks", "sprint_id")
    op.drop_index(op.f("ix_sprints_id"), table_name="sprints")
    op.drop_table("sprints")
    sprintstatus.drop(op.get_bind(), checkfirst=True)
```

---

_Reviewed: 2026-04-26T07:25:57Z_
_Reviewer: the agent (gsd-code-reviewer)_
_Depth: standard_
