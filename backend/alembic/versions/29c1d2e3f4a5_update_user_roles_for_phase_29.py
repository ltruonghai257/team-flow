"""update_user_roles_for_phase_29

Revision ID: 29c1d2e3f4a5
Revises: 76d2b3f4f184
Create Date: 2026-04-29 15:27:39.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "29c1d2e3f4a5"
down_revision: Union[str, Sequence[str], None] = "76d2b3f4f184"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

old_userrole = sa.Enum("admin", "supervisor", "member", name="userrole")
new_userrole = sa.Enum(
    "manager",
    "supervisor",
    "assistant_manager",
    "member",
    name="userrole",
)


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name != "postgresql":
        return

    op.execute("ALTER TYPE userrole RENAME TO userrole_old")
    new_userrole.create(bind, checkfirst=False)
    op.execute("ALTER TABLE users ALTER COLUMN role DROP DEFAULT")
    op.execute("ALTER TABLE team_invites ALTER COLUMN role DROP DEFAULT")
    op.execute(
        """
        ALTER TABLE users
        ALTER COLUMN role TYPE userrole
        USING (
            CASE role::text
                WHEN 'admin' THEN 'manager'
                ELSE role::text
            END
        )::userrole
        """
    )
    op.execute(
        """
        ALTER TABLE team_invites
        ALTER COLUMN role TYPE userrole
        USING (
            CASE role::text
                WHEN 'admin' THEN 'manager'
                ELSE role::text
            END
        )::userrole
        """
    )
    op.execute("ALTER TABLE users ALTER COLUMN role SET DEFAULT 'member'::userrole")
    op.execute("ALTER TABLE team_invites ALTER COLUMN role SET DEFAULT 'member'::userrole")
    op.execute("DROP TYPE userrole_old")


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name != "postgresql":
        return

    op.execute("ALTER TYPE userrole RENAME TO userrole_new")
    old_userrole.create(bind, checkfirst=False)
    op.execute("ALTER TABLE users ALTER COLUMN role DROP DEFAULT")
    op.execute("ALTER TABLE team_invites ALTER COLUMN role DROP DEFAULT")
    op.execute(
        """
        ALTER TABLE users
        ALTER COLUMN role TYPE userrole
        USING (
            CASE role::text
                WHEN 'manager' THEN 'admin'
                WHEN 'assistant_manager' THEN 'supervisor'
                ELSE role::text
            END
        )::userrole
        """
    )
    op.execute(
        """
        ALTER TABLE team_invites
        ALTER COLUMN role TYPE userrole
        USING (
            CASE role::text
                WHEN 'manager' THEN 'admin'
                WHEN 'assistant_manager' THEN 'supervisor'
                ELSE role::text
            END
        )::userrole
        """
    )
    op.execute("ALTER TABLE users ALTER COLUMN role SET DEFAULT 'member'::userrole")
    op.execute("ALTER TABLE team_invites ALTER COLUMN role SET DEFAULT 'member'::userrole")
    sa.Enum(
        "manager",
        "supervisor",
        "assistant_manager",
        "member",
        name="userrole_new",
    ).drop(bind, checkfirst=False)
