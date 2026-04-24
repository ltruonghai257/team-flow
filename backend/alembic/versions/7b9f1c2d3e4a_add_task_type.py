"""add task type

Revision ID: 7b9f1c2d3e4a
Revises: 649c85543ce6
Create Date: 2026-04-24 09:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "7b9f1c2d3e4a"
down_revision: Union[str, Sequence[str], None] = "649c85543ce6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


tasktype = sa.Enum("feature", "bug", "task", "improvement", name="tasktype")


def upgrade() -> None:
    bind = op.get_bind()
    tasktype.create(bind, checkfirst=True)
    op.add_column("tasks", sa.Column("type", tasktype, nullable=False, server_default="task"))


def downgrade() -> None:
    op.drop_column("tasks", "type")
    bind = op.get_bind()
    tasktype.drop(bind, checkfirst=True)
