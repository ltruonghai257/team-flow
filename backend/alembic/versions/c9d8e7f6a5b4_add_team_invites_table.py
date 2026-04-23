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

invitestatus_enum = sa.Enum('pending', 'accepted', 'expired', 'cancelled', name='invitestatus')


def upgrade() -> None:
    invitestatus_enum.create(op.get_bind(), checkfirst=True)
    op.create_table(
        'team_invites',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('role', sa.Enum('admin', 'supervisor', 'member', name='userrole'), nullable=True),
        sa.Column('token', sa.String(), nullable=False),
        sa.Column('validation_code', sa.String(), nullable=False),
        sa.Column('status', sa.Enum('pending', 'accepted', 'expired', 'cancelled', name='invitestatus'), nullable=True),
        sa.Column('invited_by_id', sa.Integer(), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('accepted_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['invited_by_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_team_invites_id'), 'team_invites', ['id'], unique=False)
    op.create_index(op.f('ix_team_invites_email'), 'team_invites', ['email'], unique=False)
    op.create_index(op.f('ix_team_invites_token'), 'team_invites', ['token'], unique=True)
    op.create_index(op.f('ix_team_invites_status'), 'team_invites', ['status'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_team_invites_status'), table_name='team_invites')
    op.drop_index(op.f('ix_team_invites_token'), table_name='team_invites')
    op.drop_index(op.f('ix_team_invites_email'), table_name='team_invites')
    op.drop_index(op.f('ix_team_invites_id'), table_name='team_invites')
    op.drop_table('team_invites')
    invitestatus_enum.drop(op.get_bind(), checkfirst=True)
