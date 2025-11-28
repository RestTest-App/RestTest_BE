import domain.user.entity
import domain.test.entity
import domain.review.entity
import domain.studybook.entity

from database.base import Base
from database.session import engine

async def init_db() -> None:
    async with engine.begin() as conn:
        pass