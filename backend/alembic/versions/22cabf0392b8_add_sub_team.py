"""Add sub_teams table and sub_team_id columns

Revision ID: 22cabf0392b8
Revises: c9d8e7f6a5b4
Create Date: 2026-04-24 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '22cabf0392b8'
down_revision: Union[str, Sequence[str], None] = 'c9d8e7f6a5b4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create sub_teams table
    op.execute(sa.text("""
        CREATE TABLE sub_teams (
            id SERIAL PRIMARY KEY,
            name VARCHAR NOT NULL,
            supervisor_id INTEGER REFERENCES users(id),
            created_at TIMESTAMP
        )
    """))
    op.execute(sa.text("CREATE INDEX ix_sub_teams_id ON sub_teams (id)"))

    # Add nullable sub_team_id columns
    op.execute(sa.text("ALTER TABLE users ADD COLUMN sub_team_id INTEGER REFERENCES sub_teams(id)"))
    op.execute(sa.text("ALTER TABLE projects ADD COLUMN sub_team_id INTEGER REFERENCES sub_teams(id)"))
    op.execute(sa.text("ALTER TABLE team_invites ADD COLUMN sub_team_id INTEGER REFERENCES sub_teams(id)"))

    # Insert default sub-team
    op.execute(sa.text("""
        INSERT INTO sub_teams (name, supervisor_id, created_at)
        VALUES ('Default Team', NULL, NOW())
    """))

    # Get default sub-team ID and backfill existing data
    op.execute(sa.text("""
        UPDATE users SET sub_team_id = (SELECT id FROM sub_teams WHERE name = 'Default Team' LIMIT 1)
        WHERE sub_team_id IS NULL
    """))
    op.execute(sa.text("""
        UPDATE projects SET sub_team_id = (SELECT id FROM sub_teams WHERE name = 'Default Team' LIMIT 1)
        WHERE sub_team_id IS NULL
    """))
    op.execute(sa.text("""
        UPDATE team_invites SET sub_team_id = (SELECT id FROM sub_teams WHERE name = 'Default Team' LIMIT 1)
        WHERE sub_team_id IS NULL
    """))

    # Create FK constraints with explicit names
    op.execute(sa.text("""
        ALTER TABLE users ADD CONSTRAINT fk_users_sub_team
        FOREIGN KEY (sub_team_id) REFERENCES sub_teams(id)
    """))
    op.execute(sa.text("""
        ALTER TABLE projects ADD CONSTRAINT fk_projects_sub_team
        FOREIGN KEY (sub_team_id) REFERENCES sub_teams(id)
    """))
    op.execute(sa.text("""
        ALTER TABLE team_invites ADD CONSTRAINT fk_invites_sub_team
        FOREIGN KEY (sub_team_id) REFERENCES sub_teams(id)
    """))


def downgrade() -> None:
    # Drop FK constraints
    op.execute(sa.text("ALTER TABLE team_invites DROP CONSTRAINT IF EXISTS fk_invites_sub_team"))
    op.execute(sa.text("ALTER TABLE projects DROP CONSTRAINT IF EXISTS fk_projects_sub_team"))
    op.execute(sa.text("ALTER TABLE users DROP CONSTRAINT IF EXISTS fk_users_sub_team"))

    # Drop sub_team_id columns
    op.execute(sa.text("ALTER TABLE team_invites DROP COLUMN IF EXISTS sub_team_id"))
    op.execute(sa.text("ALTER TABLE projects DROP COLUMN IF EXISTS sub_team_id"))
    op.execute(sa.text("ALTER TABLE users DROP COLUMN IF EXISTS sub_team_id"))

    # Drop sub_teams table
    op.execute(sa.text("DROP INDEX IF EXISTS ix_sub_teams_id"))
    op.execute(sa.text("DROP TABLE IF EXISTS sub_teams"))
