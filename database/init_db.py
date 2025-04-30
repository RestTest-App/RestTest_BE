from database.base import Base
from database.session import engine
from domain.test.entity.test import Test

def init_db():
    Base.metadata.create_all(bind=engine)