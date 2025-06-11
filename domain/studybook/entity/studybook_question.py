from sqlalchemy import Column, BigInteger, Text, String, Integer, ForeignKey, JSON
from database.base import Base


class StudyBookQuestion(Base):
    __tablename__ = "studybook_question"

    id = Column(BigInteger, primary_key=True, comment="나의 문제집 문제 고유 식별자")
    study_book_id = Column(BigInteger, ForeignKey("studybook.id"), nullable=False, comment="문제집 ID")

    description = Column(Text, nullable=False, comment="문제 설명")
    description_detail = Column(Text, nullable=True, comment="문제 상세 설명")
    description_image = Column(String(255), nullable=True, comment="문제 참고 이미지")
    options = Column(JSON, nullable=False, comment="문제 보기")
    answer = Column(Integer, nullable=False, comment="정답")
    option_explanations = Column(JSON, nullable=True, comment="보기 별 해설")
