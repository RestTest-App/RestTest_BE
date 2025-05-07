from sqlalchemy import Column, BigInteger, Integer, Boolean, DateTime, ForeignKey
from database.base import Base


class ReviewNoteByRestQuestion(Base):
    __tablename__ = "review_note_by_rest_question"

    id = Column(BigInteger, primary_key=True, comment="쉬엄모드 복습노트 문제 고유 식별자")
    selected_answer = Column(Integer, nullable=True, comment="사용자가 선택한 답")
    is_correct = Column(Boolean, nullable=False, comment="정답 여부")
    added_at = Column(DateTime, nullable=False, comment="추가된 일시")
    review_note_by_rest_id = Column(BigInteger, ForeignKey("review_note_by_rest.id"), nullable=False, comment="복습노트 ID")
    question_id = Column(BigInteger, ForeignKey("question.id"), nullable=False, comment="문제 ID")
