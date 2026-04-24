"""merge sub_team and task_type migrations

Revision ID: f836fa8d42c6
Revises: 22cabf0392b8, 7b9f1c2d3e4a
Create Date: 2026-04-24 18:26:10.469177

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f836fa8d42c6'
down_revision: Union[str, Sequence[str], None] = ('22cabf0392b8', '7b9f1c2d3e4a')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
