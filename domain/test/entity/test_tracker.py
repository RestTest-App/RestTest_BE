from sqlalchemy import Column, BigInteger, ForeignKey, Boolean, DateTime, Integer
from database.base import Base


class TestTracker(Base):
    __tablename__ = "test_tracker"

    id = Column(BigInteger, primary_key=True, comment="시험 기록 고유 식별값")
    exam_id = Column(BigInteger, ForeignKey("exam.id"), nullable=False, comment="시험 ID")
    user_id = Column(BigInteger, ForeignKey("user.id"), nullable=False, comment="사용자 ID")
    is_passed = Column(Boolean, nullable=False, comment="통과 여부")
    solved_at = Column(DateTime, nullable=False, comment="응시 일시")
    score = Column(Integer, nullable=False, comment="점수")
