"""add weekly board tables

Revision ID: aa11bb22cc33
Revises: c2d3e4f5a6b7
Create Date: 2026-04-28 09:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "aa11bb22cc33"
down_revision: Union[str, Sequence[str], None] = "c2d3e4f5a6b7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "weekly_posts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("author_id", sa.Integer(), nullable=False),
        sa.Column("sub_team_id", sa.Integer(), nullable=False),
        sa.Column("iso_year", sa.Integer(), nullable=False),
        sa.Column("iso_week", sa.Integer(), nullable=False),
        sa.Column("week_start_date", sa.Date(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["author_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["sub_team_id"], ["sub_teams.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("author_id", "iso_year", "iso_week", name="uq_weekly_posts_author_week"),
    )
    op.create_index(op.f("ix_weekly_posts_id"), "weekly_posts", ["id"], unique=False)
    op.create_index(op.f("ix_weekly_posts_author_id"), "weekly_posts", ["author_id"], unique=False)
    op.create_index(op.f("ix_weekly_posts_sub_team_id"), "weekly_posts", ["sub_team_id"], unique=False)
    op.create_index(op.f("ix_weekly_posts_iso_year"), "weekly_posts", ["iso_year"], unique=False)
    op.create_index(op.f("ix_weekly_posts_iso_week"), "weekly_posts", ["iso_week"], unique=False)
    op.create_index(op.f("ix_weekly_posts_week_start_date"), "weekly_posts", ["week_start_date"], unique=False)

    op.create_table(
        "weekly_post_appends",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("post_id", sa.Integer(), nullable=False),
        sa.Column("author_id", sa.Integer(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["author_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["post_id"], ["weekly_posts.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_weekly_post_appends_id"), "weekly_post_appends", ["id"], unique=False)
    op.create_index(op.f("ix_weekly_post_appends_post_id"), "weekly_post_appends", ["post_id"], unique=False)
    op.create_index(op.f("ix_weekly_post_appends_author_id"), "weekly_post_appends", ["author_id"], unique=False)

    op.create_table(
        "weekly_board_summaries",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("sub_team_id", sa.Integer(), nullable=False),
        sa.Column("iso_year", sa.Integer(), nullable=False),
        sa.Column("iso_week", sa.Integer(), nullable=False),
        sa.Column("week_start_date", sa.Date(), nullable=False),
        sa.Column("summary_text", sa.Text(), nullable=False),
        sa.Column("source_post_count", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("generated_by_mode", sa.String(), nullable=False, server_default="manual"),
        sa.Column("generated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["sub_team_id"], ["sub_teams.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("sub_team_id", "iso_year", "iso_week", name="uq_weekly_board_summary_week"),
    )
    op.create_index(op.f("ix_weekly_board_summaries_id"), "weekly_board_summaries", ["id"], unique=False)
    op.create_index(op.f("ix_weekly_board_summaries_sub_team_id"), "weekly_board_summaries", ["sub_team_id"], unique=False)
    op.create_index(op.f("ix_weekly_board_summaries_iso_year"), "weekly_board_summaries", ["iso_year"], unique=False)
    op.create_index(op.f("ix_weekly_board_summaries_iso_week"), "weekly_board_summaries", ["iso_week"], unique=False)
    op.create_index(op.f("ix_weekly_board_summaries_generated_at"), "weekly_board_summaries", ["generated_at"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_weekly_board_summaries_generated_at"), table_name="weekly_board_summaries")
    op.drop_index(op.f("ix_weekly_board_summaries_iso_week"), table_name="weekly_board_summaries")
    op.drop_index(op.f("ix_weekly_board_summaries_iso_year"), table_name="weekly_board_summaries")
    op.drop_index(op.f("ix_weekly_board_summaries_sub_team_id"), table_name="weekly_board_summaries")
    op.drop_index(op.f("ix_weekly_board_summaries_id"), table_name="weekly_board_summaries")
    op.drop_table("weekly_board_summaries")

    op.drop_index(op.f("ix_weekly_post_appends_author_id"), table_name="weekly_post_appends")
    op.drop_index(op.f("ix_weekly_post_appends_post_id"), table_name="weekly_post_appends")
    op.drop_index(op.f("ix_weekly_post_appends_id"), table_name="weekly_post_appends")
    op.drop_table("weekly_post_appends")

    op.drop_index(op.f("ix_weekly_posts_week_start_date"), table_name="weekly_posts")
    op.drop_index(op.f("ix_weekly_posts_iso_week"), table_name="weekly_posts")
    op.drop_index(op.f("ix_weekly_posts_iso_year"), table_name="weekly_posts")
    op.drop_index(op.f("ix_weekly_posts_sub_team_id"), table_name="weekly_posts")
    op.drop_index(op.f("ix_weekly_posts_author_id"), table_name="weekly_posts")
    op.drop_index(op.f("ix_weekly_posts_id"), table_name="weekly_posts")
    op.drop_table("weekly_posts")
