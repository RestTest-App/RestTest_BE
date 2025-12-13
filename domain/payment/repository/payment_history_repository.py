from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from domain.payment.entity.payment_history import PaymentHistory


class PaymentHistoryRepository:
    """결제 이력 Repository"""

    @staticmethod
    async def create(db: AsyncSession, payment_history: PaymentHistory) -> PaymentHistory:
        """
        결제 이력 생성

        Args:
            db: AsyncSession
            payment_history: PaymentHistory 객체

        Returns:
            생성된 PaymentHistory
        """
        db.add(payment_history)
        await db.flush()  # Service에서 commit 관리
        return payment_history

    @staticmethod
    async def get_by_id(db: AsyncSession, payment_id: int) -> Optional[PaymentHistory]:
        """
        ID로 결제 이력 조회

        Args:
            db: AsyncSession
            payment_id: 결제 이력 ID

        Returns:
            PaymentHistory 또는 None
        """
        result = await db.execute(
            select(PaymentHistory).where(PaymentHistory.id == payment_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_user_id(db: AsyncSession, user_id: int) -> List[PaymentHistory]:
        """
        사용자의 모든 결제 이력 조회

        Args:
            db: AsyncSession
            user_id: 사용자 ID

        Returns:
            PaymentHistory 리스트
        """
        stmt = select(PaymentHistory).where(
            PaymentHistory.user_id == user_id
        ).order_by(PaymentHistory.created_at.desc())

        result = await db.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def get_by_transaction_id(db: AsyncSession, transaction_id: str) -> Optional[PaymentHistory]:
        """
        거래 ID로 결제 이력 조회

        Args:
            db: AsyncSession
            transaction_id: 거래 ID

        Returns:
            PaymentHistory 또는 None
        """
        stmt = select(PaymentHistory).where(
            PaymentHistory.transaction_id == transaction_id
        )

        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_latest_by_user_id(db: AsyncSession, user_id: int) -> Optional[PaymentHistory]:
        """
        사용자의 가장 최근 결제 이력 조회

        Args:
            db: AsyncSession
            user_id: 사용자 ID

        Returns:
            가장 최근 PaymentHistory 또는 None
        """
        stmt = select(PaymentHistory).where(
            PaymentHistory.user_id == user_id
        ).order_by(PaymentHistory.created_at.desc()).limit(1)

        result = await db.execute(stmt)
        return result.scalar_one_or_none()
