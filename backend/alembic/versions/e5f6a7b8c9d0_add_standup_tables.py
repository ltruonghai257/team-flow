"""add standup tables

Revision ID: e5f6a7b8c9d0
Revises: d3e4f5a6b7c8
Create Date: 2026-04-28 12:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

revision: str = "e5f6a7b8c9d0"
down_revision: Union[str, Sequence[str], None] = "d3e4f5a6b7c8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # standup_settings — single-row global default template
    op.create_table(
        "standup_settings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("default_fields", JSONB(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_standup_settings_id"), "standup_settings", ["id"], unique=False)

    # standup_templates — one row per sub-team (optional override)
    op.create_table(
        "standup_templates",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("sub_team_id", sa.Integer(), nullable=False),
        sa.Column("fields", JSONB(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["sub_team_id"], ["sub_teams.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("sub_team_id"),
    )
    op.create_index(op.f("ix_standup_templates_id"), "standup_templates", ["id"], unique=False)
    op.create_index(op.f("ix_standup_templates_sub_team_id"), "standup_templates", ["sub_team_id"], unique=False)

    # standup_posts — the main feed table
    op.create_table(
        "standup_posts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("author_id", sa.Integer(), nullable=False),
        sa.Column("sub_team_id", sa.Integer(), nullable=False),
        sa.Column("field_values", JSONB(), nullable=False),
        sa.Column("task_snapshot", JSONB(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["author_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["sub_team_id"], ["sub_teams.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_standup_posts_id"), "standup_posts", ["id"], unique=False)
    op.create_index(op.f("ix_standup_posts_author_id"), "standup_posts", ["author_id"], unique=False)
    op.create_index(op.f("ix_standup_posts_sub_team_id"), "standup_posts", ["sub_team_id"], unique=False)
    op.create_index(op.f("ix_standup_posts_created_at"), "standup_posts", ["created_at"], unique=False)

    # Seed global default template — 6 fields per D-01 / UPD-02
    op.execute(
        sa.text(
            "INSERT INTO standup_settings (default_fields, updated_at) "
            "VALUES (CAST(:fields AS jsonb), NOW()) "
            "ON CONFLICT DO NOTHING"
        ).bindparams(
            fields='["Pending Tasks","Future Tasks","Blockers","Need Help From","Critical Timeline","Release Date"]'
        )
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_standup_posts_created_at"), table_name="standup_posts")
    op.drop_index(op.f("ix_standup_posts_sub_team_id"), table_name="standup_posts")
    op.drop_index(op.f("ix_standup_posts_author_id"), table_name="standup_posts")
    op.drop_index(op.f("ix_standup_posts_id"), table_name="standup_posts")
    op.drop_table("standup_posts")

    op.drop_index(op.f("ix_standup_templates_sub_team_id"), table_name="standup_templates")
    op.drop_index(op.f("ix_standup_templates_id"), table_name="standup_templates")
    op.drop_table("standup_templates")

    op.drop_index(op.f("ix_standup_settings_id"), table_name="standup_settings")
    op.drop_table("standup_settings")
