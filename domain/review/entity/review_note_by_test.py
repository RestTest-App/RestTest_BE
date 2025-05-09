from sqlalchemy import Column, BigInteger, DateTime, ForeignKey
from database.base import Base


class ReviewNoteByTest(Base):
    __tablename__ = "review_note_by_test"

    id = Column(BigInteger, primary_key=True, comment="복습노트 고유 식별자")
    created_at = Column(DateTime, nullable=False, comment="생성일시")
    user_id = Column(BigInteger, ForeignKey("user.id"), nullable=False, comment="사용자 ID")
    study_tracker_id = Column(BigInteger, ForeignKey("test_tracker.id"), nullable=False, comment="시험 기록 ID")
