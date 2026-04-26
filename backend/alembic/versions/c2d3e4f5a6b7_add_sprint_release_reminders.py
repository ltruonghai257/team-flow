"""add sprint release reminders

Revision ID: c2d3e4f5a6b7
Revises: b1c2d3e4f5a6
Create Date: 2026-04-26 18:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c2d3e4f5a6b7"
down_revision: Union[str, Sequence[str], None] = "b1c2d3e4f5a6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


notification_event_type = sa.Enum(
    "schedule",
    "task",
    "sprint_end",
    "milestone_due",
    "reminder_settings_proposal",
    name="notificationeventtype",
    create_type=False,
)
reminder_proposal_status = sa.Enum(
    "pending",
    "approved",
    "rejected",
    name="reminderproposalstatus",
    create_type=False,
)


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute(
            "ALTER TYPE notificationeventtype ADD VALUE IF NOT EXISTS 'sprint_end'"
        )
        op.execute(
            "ALTER TYPE notificationeventtype ADD VALUE IF NOT EXISTS 'milestone_due'"
        )
        op.execute(
            "ALTER TYPE notificationeventtype ADD VALUE IF NOT EXISTS 'reminder_settings_proposal'"
        )
        reminder_proposal_status.create(bind, checkfirst=True)

    op.create_table(
        "sub_team_reminder_settings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("sub_team_id", sa.Integer(), nullable=False),
        sa.Column(
            "lead_time_days",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("2"),
        ),
        sa.Column(
            "sprint_reminders_enabled",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true"),
        ),
        sa.Column(
            "milestone_reminders_enabled",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true"),
        ),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["sub_team_id"], ["sub_teams.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("sub_team_id"),
    )
    op.create_index(
        op.f("ix_sub_team_reminder_settings_id"),
        "sub_team_reminder_settings",
        ["id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_sub_team_reminder_settings_sub_team_id"),
        "sub_team_reminder_settings",
        ["sub_team_id"],
        unique=True,
    )

    op.create_table(
        "reminder_settings_proposals",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("sub_team_id", sa.Integer(), nullable=False),
        sa.Column("proposed_by_id", sa.Integer(), nullable=False),
        sa.Column("reviewed_by_id", sa.Integer(), nullable=True),
        sa.Column("lead_time_days", sa.Integer(), nullable=True),
        sa.Column("sprint_reminders_enabled", sa.Boolean(), nullable=True),
        sa.Column("milestone_reminders_enabled", sa.Boolean(), nullable=True),
        sa.Column(
            "status",
            reminder_proposal_status,
            nullable=False,
            server_default=sa.text("'pending'"),
        ),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["proposed_by_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["reviewed_by_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["sub_team_id"], ["sub_teams.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_reminder_settings_proposals_id"),
        "reminder_settings_proposals",
        ["id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_reminder_settings_proposals_sub_team_id"),
        "reminder_settings_proposals",
        ["sub_team_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_reminder_settings_proposals_status"),
        "reminder_settings_proposals",
        ["status"],
        unique=False,
    )

    op.create_index(
        "ix_event_notifications_generated_pending_unique",
        "event_notifications",
        ["event_type", "event_ref_id", "user_id"],
        unique=True,
        postgresql_where=sa.text(
            "event_type IN ('sprint_end', 'milestone_due') AND status = 'pending'"
        ),
    )


def downgrade() -> None:
    # PostgreSQL enum value removal is intentionally omitted; dropping the tables
    # and partial index is sufficient for safe rollback in this project.
    op.drop_index(
        "ix_event_notifications_generated_pending_unique",
        table_name="event_notifications",
    )

    op.drop_index(
        op.f("ix_reminder_settings_proposals_status"),
        table_name="reminder_settings_proposals",
    )
    op.drop_index(
        op.f("ix_reminder_settings_proposals_sub_team_id"),
        table_name="reminder_settings_proposals",
    )
    op.drop_index(
        op.f("ix_reminder_settings_proposals_id"),
        table_name="reminder_settings_proposals",
    )
    op.drop_table("reminder_settings_proposals")

    op.drop_index(
        op.f("ix_sub_team_reminder_settings_sub_team_id"),
        table_name="sub_team_reminder_settings",
    )
    op.drop_index(
        op.f("ix_sub_team_reminder_settings_id"),
        table_name="sub_team_reminder_settings",
    )
    op.drop_table("sub_team_reminder_settings")
