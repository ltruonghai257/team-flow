"""merge multiple heads

Revision ID: 76d2b3f4f184
Revises: 45e64e666da7, aa11bb22cc33, e4f5a6b7c8d9
Create Date: 2026-04-28 15:26:20.878798

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '76d2b3f4f184'
down_revision: Union[str, Sequence[str], None] = ('45e64e666da7', 'aa11bb22cc33', 'e4f5a6b7c8d9')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
