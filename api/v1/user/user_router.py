from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import ValidationError

from app.auth.dependency import get_current_user, get_db
from app.user.dto.request.update_user_profile_request import UpdateUserProfileRequest
from app.user.dto.request.update_user_info_request import UpdateUserInfoRequest
from app.user.dto.response.get_user_info_response import GetUserInfoResponse
from app.user.dto.response.update_user_info_response import UpdateUserInfoResponse
from app.user.usecase.update_user_profile_usecase import UpdateUserProfileUseCase
from app.user.usecase.update_user_info_usecase import UpdateUserInfoUseCase
from app.utils.dto.success import ok
from domain.auth.service.jwt_service import JWTService
from exception.client_exception import BadRequestException, ForbiddenException


router = APIRouter()

jwt_service = JWTService()


# 사용자 정보 조회
@router.get("/get-user-info", response_model=GetUserInfoResponse)
async def get_user_info(user=Depends(get_current_user)):
    user_dict = user.__dict__.copy()
    if isinstance(user_dict.get("monthly_study_date"), dict):
        user_dict["monthly_study_date"] = None

    user_info = GetUserInfoResponse.model_validate(user_dict)
    payload: dict = user_info.model_dump(mode="json")
    return ok(data=payload, message="사용자 정보 조회 성공")


# 사용자 프로필 수정 (닉네임, 프로필 이미지)
@router.patch("/update-user-profile", response_model=UpdateUserInfoResponse)
async def update_user_profile(
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    nickname: str = Form(None),
    delete_image: bool = Form(False),
    profile_image: UploadFile = File(None)
):
    """
    사용자 프로필 수정 API (Multipart Form Data)

    Args:
        user: 현재 로그인한 사용자 (OAuth 인증됨)
        db: Database session
        nickname: 변경할 닉네임 (선택사항)
        delete_image: 프로필 이미지 삭제 여부
        profile_image: 업로드할 프로필 이미지 파일 (png, jpg, jpeg)

    Returns:
        UpdateUserInfoResponse: 업데이트된 사용자 정보

    Raises:
        400: 올바른 닉네임 형식이 아님
        401: access token 만료
        403: 권한 없음
        500: 서버 오류
    """
    try:
        # Request DTO 생성 (nickname 검증 포함)
        request = UpdateUserProfileRequest(
            nickname=nickname,
            delete_image=delete_image
        )

        # UseCase 실행
        usecase = UpdateUserProfileUseCase(db)
        updated_user = await usecase.execute(user, request, profile_image)

        # Response 생성
        response = UpdateUserInfoResponse(
            id=updated_user.id,
            nickname=updated_user.nickname,
            gender=updated_user.gender,
            birthday=updated_user.birthday.isoformat() if updated_user.birthday else None,
            job=updated_user.job,
            rest_goal=updated_user.rest_goal,
            test_goal=updated_user.test_goal,
            goal_table=updated_user.goal_table,
            profile_image=updated_user.profile_image
        )

        return ok(data=response.model_dump(), message="프로필 수정 성공")

    except ValidationError as e:
        # Pydantic 검증 오류 (nickname 형식)
        raise BadRequestException(message="올바른 닉네임 형식이 아닙니다.")
    except ValueError as e:
        # 커스텀 검증 오류
        raise BadRequestException(message=str(e))
    except ForbiddenException:
        raise
    except Exception as e:
        raise


# 사용자 정보 수정 (모든 필드)
@router.patch("/update-user-info")
async def update_user_info(
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    request: UpdateUserInfoRequest
):
    """
    사용자 정보 수정 API (JSON Body)

    여러 필드를 동시에 수정 가능합니다.
    필드를 지정하지 않으면 해당 필드는 변경되지 않습니다.

    Request Body (JSON):
    {
        "nickname": "새로운닉네임",
        "gender": "M",
        "birthday": "1990-01-01",
        "job": "개발자",
        "rest_goal": 5,
        "test_goal": 10,
        "goal_table": [1, 3, 5]
    }

    Args:
        user: 현재 로그인한 사용자 (OAuth 인증됨)
        db: Database session
        request: 업데이트 요청 DTO (UpdateUserInfoRequest)

    Returns:
        UpdateUserInfoResponse: 업데이트된 사용자 정보

    Raises:
        400: 필드 검증 실패
        401: access token 만료
        403: 권한 없음
        500: 서버 오류
    """
    try:
        # UseCase 실행
        usecase = UpdateUserInfoUseCase(db)
        updated_user = await usecase.execute(user, request)

        # Response 생성
        response = UpdateUserInfoResponse(
            id=updated_user.id,
            nickname=updated_user.nickname,
            gender=updated_user.gender,
            birthday=updated_user.birthday.isoformat() if updated_user.birthday else None,
            job=updated_user.job,
            rest_goal=updated_user.rest_goal,
            test_goal=updated_user.test_goal,
            goal_table=updated_user.goal_table,
            profile_image=updated_user.profile_image
        )

        return ok(data=response.model_dump(), message="사용자 정보 수정 성공")

    except ValidationError as e:
        # Pydantic 검증 오류
        errors = e.errors()
        error_messages = [f"{err['loc'][0]}: {err['msg']}" for err in errors]
        raise BadRequestException(message=", ".join(error_messages))
    except ValueError as e:
        # 커스텀 검증 오류
        raise BadRequestException(message=str(e))
    except ForbiddenException:
        raise
    except Exception as e:
        raise