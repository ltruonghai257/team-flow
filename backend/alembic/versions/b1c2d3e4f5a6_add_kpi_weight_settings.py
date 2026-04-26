"""add kpi weight settings

Revision ID: b1c2d3e4f5a6
Revises: 8a1b2c3d4e5f
Create Date: 2026-04-26 15:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b1c2d3e4f5a6"
down_revision: Union[str, Sequence[str], None] = "8a1b2c3d4e5f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "kpi_weight_settings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("sub_team_id", sa.Integer(), nullable=True),
        sa.Column("workload_weight", sa.Integer(), nullable=False, server_default="20"),
        sa.Column("velocity_weight", sa.Integer(), nullable=False, server_default="25"),
        sa.Column("cycle_time_weight", sa.Integer(), nullable=False, server_default="20"),
        sa.Column("on_time_weight", sa.Integer(), nullable=False, server_default="20"),
        sa.Column("defect_weight", sa.Integer(), nullable=False, server_default="15"),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["sub_team_id"], ["sub_teams.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("sub_team_id"),
    )
    op.create_index("ix_kpi_weight_settings_id", "kpi_weight_settings", ["id"], unique=False)
    op.create_index("ix_kpi_weight_settings_sub_team_id", "kpi_weight_settings", ["sub_team_id"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_kpi_weight_settings_sub_team_id", table_name="kpi_weight_settings")
    op.drop_index("ix_kpi_weight_settings_id", table_name="kpi_weight_settings")
    op.drop_table("kpi_weight_settings")
