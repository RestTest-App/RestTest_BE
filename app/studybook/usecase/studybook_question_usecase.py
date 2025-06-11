from sqlalchemy.orm import Session
from domain.studybook.studybook_question.service.studybook_question_service import register_question
from app.studybook.dto.response.upload_studybook_response_dto import UploadStudybookResponseDTO
from domain.user.entity.user import User
from domain.studybook.entity.studybook import StudyBook
from exception.client_exception import (
    NotFoundException, BadRequestException
)
from exception.success import created

async def get_studybook_questions_usecase(
    studybook_id: int,
    current_user: User,
    db: Session
):
    """
    문제집 내 모든 문제 조회

    - 404: 존재하지 않는 문제집
    - 403: 타인의 문제집 접근 시
    """
    studybook = db.query(StudyBook).filter(StudyBook.id == studybook_id).first()

    if not studybook:
        raise NotFoundException("존재하지 않는 문제집입니다.")
    if studybook.user_id != current_user.id:
        raise ForbiddenException("접근 권한이 없습니다.")

    questions = (
        db.query(StudyBookQuestion)
        .filter(StudyBookQuestion.study_book_id == studybook_id)
        .all()
    )

    result = [
        {
            "question_id": q.id,
            "description": q.description,
            "options": q.options,
            "answer": q.answer,
            "created_at": q.created_at
        }
        for q in questions
    ]

    return ok(data={"questions": result}, message="문제집 문제 목록 조회 성공")

async def register_studybook_question_usecase(
    studybook_id: int,
    question_data: dict,
    current_user: User,
    db: Session
):
    """
    문제 등록 유즈케이스
    - 해당 문제집이 본인 소유인지 확인
    - 문제 저장
    - 성공 응답 반환
    """
    studybook = db.query(StudyBook).filter(
        StudyBook.id == studybook_id,
        StudyBook.user_id == current_user.id
    ).first()

    if not studybook:
        raise NotFoundException("해당 문제집을 찾을 수 없습니다.")

    if "description" not in question_data or "options" not in question_data or "answer" not in question_data:
        raise BadRequestException("문제 데이터 형식이 올바르지 않습니다.")

    question_data["study_book_id"] = studybook_id

    question = register_question(db, question_data)

    db.commit()

    return created(data={"question_id": question.id}, message="문제 등록 성공")
