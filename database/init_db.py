from database.base import Base
from database.session import engine

# import domain.user.entity
# import domain.test.entity
# import domain.review.entity
# import domain.studybook.entity

async def init_db():
    Base.metadata.create_all(bind=engine)