from fastapi import APIRouter, Depends, Path, Body
from sqlalchemy.orm import Session
from database.dependency import get_db
from app.auth.dependency import get_current_user
from domain.user.entity.user import User
from app.studybook_question.usecase.studybook_question_usecase import (
    register_studybook_question_usecase,
    get_studybook_questions_usecase,
    delete_studybook_question_usecase,
    update_studybook_question_usecase
)


router = APIRouter()

@router.post("/{studybook_id}")
async def register_studybook_question(
    studybook_id: int = Path(..., description="문제집 ID"),
    payload: dict = Body(..., description="문제 등록 요청 데이터"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return await register_studybook_question_usecase(
        studybook_id=studybook_id,
        payload=payload,
        current_user=current_user,
        db=db
    )


@router.get("/{studybook_id}")
async def get_studybook_questions(
    studybook_id: int = Path(..., description="문제집 ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return await get_studybook_questions_usecase(
        studybook_id=studybook_id,
        current_user=current_user,
        db=db
    )

@router.delete("/{question_id}")
async def delete_studybook_question(
    question_id: int = Path(..., description="문제 ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return await delete_studybook_question_usecase(
        question_id=question_id,
        current_user=current_user,
        db=db
    )

@router.put("/{question_id}")
async def update_studybook_question(
    question_id: int = Path(..., description="문제 ID"),
    payload: dict = Body(..., description="문제 수정 요청 데이터"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return await update_studybook_question_usecase(
        question_id=question_id,
        payload=payload,
        current_user=current_user,
        db=db
    )