"""Add team_invites table

Revision ID: c9d8e7f6a5b4
Revises: a1b2c3d4e5f6
Create Date: 2026-04-23 23:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c9d8e7f6a5b4'
down_revision: Union[str, Sequence[str], None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.execute(sa.text("""
        DO $$ BEGIN
            CREATE TYPE userrole AS ENUM ('admin', 'supervisor', 'member');
        EXCEPTION WHEN duplicate_object THEN null;
        END $$
    """))
    op.execute(sa.text("""
        DO $$ BEGIN
            CREATE TYPE invitestatus AS ENUM ('pending', 'accepted', 'expired', 'cancelled');
        EXCEPTION WHEN duplicate_object THEN null;
        END $$
    """))
    op.execute(sa.text("""
        CREATE TABLE IF NOT EXISTS team_invites (
            id          SERIAL PRIMARY KEY,
            email       VARCHAR NOT NULL,
            role        userrole DEFAULT 'member',
            token       VARCHAR NOT NULL UNIQUE,
            validation_code VARCHAR NOT NULL,
            status      invitestatus DEFAULT 'pending',
            invited_by_id INTEGER NOT NULL REFERENCES users(id),
            expires_at  TIMESTAMP NOT NULL,
            accepted_at TIMESTAMP,
            created_at  TIMESTAMP
        )
    """))
    op.execute(sa.text("CREATE INDEX IF NOT EXISTS ix_team_invites_id ON team_invites (id)"))
    op.execute(sa.text("CREATE INDEX IF NOT EXISTS ix_team_invites_email ON team_invites (email)"))
    op.execute(sa.text("CREATE UNIQUE INDEX IF NOT EXISTS ix_team_invites_token ON team_invites (token)"))
    op.execute(sa.text("CREATE INDEX IF NOT EXISTS ix_team_invites_status ON team_invites (status)"))


def downgrade() -> None:
    op.drop_index(op.f('ix_team_invites_status'), table_name='team_invites')
    op.drop_index(op.f('ix_team_invites_token'), table_name='team_invites')
    op.drop_index(op.f('ix_team_invites_email'), table_name='team_invites')
    op.drop_index(op.f('ix_team_invites_id'), table_name='team_invites')
    op.drop_table('team_invites')
    op.execute("DROP TYPE IF EXISTS invitestatus")
