"""stub baseline for existing DB

Revision ID: e41ef1fb1ba4
Revises:
Create Date: 2025-06-13 12:00:00
"""
from alembic import op
import sqlalchemy as sa

# 리비전 식별자
revision = 'e41ef1fb1ba4'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # 이 stub 에선 아무 작업도 하지 않습니다.
    pass

def downgrade():
    pass