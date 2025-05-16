from database.base import Base
from database.session import engine

# ✅ 여기에 반드시 이 import가 있어야 함
from domain.user.entity.certificate import Certificate
from domain.user.entity.user_certificate import UserCertificate
from domain.user.entity.user import User
from domain.test.entity.exam import Exam

def init_db():
    Base.metadata.create_all(bind=engine)