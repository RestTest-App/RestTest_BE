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
    status = await MembershipService.check_subscription_status(current_user)

    response = {
        "user_id": current_user.id,
        "membership_tier": current_user.membership_tier,
        "is_active": status["is_active"],
        "is_expired": status["is_expired"],
        "subscription_expire_date": status["expire_date"].isoformat() if status["expire_date"] else None
    }

    return ok(data=response, message="멤버십 정보 조회 성공")


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
                "subscription_expire_date": "2025-12-30T00:00:00"
            }
        }
    """
    result = await MembershipService.upgrade_membership(
        db,
        current_user,
        request.membership_tier,
        request.payment_amount,
        request.duration_days
    )

    # subscription_expire_date를 isoformat으로 변환
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
    payment_histories = await MembershipService.get_payment_history(db, current_user.id)

    return ok(data=payment_histories, message="결제 이력 조회 성공")
