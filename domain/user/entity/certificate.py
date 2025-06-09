from sqlalchemy import Column, BigInteger, String
from database.base import Base


class Certificate(Base):
    __tablename__ = "certificate"

    id = Column(BigInteger, primary_key=True, comment="자격증 고유 식별값")
    name = Column(String(100), nullable=False, comment="자격증 이름")
