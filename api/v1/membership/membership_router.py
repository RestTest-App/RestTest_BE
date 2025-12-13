from fastapi import APIRouter, Depends
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependency import get_current_user
from database.dependency import get_db
from domain.user.entity.user import User
from domain.membership.service.membership_service import MembershipService
from app.utils.dto.success import ok
from pydantic import BaseModel, Field


router = APIRouter()


class UpgradeMembershipRequest(BaseModel):
    """멤버십 업그레이드 요청 DTO"""
    membership_tier: str = Field(..., description="멤버십 등급 (FREE, PREMIUM)")
    payment_amount: int = Field(default=0, description="결제 금액 (원)")
    duration_days: int = Field(default=30, description="구독 기간 (일)")


class MembershipInfoResponse(BaseModel):
    """멤버십 정보 응답 DTO"""
    user_id: int
    membership_tier: str
    is_active: bool
    is_expired: bool
    subscription_expire_date: str | None


@router.get("/info")
async def get_membership_info(
    current_user: Annotated[User, Depends(get_current_user)]
):
    """
    멤버십 정보 조회

    Returns:
        {
            "code": 200,
            "message": "멤버십 정보 조회 성공",
            "data": {
                "user_id": 1,
                "membership_tier": "FREE",
                "is_active": false,
                "is_expired": false,
                "subscription_expire_date": null
            }
        }
    """
    subscription_status = await MembershipService.check_subscription_status(current_user)

    membership_tier = getattr(current_user, 'membership_tier', 'FREE')

    response = MembershipInfoResponse(
        user_id=current_user.id,
        membership_tier=membership_tier,
        is_active=subscription_status["is_active"],
        is_expired=subscription_status["is_expired"],
        subscription_expire_date=subscription_status["expire_date"].isoformat() if subscription_status["expire_date"] else None
    )

    return ok(data=response.model_dump(), message="멤버십 정보 조회 성공")


@router.patch("/upgrade")
async def upgrade_membership(
    request: UpgradeMembershipRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    멤버십 업그레이드 (테스트용)

    Request Body:
        {
            "membership_tier": "PREMIUM",
            "payment_amount": 9900,
            "duration_days": 30
        }

    Returns:
        {
            "code": 200,
            "message": "멤버십 업그레이드 성공",
            "data": {
                "user_id": 1,
                "previous_tier": "FREE",
                "new_tier": "PREMIUM",
                "subscription_expire_date": "2026-01-11T12:00:00"
            }
        }
    """
    result = await MembershipService.upgrade_membership(
        db=db,
        user=current_user,
        membership_tier=request.membership_tier,
        payment_amount=request.payment_amount,
        duration_days=request.duration_days
    )

    # subscription_expire_date가 datetime이면 문자열로 변환
    if result["subscription_expire_date"]:
        result["subscription_expire_date"] = result["subscription_expire_date"].isoformat()

    return ok(data=result, message="멤버십 업그레이드 성공")


@router.get("/payment-history")
async def get_payment_history(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    결제 이력 조회

    Returns:
        {
            "code": 200,
            "message": "결제 이력 조회 성공",
            "data": [
                {
                    "id": 1,
                    "membership_tier": "PREMIUM",
                    "payment_amount": 9900,
                    "payment_method": "TEST",
                    "payment_status": "SUCCESS",
                    "subscription_start_date": "2025-11-30T00:00:00",
                    "subscription_end_date": "2025-12-30T00:00:00",
                    "created_at": "2025-11-30T00:00:00",
                    "transaction_id": "TEST_1_1234567890",
                    "pg_provider": "TEST"
                }
            ]
        }
    """
    payment_history = await MembershipService.get_payment_history(
        db=db,
        user_id=current_user.id
    )

    return ok(data=payment_history, message="결제 이력 조회 성공")


@router.patch("/cancel")
async def cancel_membership(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    멤버십 구독 해지

    구독을 해지합니다. 만료일까지는 프리미엄 기능을 계속 사용할 수 있습니다.

    Returns:
        {
            "code": 200,
            "message": "구독 해지가 완료되었습니다",
            "data": {
                "user_id": 1,
                "membership_tier": "PREMIUM",
                "subscription_expire_date": "2026-01-11T12:00:00",
                "days_remaining": 29,
                "message": "만료일까지 프리미엄 기능을 계속 사용할 수 있습니다."
            }
        }
    """
    from datetime import datetime
    from exception.client_exception import BadRequestException

    membership_tier = getattr(current_user, 'membership_tier', 'FREE')
    subscription_expire_date = getattr(current_user, 'subscription_expire_date', None)

    # 이미 FREE 등급이면 해지할 구독이 없음
    if membership_tier == "FREE":
        raise BadRequestException(message="해지할 구독이 없습니다.")

    # 구독 상태 확인
    subscription_status = await MembershipService.check_subscription_status(current_user)

    if subscription_status["is_expired"]:
        raise BadRequestException(message="이미 만료된 구독입니다.")

    # 남은 일수 계산
    if subscription_expire_date:
        now = datetime.now()
        days_remaining = (subscription_expire_date - now).days
    else:
        days_remaining = 0

    # 실제 구독 해지 로직은 여기서 구현
    # (예: auto_renewal 플래그 설정, 또는 즉시 FREE로 변경 등)
    # 현재는 정보만 반환

    response = {
        "user_id": current_user.id,
        "membership_tier": membership_tier,
        "subscription_expire_date": subscription_expire_date.isoformat() if subscription_expire_date else None,
        "is_active": subscription_status["is_active"],
        "days_remaining": days_remaining,
        "message": f"만료일({subscription_expire_date.date()})까지 프리미엄 기능을 계속 사용할 수 있습니다." if subscription_expire_date else "구독 해지가 완료되었습니다."
    }

    return ok(data=response, message="구독 해지가 완료되었습니다")
