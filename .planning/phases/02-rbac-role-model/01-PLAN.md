---
wave: 1
depends_on: []
requirements: [REQ-07]

files_modified:
  - backend/app/models.py
  - backend/app/auth.py
  - backend/app/routers/users.py
  - backend/app/routers/dashboard.py
  - backend/app/schemas.py
  - backend/app/scripts/create_admin.py
autonomous: true
---

# Phase 2 - Backend RBAC & Role Model

## Objective
Formalize the role system server-side using a SQLAlchemy Enum for `User.role`, create the initial admin setup script, and implement FastAPI dependencies for RBAC (Role-Based Access Control).

## Requirements Addressed
- REQ-07 (Role-Based Access Control Clarification)

## Tasks

```xml
<task>
  <description>Update User model with SQLAlchemy Enum for roles</description>
  <read_first>
    - backend/app/models.py
  </read_first>
  <action>
    Add a Python Enum `UserRole` with values `admin`, `supervisor`, `member`.
    Update the `role` column in the `User` class to use `sqlalchemy.Enum(UserRole)` instead of `String`.
    Default the role to `UserRole.member`.
    Run alembic to generate the migration: `alembic revision --autogenerate -m "Add role enum"`.
  </action>
  <acceptance_criteria>
    `backend/app/models.py` contains `class UserRole(str, enum.Enum):`
    `User` model `role` column uses `Enum(UserRole)`.
    An alembic migration file is generated and successfully runs via `alembic upgrade head`.
  </acceptance_criteria>
</task>

<task>
  <description>Implement FastAPI RBAC dependencies</description>
  <read_first>
    - backend/app/auth.py
    - backend/app/models.py
  </read_first>
  <action>
    In `backend/app/auth.py`, create `require_supervisor` and `require_admin` dependencies.
    `require_supervisor` should depend on `get_current_user` and raise a 403 HTTPException if `current_user.role` is not `admin` or `supervisor`.
    `require_admin` should depend on `get_current_user` and raise a 403 HTTPException if `current_user.role` is not `admin`.
  </action>
  <acceptance_criteria>
    `backend/app/auth.py` contains `def require_supervisor(`
    `backend/app/auth.py` contains `def require_admin(`
    Both dependencies return the current user if the role condition is met.
  </acceptance_criteria>
</task>

<task>
  <description>Add User Role Promotion API</description>
  <read_first>
    - backend/app/schemas.py
    - backend/app/routers/users.py
    - backend/app/auth.py
  </read_first>
  <action>
    In `backend/app/schemas.py`, create a `UserRoleUpdate` Pydantic model with a `role` field.
    In `backend/app/routers/users.py`, add a `PATCH /api/users/{user_id}/role` endpoint.
    The endpoint must depend on `require_admin`.
    It should update the target user's role in the database and return the updated user.
  </action>
  <acceptance_criteria>
    `backend/app/schemas.py` contains `class UserRoleUpdate(BaseModel):`
    `backend/app/routers/users.py` contains `@router.patch("/{user_id}/role"`
    The endpoint uses `current_user: User = Depends(require_admin)`.
  </acceptance_criteria>
</task>

<task>
  <description>Create initial admin CLI script</description>
  <read_first>
    - backend/app/models.py
    - backend/app/database.py
    - backend/app/auth.py
  </read_first>
  <action>
    Create a new file `backend/app/scripts/create_admin.py`.
    The script should accept email, username, full_name, and password via environment variables or prompt.
    It initializes the async DB session, hashes the password using `get_password_hash` from `auth.py`, and creates a user with `role=UserRole.admin`.
    If the user already exists, it should just promote them to admin.
  </action>
  <acceptance_criteria>
    `backend/app/scripts/create_admin.py` exists.
    The script uses the async DB session to insert/update a user with `role=UserRole.admin`.
    Running `python -m app.scripts.create_admin --help` (or similar) runs without syntax errors.
  </acceptance_criteria>
</task>

<task autonomous="false">
  <description>[BLOCKING] Database Migration Schema Push</description>
  <read_first>
    - backend/alembic/env.py
  </read_first>
  <action>
    Run the alembic migration command to update the live database with the newly created Enum.
    `alembic upgrade head`
  </action>
  <acceptance_criteria>
    The migration successfully completes and updates the database schema.
    PostgreSQL reports the enum `userrole` exists.
  </acceptance_criteria>
</task>
```

## Verification
- Run the `create_admin.py` script to create an admin user successfully.
- Test the `PATCH /api/users/{id}/role` endpoint as an admin (success) and as a member (403 Forbidden).
- Ensure `require_supervisor` blocks member access.
## Must Haves
- [ ] `User.role` enum values formally defined: `admin`, `supervisor`, `member`
- [ ] Backend middleware enforces role checks
- [ ] Role change by admin only

