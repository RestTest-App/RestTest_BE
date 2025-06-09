from sqlalchemy import Column, BigInteger, Text, String, Integer, DECIMAL, ForeignKey, JSON
from database.base import Base


class Question(Base):
    __tablename__ = "question"

    id = Column(BigInteger, primary_key=True, comment="문제 고유 식별자")
    answer_rate = Column(DECIMAL(5, 2), nullable=True, comment="정답률")
    section = Column(String(50), nullable=False, comment="문제 분류")
    description = Column(Text, nullable=False, comment="문제 설명")
    description_detail = Column(Text, nullable=True, comment="문제 상세 설명")
    description_image = Column(String(255), nullable=True, comment="문제 참고 이미지")
    options = Column(JSON, nullable=False, comment="문제 보기")
    answer = Column(Integer, nullable=False, comment="정답")
    option_explanations = Column(JSON, nullable=False, comment="보기 별 해설")
    exam_id = Column(BigInteger, ForeignKey("exam.id"), nullable=False, comment="시험 ID")
    exam_section_id = Column(BigInteger, ForeignKey("exam_section.id"), nullable=False, comment="과목 고유 식별값")
