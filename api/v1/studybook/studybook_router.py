# api/v1/studybook/studybook_router.py

from fastapi import APIRouter, UploadFile, File, Form, Path, Depends
from typing import Annotated
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.studybook.dto.response.upload_studybook_response_dto import UploadStudybookResponseDTO
from app.studybook.dto.response.my_studybook_response_dto import MyStudybookResponseDTO
from app.studybook.dto.response.delete_studybook_response_dto import DeleteStudybookResponseDTO
from app.studybook.dto.response.studybook_detail_response_dto import StudybookDetailResponseDTO
from app.studybook.usecase.studybook_usecase import (
    upload_my_studybook_by_img_usecase,
    upload_my_studybook_usecase
)

from domain.user.entity.user import User
from database.dependency import get_db
from app.studybook.usecase.studybook_usecase import (
    upload_my_studybook_by_pdf_usecase,
    get_my_studybooks_usecase,
    get_studybook_detail_usecase,
    delete_my_studybook_usecase
)
from app.utils.dummy_questions import dummy_questions
from app.studybook.usecase.studybook_usecase import upload_my_studybook_by_dummy_usecase

from app.auth.dependency import get_current_user, check_api_rate_limit
router = APIRouter()
#
# def get_dummy_user() -> User:
#     return User(
#         id=1,
#         auth_provider="google",
#         email="dummy@example.com",
#         nickname="Dummy",
#         gender="male",
#         birthday=datetime(2000, 1, 1),
#         job="Student",
#         agree_to_terms=True,
#         created_at=datetime.now(),
#         studybook_limit=5,
#         rest_goal=None,
#         test_goal=None,
#         profile_image=None,
#         total_study_days=0,
#         monthly_study_date=[],  # 수정될 수 있음
#         is_study_today=False,
#     )

@router.post("/upload-my-studybook-by-dummy")
async def upload_my_studybook_by_dummy(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # 테스트용 문제집 이름 (원하면 param으로도 받을 수 있음)
    studybook_name = "테스트 더미 문제집"
    return await upload_my_studybook_by_dummy_usecase(studybook_name, dummy_questions, current_user, db)


@router.post("/upload-my-studybook", response_model=UploadStudybookResponseDTO)
async def upload_my_studybook(
    files: list[UploadFile] = File(...),
    copyright_agreed: bool = Form(...),  # 저작권 동의 필수
    answers: str = Form(None),
    question_count: int = Form(None),
    *,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[None, Depends(check_api_rate_limit)]  # Rate Limit 체크
):
    """
    통합 문제집 업로드 API (PDF 또는 이미지)

    - PDF: 1개 파일만 업로드 가능
    - 이미지: 여러 개 파일 업로드 가능

    Form Data Parameters:
        files: 업로드할 파일 (PDF 또는 이미지)
        copyright_agreed: 저작권 동의 여부 (필수, true 필요)
        answers: JSON 형식의 정답 리스트 (선택사항)
        question_count: 예상 문제 개수 (PDF 전용, 선택사항)
    """
    from exception.client_exception import BadRequestException

    # 저작권 동의 확인
    if not copyright_agreed:
        raise BadRequestException(
            message="저작권 관련 법률을 준수하기 위해 동의가 필요합니다. 타인의 저작물을 무단으로 업로드하지 마세요."
        )

    answer_list = None
    if answers:
        import json
        try:
            answer_list = json.loads(answers)
        except:
            answer_list = None
    return await upload_my_studybook_usecase(files, current_user, db, answer_list, question_count)


@router.post("/upload-my-studybook-by-pdf", response_model=UploadStudybookResponseDTO)
async def upload_my_studybook_by_pdf(
    file: UploadFile = File(...),
    answers: str = None,
    question_count: int = None,
    *,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)]
):
    # answers가 있으면 JSON 문자열로 파싱
    answer_list = None
    if answers:
        import json
        try:
            answer_list = json.loads(answers)
        except:
            answer_list = None
    return await upload_my_studybook_by_pdf_usecase(file, current_user, db, answer_list, question_count)
@router.post("/upload-my-studybook-by-img", response_model=UploadStudybookResponseDTO)
async def upload_my_studybook_by_img(
    file: UploadFile = File(...),
    answers: str = None,
    *,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)]
):
    # answers가 있으면 JSON 문자열로 파싱
    answer_list = None
    if answers:
        import json
        try:
            answer_list = json.loads(answers)
        except:
            answer_list = None
    return await upload_my_studybook_by_img_usecase(file, current_user, db, answer_list)
@router.get("/my_studybook", response_model=MyStudybookResponseDTO)
async def my_studybook(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)]
):
    return await get_my_studybooks_usecase(current_user, db)

@router.get("/my_studybook/{studybook_id}", response_model=StudybookDetailResponseDTO)
async def get_studybook_detail(
    studybook_id: Annotated[int, Path()],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)]
):
    return await get_studybook_detail_usecase(studybook_id, current_user, db)

@router.delete("/delete-my-studybook/{studybook_id}", response_model=DeleteStudybookResponseDTO)
async def delete_my_studybook(
    studybook_id: Annotated[int, Path()],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)]
):
    return await delete_my_studybook_usecase(studybook_id, current_user, db)


