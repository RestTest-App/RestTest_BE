from sqlalchemy import Column, BigInteger, String, Integer, ForeignKey
from database.base import Base


class ExamSection(Base):
    __tablename__ = "exam_section"

    id = Column(BigInteger, primary_key=True, comment="과목 고유 식별값")
    name = Column(String(100), nullable=True, comment="과목 명")
    order = Column(Integer, nullable=False, comment="과목 순서")
    exam_id = Column(BigInteger, ForeignKey("exam.id"), nullable=False, comment="시험 고유 식별값")
