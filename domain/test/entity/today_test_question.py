from sqlalchemy import Column, BigInteger, Text, Integer, JSON, ForeignKey
from database.base import Base


class TodayTestQuestion(Base):
    __tablename__ = "today_test_question"

    id = Column(BigInteger, primary_key=True, comment="오늘의 문제 질문 고유 식별자")
    today_test_by_ai_id = Column(BigInteger, ForeignKey("today_test.id"), nullable=False, comment="오늘의 문제 ID")

    description = Column(Text, nullable=False, comment="문제 설명")
    description_detail = Column(Text, nullable=True, comment="문제 상세 설명")
    options = Column(JSON, nullable=False, comment="보기 목록")
    answer = Column(Integer, nullable=False, comment="정답")
    option_explanations = Column(JSON, nullable=False, comment="보기별 해설")
