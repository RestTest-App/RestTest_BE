from sqlalchemy import Column, BigInteger, DateTime, String, ForeignKey
from database.base import Base


class ReviewNoteByRest(Base):
    __tablename__ = "review_note_by_rest"

    id = Column(BigInteger, primary_key=True, comment="쉬엄모드 복습노트 고유 식별자")
    created_at = Column(DateTime, nullable=False, comment="최초 생성일시")
    updated_at = Column(DateTime, nullable=False, comment="마지막 업데이트")
    name = Column(String(100), nullable=False, comment="복습노트 이름")
    user_id = Column(BigInteger, ForeignKey("user.id"), nullable=False, comment="사용자 ID")
    certificate_id = Column(BigInteger, ForeignKey("certificate.id"), nullable=False, comment="자격증 ID")

