from sqlalchemy import Column, BigInteger, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from database.base import Base


class TodayTest(Base):
    __tablename__ = "today_test"

    id = Column(BigInteger, primary_key=True, comment="오늘의 문제 고유 식별자")
    created_at = Column(DateTime, nullable=False, comment="생성일시")
    is_solved = Column(Boolean, nullable=False, comment="응시 완료 여부", default=False)
    certificate_id = Column(BigInteger, ForeignKey("certificate.id"), nullable=False, comment="자격증 ID")
    user_today_tests = relationship("UserTodayTest", back_populates="today_test", cascade="all, delete-orphan")