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
from app.goal.service.goal_service import GoalService
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


# 테스트용 사용자 정보 조회 (user_id로 직접 조회)
@router.get("/get-user-info-test/{user_id}")
async def get_user_info_test(user_id: int, db: AsyncSession = Depends(get_db)):
    """
    테스트용 사용자 정보 조회 API

    user_id를 직접 전달하여 사용자 정보를 조회합니다.
    인���이 필요하지 않습니다.
    """
    from domain.auth.service.auth_service import AuthService

    user = await AuthService.get_user_by_id(db, user_id)

    if not user:
        raise ForbiddenException(message="사용자를 찾을 수 없습니다.")

    user_dict = user.__dict__.copy()

    # SQLAlchemy 내부 속성 제거
    user_dict.pop('_sa_instance_state', None)

    # birthday를 문자열로 변환 (date 객체는 JSON 직렬화 불가)
    if user_dict.get("birthday"):
        user_dict["birthday"] = user_dict["birthday"].isoformat()

    # created_at를 문자열로 변환
    if user_dict.get("created_at"):
        user_dict["created_at"] = user_dict["created_at"].isoformat()

    # monthly_study_date가 dict이면 None으로 설정
    if isinstance(user_dict.get("monthly_study_date"), dict):
        user_dict["monthly_study_date"] = None

    return ok(data=user_dict, message="사용자 정보 조회 성공")


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
    request: UpdateUserInfoRequest,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
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


# 사용자 목표 진행도 조회
@router.get("/goals/progress")
async def get_goals_progress(user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """
    사용자의 오늘 목표 진행도 조회 API

    사용자가 설정한 모든 목표의 오늘 진행 상황을 조회합니다.

    Returns:
        {
            "code": 200,
            "message": "목표 진행도 조회 성공",
            "data": {
                "today_date": "2025-11-17",
                "total_goals": 3,
                "achieved_goals": 2,
                "overall_progress": 66.7,
                "goals": [...]
            }
        }
    """
    try:
        goals_progress = await GoalService.get_all_goals_progress(db, user.id)
        return ok(data=goals_progress, message="목표 진행도 조회 성공")
    except Exception as e:
        raise


# 개별 목표 진행도 조회
@router.get("/goals/progress/{goal_id}")
async def get_goal_progress(goal_id: int, user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """
    개별 목표 진행도 조회 API

    특정 목표의 오늘 진행 상황을 조회합니다.

    Args:
        goal_id: 목표 ID (1-9)

    Returns:
        {
            "code": 200,
            "message": "목표 진행도 조회 성공",
            "data": {
                "goal_id": 1,
                "goal_name": "하루에 10문제",
                "goal_type": "daily_problem",
                "target_value": 10,
                "current_progress": 7,
                "progress_percent": 70.0,
                "is_achieved": false
            }
        }
    """
    try:
        goal_progress = await GoalService.get_goal_progress(db, user.id, goal_id)

        # 목표가 없을 경우
        if "error" in goal_progress:
            raise BadRequestException(message=goal_progress["error"])

        return ok(data=goal_progress, message="목표 진행도 조회 성공")
    except BadRequestException:
        raise
    except Exception as e:
        raise