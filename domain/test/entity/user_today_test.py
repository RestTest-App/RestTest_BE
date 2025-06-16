from sqlalchemy import Column, Integer, Boolean, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.base import Base
from sqlalchemy import ForeignKey, BigInteger


class UserTodayTest(Base):
    __tablename__ = "user_today_test"

    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    today_test_id = Column(BigInteger, ForeignKey("today_test.id", ondelete="CASCADE"), nullable=False)
    is_solved = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint("user_id", "today_test_id", name="uq_user_today_test"),
    )

    user = relationship("User", back_populates="user_today_tests")
    today_test = relationship("TodayTest", back_populates="user_today_tests")
