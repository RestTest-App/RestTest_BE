from sqlalchemy import Column, BigInteger, String, Integer, DateTime, ForeignKey
from database.base import Base


class PaymentHistory(Base):
    __tablename__ = "payment_history"

    id = Column(BigInteger, primary_key=True, comment="결제 이력 고유 식별값")
    user_id = Column(BigInteger, ForeignKey("user.id"), nullable=False, comment="사용자 ID")
    membership_tier = Column(String(20), nullable=False, comment="구매한 멤버십 등급")
    payment_amount = Column(Integer, nullable=False, comment="결제 금액 (원)")
    payment_method = Column(String(50), nullable=True, comment="결제 수단 (카드, 계좌이체 등)")
    payment_status = Column(String(20), nullable=False, comment="결제 상태 (SUCCESS, FAILED, REFUND)")
    subscription_start_date = Column(DateTime, nullable=False, comment="구독 시작일")
    subscription_end_date = Column(DateTime, nullable=False, comment="구독 종료일")
    created_at = Column(DateTime, nullable=False, comment="결제 시간")
    transaction_id = Column(String(255), unique=True, nullable=True, comment="결제 고유 ID (PG사 제공)")
    pg_provider = Column(String(50), nullable=True, comment="PG사 (토스페이, 네이버페이 등)")
