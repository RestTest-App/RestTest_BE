from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update, select

from domain.user.entity.user import User
from domain.payment.entity.payment_history import PaymentHistory
from domain.payment.repository.payment_history_repository import PaymentHistoryRepository


class MembershipService:
    """멤버십 관리 서비스"""

    @staticmethod
    async def upgrade_membership(
        db: AsyncSession,
        user: User,
        membership_tier: str,
        payment_amount: int = 0,
        duration_days: int = 30
    ) -> dict:
        """
        멤버십 업그레이드 (테스트용)

        Args:
            db: AsyncSession
            user: User 객체
            membership_tier: 업그레이드할 멤버십 등급 (PREMIUM, FREE)
            payment_amount: 결제 금액 (원)
            duration_days: 구독 기간 (일)

        Returns:
            {
                "user_id": int,
                "previous_tier": str,
                "new_tier": str,
                "subscription_expire_date": datetime
            }
        """
        previous_tier = user.membership_tier
        start_date = datetime.now()
        end_date = start_date + timedelta(days=duration_days)

        # User 멤버십 정보 업데이트
        await db.execute(
            update(User)
            .where(User.id == user.id)
            .values(
                membership_tier=membership_tier,
                subscription_expire_date=end_date if membership_tier != 'FREE' else None
            )
        )

        # 결제 이력 생성 (FREE가 아닐 경우)
        if membership_tier != 'FREE':
            payment_history = PaymentHistory(
                user_id=user.id,
                membership_tier=membership_tier,
                payment_amount=payment_amount,
                payment_method="TEST",
                payment_status="SUCCESS",
                subscription_start_date=start_date,
                subscription_end_date=end_date,
                created_at=start_date,
                transaction_id=f"TEST_{user.id}_{int(start_date.timestamp())}",
                pg_provider="TEST"
            )
            await PaymentHistoryRepository.create(db, payment_history)

        await db.commit()

        return {
            "user_id": user.id,
            "previous_tier": previous_tier,
            "new_tier": membership_tier,
            "subscription_expire_date": end_date if membership_tier != 'FREE' else None
        }

    @staticmethod
    async def check_subscription_status(user: User) -> dict:
        """
        구독 상태 확인

        Args:
            user: User 객체

        Returns:
            {
                "is_active": bool,
                "is_expired": bool,
                "tier": str,
                "expire_date": datetime or None
            }
        """
        now = datetime.now()
        is_expired = False
        is_active = user.membership_tier != 'FREE'

        # 구독 만료일이 있고, 현재 시간이 만료일을 넘었는지 확인
        if user.subscription_expire_date and now > user.subscription_expire_date:
            is_expired = True
            is_active = False

        return {
            "is_active": is_active,
            "is_expired": is_expired,
            "tier": user.membership_tier,
            "expire_date": user.subscription_expire_date
        }

    @staticmethod
    async def get_payment_history(db: AsyncSession, user_id: int) -> list:
        """
        사용자의 결제 이력 조회

        Args:
            db: AsyncSession
            user_id: 사용자 ID

        Returns:
            결제 이력 리스트
        """
        payment_histories = await PaymentHistoryRepository.get_by_user_id(db, user_id)

        return [
            {
                "id": ph.id,
                "membership_tier": ph.membership_tier,
                "payment_amount": ph.payment_amount,
                "payment_method": ph.payment_method,
                "payment_status": ph.payment_status,
                "subscription_start_date": ph.subscription_start_date.isoformat(),
                "subscription_end_date": ph.subscription_end_date.isoformat(),
                "created_at": ph.created_at.isoformat(),
                "transaction_id": ph.transaction_id,
                "pg_provider": ph.pg_provider
            }
            for ph in payment_histories
        ]
