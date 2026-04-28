"""add knowledge sessions

Revision ID: e4f5a6b7c8d9
Revises: d3e4f5a6b7c8
Create Date: 2026-04-28 09:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "e4f5a6b7c8d9"
down_revision: Union[str, Sequence[str], None] = "d3e4f5a6b7c8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute(
            "ALTER TYPE notificationeventtype ADD VALUE IF NOT EXISTS 'knowledge_session'"
        )
        # Create enum type using raw SQL if it doesn't exist
        op.execute("""
            DO $$ BEGIN
                CREATE TYPE knowledgesessiontype AS ENUM ('presentation', 'demo', 'workshop', 'qa');
            EXCEPTION
                WHEN duplicate_object THEN null;
            END $$;
        """)
        # Use raw SQL type string to avoid SQLAlchemy enum creation
        session_type_col = sa.Column("session_type", sa.String(), nullable=False)
    else:
        # For SQLite or other databases, use String
        session_type_col = sa.Column("session_type", sa.String(), nullable=False)

    op.create_table(
        "knowledge_sessions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("topic", sa.String(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("references", sa.Text(), nullable=True),
        session_type_col,
        sa.Column("start_time", sa.DateTime(), nullable=False),
        sa.Column("duration_minutes", sa.Integer(), nullable=False),
        sa.Column("tags", sa.String(), nullable=True),
        sa.Column("presenter_id", sa.Integer(), nullable=False),
        sa.Column("sub_team_id", sa.Integer(), nullable=True),
        sa.Column("created_by_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["created_by_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["presenter_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["sub_team_id"], ["sub_teams.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    # Alter column to use enum type for PostgreSQL
    if bind.dialect.name == "postgresql":
        op.execute("""
            ALTER TABLE knowledge_sessions 
            ALTER COLUMN session_type TYPE knowledgesessiontype 
            USING session_type::knowledgesessiontype
        """)
    op.create_index(op.f("ix_knowledge_sessions_id"), "knowledge_sessions", ["id"], unique=False)
    op.create_index(
        op.f("ix_knowledge_sessions_start_time"),
        "knowledge_sessions",
        ["start_time"],
        unique=False,
    )
    op.create_index(
        op.f("ix_knowledge_sessions_presenter_id"),
        "knowledge_sessions",
        ["presenter_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_knowledge_sessions_sub_team_id"),
        "knowledge_sessions",
        ["sub_team_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_knowledge_sessions_created_by_id"),
        "knowledge_sessions",
        ["created_by_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_knowledge_sessions_created_by_id"), table_name="knowledge_sessions")
    op.drop_index(op.f("ix_knowledge_sessions_sub_team_id"), table_name="knowledge_sessions")
    op.drop_index(op.f("ix_knowledge_sessions_presenter_id"), table_name="knowledge_sessions")
    op.drop_index(op.f("ix_knowledge_sessions_start_time"), table_name="knowledge_sessions")
    op.drop_index(op.f("ix_knowledge_sessions_id"), table_name="knowledge_sessions")
    op.drop_table("knowledge_sessions")
