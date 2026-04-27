"""add status transitions

Revision ID: d3e4f5a6b7c8
Revises: c2d3e4f5a6b7
Create Date: 2026-04-27 01:55:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "d3e4f5a6b7c8"
down_revision: Union[str, Sequence[str], None] = "c2d3e4f5a6b7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "status_transitions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("status_set_id", sa.Integer(), nullable=False),
        sa.Column("from_status_id", sa.Integer(), nullable=False),
        sa.Column("to_status_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.CheckConstraint(
            "from_status_id != to_status_id",
            name="ck_status_transitions_no_self_transition",
        ),
        sa.ForeignKeyConstraint(
            ["from_status_id"], ["custom_statuses.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["status_set_id"], ["status_sets.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["to_status_id"], ["custom_statuses.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "status_set_id",
            "from_status_id",
            "to_status_id",
            name="uq_status_transitions_status_set_from_to",
        ),
    )
    op.create_index(
        op.f("ix_status_transitions_id"),
        "status_transitions",
        ["id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_status_transitions_status_set_id"),
        "status_transitions",
        ["status_set_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_status_transitions_from_status_id"),
        "status_transitions",
        ["from_status_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_status_transitions_to_status_id"),
        "status_transitions",
        ["to_status_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_status_transitions_to_status_id"),
        table_name="status_transitions",
    )
    op.drop_index(
        op.f("ix_status_transitions_from_status_id"),
        table_name="status_transitions",
    )
    op.drop_index(
        op.f("ix_status_transitions_status_set_id"),
        table_name="status_transitions",
    )
    op.drop_index(op.f("ix_status_transitions_id"), table_name="status_transitions")
    op.drop_table("status_transitions")
