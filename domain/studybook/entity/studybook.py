from sqlalchemy import Column, BigInteger, DateTime, String, Integer, ForeignKey
from database.base import Base


class StudyBook(Base):
    __tablename__ = "studybook"

    id = Column(BigInteger, primary_key=True, comment="나의 문제집 고유 식별자")
    created_at = Column(DateTime, nullable=False, comment="문제집 생성일시")
    name = Column(String(100), nullable=False, comment="문제집 이름")
    question_count = Column(Integer, nullable=False, comment="문제 수")
    file_color = Column(String(20), nullable=False, comment="파일 색상")
    user_id = Column(BigInteger, ForeignKey("user.id"), nullable=False, comment="사용자 고유 식별값")
