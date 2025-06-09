from sqlalchemy import Column, BigInteger, ForeignKey, Integer, Boolean
from database.base import Base


class UserQuestionTracker(Base):
    __tablename__ = "user_question_tracker"

    id = Column(BigInteger, primary_key=True, comment="시험 질문 응답 고유 식별값")
    study_tracker_id = Column(BigInteger, ForeignKey("test_tracker.id"), nullable=False, comment="시험 기록 ID")
    question_id = Column(BigInteger, ForeignKey("question.id"), nullable=False, comment="문제 ID")
    selected_answer = Column(Integer, nullable=True, comment="선택한 답")
    is_correct = Column(Boolean, nullable=False, comment="정답 여부")
    add_to_review = Column(Boolean, nullable=False, comment="리뷰노트 등록 여부")
