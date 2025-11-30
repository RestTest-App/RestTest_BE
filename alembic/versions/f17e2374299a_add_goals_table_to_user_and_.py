"""add goals_table to user and explanations to question

Revision ID: f17e2374299a
Revises: edeb78e94e98
Create Date: 2025-11-12 20:31:36.410704

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f17e2374299a'
down_revision: Union[str, None] = 'edeb78e94e98'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add goal_table to user table (using JSON to store array of goal numbers)
    op.add_column(
        'user',
        sa.Column(
            'goal_table',
            sa.JSON(),
            nullable=True,
            comment="목표 테이블"
        )
    )

    # Add explanations to question table
    op.add_column(
        'question',
        sa.Column(
            'explanations',
            sa.Text(),
            nullable=True,
            comment="전체 해설"
        )
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Remove goal_table from user table
    op.drop_column('user', 'goal_table')

    # Remove explanations from question table
    op.drop_column('question', 'explanations')
