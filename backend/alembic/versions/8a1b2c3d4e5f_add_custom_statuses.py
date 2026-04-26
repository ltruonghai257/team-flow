"""add custom statuses

Revision ID: 8a1b2c3d4e5f
Revises: 6ff5de88b5d6
Create Date: 2026-04-26 07:25:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "8a1b2c3d4e5f"
down_revision: Union[str, Sequence[str], None] = "6ff5de88b5d6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


status_set_scope = sa.Enum(
    "sub_team_default", "project", name="statussetscope", create_type=False
)
task_status = sa.Enum(
    "todo", "in_progress", "review", "done", "blocked", name="taskstatus", create_type=False
)


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    
    # Check if enum types already exist, create them if not
    existing_types = [t['name'] for t in inspector.get_enums()]
    if "statussetscope" not in existing_types:
        sa.Enum(
            "sub_team_default", "project", name="statussetscope"
        ).create(bind, checkfirst=True)
    if "taskstatus" not in existing_types:
        sa.Enum(
            "todo", "in_progress", "review", "done", "blocked", name="taskstatus"
        ).create(bind, checkfirst=True)

    # Check if status_sets table already exists
    tables = inspector.get_table_names()
    
    if "status_sets" not in tables:
        op.create_table("status_sets",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("scope", status_set_scope, nullable=False),
        sa.Column("sub_team_id", sa.Integer(), nullable=True),
        sa.Column("project_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"]),
        sa.ForeignKeyConstraint(["sub_team_id"], ["sub_teams.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
        op.create_index(op.f("ix_status_sets_id"), "status_sets", ["id"], unique=False)
        op.create_index(
            op.f("ix_status_sets_scope"), "status_sets", ["scope"], unique=False
        )
        op.create_index(
            op.f("ix_status_sets_sub_team_id"),
            "status_sets",
            ["sub_team_id"],
            unique=False,
        )
        op.create_index(
            op.f("ix_status_sets_project_id"),
            "status_sets",
            ["project_id"],
            unique=False,
        )

    if "custom_statuses" not in tables:
        op.create_table("custom_statuses",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("status_set_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("slug", sa.String(), nullable=False),
        sa.Column("color", sa.String(), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("is_done", sa.Boolean(), nullable=False),
        sa.Column("is_archived", sa.Boolean(), nullable=False),
        sa.Column("legacy_status", task_status, nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["status_set_id"], ["status_sets.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
        op.create_index(
            op.f("ix_custom_statuses_id"), "custom_statuses", ["id"], unique=False
        )
        op.create_index(
            op.f("ix_custom_statuses_status_set_id"),
            "custom_statuses",
            ["status_set_id"],
            unique=False,
        )
        op.create_index(
            op.f("ix_custom_statuses_slug"), "custom_statuses", ["slug"], unique=False
        )
        op.create_index(
            op.f("ix_custom_statuses_is_done"),
            "custom_statuses",
            ["is_done"],
            unique=False,
        )
        op.create_index(
            op.f("ix_custom_statuses_is_archived"),
            "custom_statuses",
            ["is_archived"],
            unique=False,
        )
        op.create_index(
            op.f("ix_custom_statuses_legacy_status"),
            "custom_statuses",
            ["legacy_status"],
            unique=False,
        )

    # Check if custom_status_id column already exists in tasks table
    tasks_columns = [col['name'] for col in inspector.get_columns('tasks')]
    if "custom_status_id" not in tasks_columns:
        op.add_column("tasks", sa.Column("custom_status_id", sa.Integer(), nullable=True))
        op.create_index(
            op.f("ix_tasks_custom_status_id"),
            "tasks",
            ["custom_status_id"],
            unique=False,
        )
        op.create_foreign_key(
            "fk_tasks_custom_status_id",
            "tasks",
            "custom_statuses",
            ["custom_status_id"],
            ["id"],
        )

    # Only run data seeding if tables were just created
    if "status_sets" not in tables:
        op.execute(
            sa.text(
                """
                INSERT INTO status_sets (scope, sub_team_id, project_id, created_at, updated_at)
                SELECT 'sub_team_default', sub_teams.id, NULL, NOW(), NOW()
                FROM sub_teams
                """
            )
        )
        op.execute(
            sa.text(
                """
                INSERT INTO status_sets (scope, sub_team_id, project_id, created_at, updated_at)
                VALUES ('sub_team_default', NULL, NULL, NOW(), NOW())
                """
            )
        )
        op.execute(
            sa.text(
                """
                INSERT INTO custom_statuses (
                    status_set_id, name, slug, color, position, is_done, is_archived,
                    legacy_status, created_at, updated_at
                )
                SELECT
                    status_sets.id, defaults.name, defaults.slug, defaults.color,
                    defaults.position, defaults.is_done, false, defaults.legacy_status,
                    NOW(), NOW()
                FROM status_sets
                CROSS JOIN (
                    VALUES
                        ('To Do', 'todo', '#64748b', 0, false, 'todo'),
                        ('In Progress', 'in_progress', '#0ea5e9', 1, false, 'in_progress'),
                        ('Review', 'review', '#f59e0b', 2, false, 'review'),
                        ('Done', 'done', '#10b981', 3, true, 'done'),
                        ('Blocked', 'blocked', '#f43f5e', 4, false, 'blocked')
                ) AS defaults(name, slug, color, position, is_done, legacy_status)
                WHERE status_sets.scope = 'sub_team_default'
                """
            )
        )
        op.execute(
            sa.text(
                """
                WITH task_status_sets AS (
                    SELECT
                        tasks.id AS task_id,
                        COALESCE(team_status_sets.id, fallback_status_sets.id) AS status_set_id,
                        tasks.status AS legacy_status
                    FROM tasks
                    LEFT JOIN projects ON projects.id = tasks.project_id
                    LEFT JOIN status_sets AS team_status_sets
                        ON team_status_sets.scope = 'sub_team_default'
                        AND team_status_sets.sub_team_id = projects.sub_team_id
                    JOIN status_sets AS fallback_status_sets
                        ON fallback_status_sets.scope = 'sub_team_default'
                        AND fallback_status_sets.sub_team_id IS NULL
                )
                UPDATE tasks
                SET custom_status_id = custom_statuses.id
                FROM task_status_sets
                JOIN custom_statuses
                    ON custom_statuses.status_set_id = task_status_sets.status_set_id
                    AND custom_statuses.legacy_status = task_status_sets.legacy_status
                WHERE tasks.id = task_status_sets.task_id
                """
            )
        )


def downgrade() -> None:
    op.drop_constraint("fk_tasks_custom_status_id", "tasks", type_="foreignkey")
    op.drop_index(op.f("ix_tasks_custom_status_id"), table_name="tasks")
    op.drop_column("tasks", "custom_status_id")

    op.drop_index(op.f("ix_custom_statuses_legacy_status"), table_name="custom_statuses")
    op.drop_index(op.f("ix_custom_statuses_is_archived"), table_name="custom_statuses")
    op.drop_index(op.f("ix_custom_statuses_is_done"), table_name="custom_statuses")
    op.drop_index(op.f("ix_custom_statuses_slug"), table_name="custom_statuses")
    op.drop_index(op.f("ix_custom_statuses_status_set_id"), table_name="custom_statuses")
    op.drop_index(op.f("ix_custom_statuses_id"), table_name="custom_statuses")
    op.drop_table("custom_statuses")

    op.drop_index(op.f("ix_status_sets_project_id"), table_name="status_sets")
    op.drop_index(op.f("ix_status_sets_sub_team_id"), table_name="status_sets")
    op.drop_index(op.f("ix_status_sets_scope"), table_name="status_sets")
    op.drop_index(op.f("ix_status_sets_id"), table_name="status_sets")
    op.drop_table("status_sets")

    bind = op.get_bind()
    status_set_scope.drop(bind, checkfirst=True)
