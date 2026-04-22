"""Add role enum

Revision ID: a1b2c3d4e5f6
Revises: fb50c0295f56
Create Date: 2026-04-22 23:45:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = 'fb50c0295f56'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

userrole_enum = sa.Enum('admin', 'supervisor', 'member', name='userrole')


def upgrade() -> None:
    userrole_enum.create(op.get_bind(), checkfirst=True)
    op.execute("ALTER TABLE users ALTER COLUMN role TYPE userrole USING role::userrole")
    op.execute("ALTER TABLE users ALTER COLUMN role SET DEFAULT 'member'::userrole")


def downgrade() -> None:
    op.execute("ALTER TABLE users ALTER COLUMN role TYPE VARCHAR USING role::VARCHAR")
    op.execute("ALTER TABLE users ALTER COLUMN role SET DEFAULT 'member'")
    userrole_enum.drop(op.get_bind(), checkfirst=True)
