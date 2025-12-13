"""
Membership Service
멤버십 관련 비즈니스 로직
"""
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
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
        멤버십 업그레이드

        Args:
            db: Database session
            user: 사용자 객체
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
        previous_tier = getattr(user, 'membership_tier', 'FREE')

        # 구독 시작/종료일 설정
        subscription_start = datetime.now()
        subscription_end = subscription_start + timedelta(days=duration_days)

        # User 업데이트
        user.membership_tier = membership_tier
        user.subscription_expire_date = subscription_end if membership_tier != 'FREE' else None

        # PaymentHistory 생성 (FREE가 아닐 경우)
        if membership_tier != 'FREE':
            payment_history = PaymentHistory(
                user_id=user.id,
                membership_tier=membership_tier,
                payment_amount=payment_amount,
                payment_method="TEST",  # 테스트용
                payment_status="SUCCESS",
                subscription_start_date=subscription_start,
                subscription_end_date=subscription_end,
                created_at=subscription_start,
                transaction_id=f"TEST_{user.id}_{int(subscription_start.timestamp())}",
                pg_provider="TEST"
            )

            await PaymentHistoryRepository.create(db, payment_history)

        await db.commit()
        await db.refresh(user)

        return {
            "user_id": user.id,
            "previous_tier": previous_tier,
            "new_tier": membership_tier,
            "subscription_expire_date": subscription_end if membership_tier != 'FREE' else None
        }

    @staticmethod
    async def check_subscription_status(user: User) -> dict:
        """
        구독 상태 확인

        Args:
            user: 사용자 객체

        Returns:
            {
                "is_active": bool,
                "is_expired": bool,
                "expire_date": datetime | None
            }
        """
        membership_tier = getattr(user, 'membership_tier', 'FREE')
        subscription_expire_date = getattr(user, 'subscription_expire_date', None)

        if membership_tier == "FREE" or subscription_expire_date is None:
            return {
                "is_active": False,
                "is_expired": False,
                "expire_date": None
            }

        now = datetime.now()
        is_expired = subscription_expire_date < now

        return {
            "is_active": not is_expired,
            "is_expired": is_expired,
            "expire_date": subscription_expire_date
        }

    @staticmethod
    async def get_payment_history(db: AsyncSession, user_id: int) -> list:
        """
        결제 이력 조회

        Args:
            db: Database session
            user_id: 사용자 ID

        Returns:
            List of payment history dicts
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
