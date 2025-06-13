# api/v1/studybook/studybook_router.py

from fastapi import APIRouter, UploadFile, File, Path, Depends
from typing import Annotated
from datetime import datetime
from sqlalchemy.orm import Session

from app.studybook.dto.response.upload_studybook_response_dto import UploadStudybookResponseDTO
from app.studybook.dto.response.my_studybook_response_dto import MyStudybookResponseDTO
from app.studybook.dto.response.delete_studybook_response_dto import DeleteStudybookResponseDTO
from app.studybook.usecase.studybook_usecase import upload_my_studybook_by_img_usecase

from domain.user.entity.user import User
from database.dependency import get_db
from app.studybook.usecase.studybook_usecase import upload_my_studybook_by_pdf_usecase, get_my_studybooks_usecase
from app.studybook.usecase.studybook_usecase import delete_my_studybook_usecase
from app.auth.dependency import get_current_user
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

@router.post("/upload-my-studybook-by-pdf", response_model=UploadStudybookResponseDTO)
async def upload_my_studybook_by_pdf(
    file: UploadFile = File(...),
    *,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)]
):
    return await upload_my_studybook_by_pdf_usecase(file, current_user,
                                                    db)
@router.post("/upload-my-studybook-by-img", response_model=UploadStudybookResponseDTO)
async def upload_my_studybook_by_img(
    file: UploadFile = File(...),
    *,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)]
):
    return await upload_my_studybook_by_img_usecase(file, current_user, db)
@router.get("/my_studybook", response_model=MyStudybookResponseDTO)
async def my_studybook(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)]
):
    return await get_my_studybooks_usecase(current_user, db)

@router.delete("/delete-my-studybook/{studybook_id}", response_model=DeleteStudybookResponseDTO)
async def delete_my_studybook(
    studybook_id: Annotated[int, Path()],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)]
):
    return await delete_my_studybook_usecase(studybook_id, current_user, db)


