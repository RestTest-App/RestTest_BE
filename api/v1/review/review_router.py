from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.review.dto.request.review_test_mode_request import ReviewTestModeRequest
from app.review.dto.response.get_review_note_list_response import GetReviewNoteListResponse
from app.review.dto.response.get_review_rest_mode_response import GetReviewRestModeResponse
from app.review.dto.response.get_review_test_mode_response import GetReviewTestModeResponse
from app.review.usecase.review_usecase import add_review_note_test_mode_usecase, get_review_note_list_usecase, \
    get_review_note_rest_mode_usecase, get_review_note_test_mode_usecase, delete_review_note_usecase
from core.dependency import get_db

router = APIRouter()

@router.post("/add-review-note-test-mode/{exam_id}", response_model=GetReviewTestModeResponse)
async def add_review_note_test_mode(
        exam_id: int,
        request: ReviewTestModeRequest,
        db: Session = Depends(get_db)
):
    return add_review_note_test_mode_usecase(db, request, exam_id=exam_id)

@router.get("/get-review-note-test-mode/{review_note_id}", response_model=GetReviewTestModeResponse)
async def get_review_note_test_mode(review_note_id: int, db: Session = Depends(get_db)):
    return get_review_note_test_mode_usecase(db, review_note_id=review_note_id)

@router.get("/get-review-note-rest-mode/{review_note_id}", response_model=GetReviewRestModeResponse)
async def get_review_note_rest_mode(review_note_id: int, db: Session = Depends(get_db)):
    return get_review_note_rest_mode_usecase(db, review_note_id=review_note_id)

@router.get("/get-review-note-list", response_model=GetReviewNoteListResponse)
async def get_review_note_list(db: Session = Depends(get_db)):
    return get_review_note_list_usecase(db, user_id=1)

@router.delete("/delete-review-note/{reviewNoteId}")
async def delete_review_note(reviewNoteId: int, db: Session = Depends(get_db)):
    return delete_review_note_usecase(db, review_note_id=reviewNoteId)
