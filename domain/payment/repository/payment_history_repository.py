from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from domain.payment.entity.payment_history import PaymentHistory


class PaymentHistoryRepository:
    """결제 이력 Repository"""

    @staticmethod
    async def create(db: AsyncSession, payment_history: PaymentHistory) -> PaymentHistory:
        """결제 이력 생성"""
        db.add(payment_history)
        await db.flush()
        return payment_history

    @staticmethod
    async def get_by_id(db: AsyncSession, payment_id: int) -> Optional[PaymentHistory]:
        """ID로 결제 이력 조회"""
        result = await db.execute(
            select(PaymentHistory).where(PaymentHistory.id == payment_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_user_id(db: AsyncSession, user_id: int) -> List[PaymentHistory]:
        """사용자의 모든 결제 이력 조회"""
        result = await db.execute(
            select(PaymentHistory)
            .where(PaymentHistory.user_id == user_id)
            .order_by(PaymentHistory.created_at.desc())
        )
        return result.scalars().all()

    @staticmethod
    async def get_by_transaction_id(db: AsyncSession, transaction_id: str) -> Optional[PaymentHistory]:
        """거래 ID로 결제 이력 조회"""
        result = await db.execute(
            select(PaymentHistory).where(PaymentHistory.transaction_id == transaction_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_latest_by_user_id(db: AsyncSession, user_id: int) -> Optional[PaymentHistory]:
        """사용자의 가장 최근 결제 이력 조회"""
        result = await db.execute(
            select(PaymentHistory)
            .where(PaymentHistory.user_id == user_id)
            .order_by(PaymentHistory.created_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()
