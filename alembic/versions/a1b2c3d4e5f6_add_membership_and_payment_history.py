"""add membership and payment_history

Revision ID: a1b2c3d4e5f6
Revises: f17e2374299a
Create Date: 2025-11-30 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = 'f17e2374299a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add membership_tier to user table
    op.add_column(
        'user',
        sa.Column(
            'membership_tier',
            sa.String(20),
            nullable=False,
            server_default='FREE',
            comment="멤버십 등급 (FREE, PREMIUM)"
        )
    )

    # Add subscription_expire_date to user table
    op.add_column(
        'user',
        sa.Column(
            'subscription_expire_date',
            sa.DateTime(),
            nullable=True,
            comment="구독 만료일"
        )
    )

    # Create payment_history table
    op.create_table(
        'payment_history',
        sa.Column('id', sa.BigInteger(), nullable=False, comment="결제 이력 고유 식별값"),
        sa.Column('user_id', sa.BigInteger(), nullable=False, comment="사용자 ID"),
        sa.Column('membership_tier', sa.String(20), nullable=False, comment="구매한 멤버십 등급"),
        sa.Column('payment_amount', sa.Integer(), nullable=False, comment="결제 금액 (원)"),
        sa.Column('payment_method', sa.String(50), nullable=True, comment="결제 수단 (카드, 계좌이체 등)"),
        sa.Column('payment_status', sa.String(20), nullable=False, comment="결제 상태 (SUCCESS, FAILED, REFUND)"),
        sa.Column('subscription_start_date', sa.DateTime(), nullable=False, comment="구독 시작일"),
        sa.Column('subscription_end_date', sa.DateTime(), nullable=False, comment="구독 종료일"),
        sa.Column('created_at', sa.DateTime(), nullable=False, comment="결제 시간"),
        sa.Column('transaction_id', sa.String(255), nullable=True, comment="결제 고유 ID (PG사 제공)"),
        sa.Column('pg_provider', sa.String(50), nullable=True, comment="PG사 (토스페이, 네이버페이 등)"),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.UniqueConstraint('transaction_id')
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Drop payment_history table
    op.drop_table('payment_history')

    # Remove membership columns from user table
    op.drop_column('user', 'subscription_expire_date')
    op.drop_column('user', 'membership_tier')
