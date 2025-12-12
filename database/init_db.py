import domain.user.entity
import domain.test.entity
import domain.review.entity
import domain.studybook.entity
import domain.payment.entity

from database.base import Base
from database.session import engine
from sqlalchemy import text

async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

        # explanation 칼럼 추가 (없으면 추가)
        try:
            await conn.execute(text(
                "ALTER TABLE studybook_question ADD COLUMN explanation LONGTEXT NULL COMMENT '문제 해설';"
            ))
        except Exception as e:
            if "Duplicate column name" not in str(e):
                print(f"[WARNING] explanation 칼럼 추가 중 오류: {e}")

        # User 테이블에 멤버십 관련 칼럼 추가 (없으면 추가)
        try:
            await conn.execute(text(
                "ALTER TABLE user ADD COLUMN membership_tier VARCHAR(20) NOT NULL DEFAULT 'FREE' COMMENT '멤버십 등급 (FREE, PREMIUM)';"
            ))
        except Exception as e:
            if "Duplicate column name" not in str(e):
                print(f"[WARNING] membership_tier 칼럼 추가 중 오류: {e}")

        try:
            await conn.execute(text(
                "ALTER TABLE user ADD COLUMN subscription_expire_date DATETIME NULL COMMENT '구독 만료일';"
            ))
        except Exception as e:
            if "Duplicate column name" not in str(e):
                print(f"[WARNING] subscription_expire_date 칼럼 추가 중 오류: {e}")
