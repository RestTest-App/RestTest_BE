from pyexpat.errors import messages
from typing import Optional

from fastapi import APIRouter, Depends, Query
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.auth.dependency import get_current_user
from app.review.dto.request.add_review_note_test_request import AddReviewNoteTestRequestDto
from app.review.dto.response.get_review_rest_mode_response import GetReviewRestModeResponse
from app.review.dto.response.get_review_test_mode_response import GetReviewTestModeResponse
from app.review.dto.response.review_note_detail_response import ReviewNoteDetailResponseDto
from app.review.dto.response.review_note_list_response import ReviewNoteListResponseDto
from app.review.usecase.review_note_detail_usecase import ReviewNoteDetailUseCase
from app.review.usecase.review_note_list_usecase import ReviewNoteListUseCase
from app.review.usecase.review_note_test_usecase import ReviewNoteTestUseCase
from app.review.usecase.review_usecase import get_review_note_rest_mode_usecase, get_review_note_test_mode_usecase, delete_review_note_usecase
from app.utils.dto.success import ok
from database.dependency import get_db
from domain.user.entity import User

router = APIRouter()

# @router.post("/add-review-note-test-mode/{exam_id}", response_model=GetReviewTestModeResponse)
# async def add_review_note_test_mode(
#         exam_id: int,
#         request: ReviewTestModeRequest,
#         db: Session = Depends(get_db)
# ):
#     return add_review_note_test_mode_usecase(db, request, exam_id=exam_id)

# @router.get("/get-review-note-test-mode/{review_note_id}", response_model=GetReviewTestModeResponse)
# async def get_review_note_test_mode(review_note_id: int, db: Session = Depends(get_db)):
#     return get_review_note_test_mode_usecase(db, review_note_id=review_note_id)

@router.get("/get-review-note-rest-mode/{review_note_id}", response_model=GetReviewRestModeResponse)
async def get_review_note_rest_mode(review_note_id: int, db: Session = Depends(get_db)):
    return get_review_note_rest_mode_usecase(db, review_note_id=review_note_id)

@router.delete("/delete-review-note/{reviewNoteId}")
async def delete_review_note(reviewNoteId: int, db: Session = Depends(get_db)):
    return delete_review_note_usecase(db, review_note_id=reviewNoteId)

@router.post("/add-review-note-test-mode/{exam_id}", response_model=None)
async def add_review_note_test_mode(
        request: AddReviewNoteTestRequestDto,
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    usecase = ReviewNoteTestUseCase()
    await usecase.execute(
        request=request,
        user_id=user.id,
        db=db
    )
    return ok(data=None, message="복습노트 추가 성공")


@router.get("/get-review-note-list", response_model=ReviewNoteListResponseDto)
async def get_review_note_list(
    category: Optional[int] = Query(None),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    dto = await ReviewNoteListUseCase().execute(db, user.id, category)
    return ok(data=dto.model_dump(), message="복습노트 불러오기 성공")



@router.get("/get-review-note-test-mode/{review_note_id}", response_model=ReviewNoteDetailResponseDto)
async def get_review_note_test_mode(
    review_note_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    dto = await ReviewNoteDetailUseCase().execute(db, user.id, review_note_id)
    return ok(data=jsonable_encoder(dto), message="복습노트 조회 성공")