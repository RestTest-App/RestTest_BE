"""merge heads

Revision ID: edeb78e94e98
Revises: 4e97dd8fe7e3, dae93c3d042e
Create Date: 2025-06-16 12:46:26.517344

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'edeb78e94e98'
down_revision: Union[str, None] = ('4e97dd8fe7e3', 'dae93c3d042e')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
