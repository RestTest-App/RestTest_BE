from sqlalchemy import Column, BigInteger, String, DECIMAL, Integer, ForeignKey
from database.base import Base


class Exam(Base):
    __tablename__ = "exam"

    id = Column(BigInteger, primary_key=True, comment="시험 고유 식별값")
    name = Column(String(100), nullable=False, comment="시험 이름")
    pass_rate = Column(DECIMAL(5, 2), nullable=True, comment="합격률")
    year = Column(Integer, nullable=False, comment="응시 년도")
    month = Column(Integer, nullable=False, comment="응시 월")
    trial = Column(Integer, nullable=True, comment="회차")
    time = Column(Integer, nullable=False, comment="시험 시간")
    certificate_id = Column(BigInteger, ForeignKey("certificate.id"), nullable=False, comment="자격증 ID")
