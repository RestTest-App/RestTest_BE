from sqlalchemy.orm import Session
from domain.studybook.entity.studybook import StudyBook
from domain.studybook.entity.studybook_question import StudyBookQuestion
from domain.user.entity.user import User
from exception.client_exception import (
    NotFoundException, ForbiddenException, BadRequestException
)
from exception.success import created, ok
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

async def register_studybook_question_usecase(
    study_book_id: int,
    payload: dict,
    current_user: User,
    db: Session
):
    """
    문제 등록

    예외:
    - 404: 문제집이 존재하지 않음
    - 403: 본인 문제집이 아님
    - 400: 필수 필드 누락
    """
    studybook = db.query(StudyBook).filter(StudyBook.id == study_book_id).first()

    if not studybook:
        raise NotFoundException("존재하지 않는 문제집입니다.")
    if studybook.user_id != current_user.id:
        raise ForbiddenException("접근 권한이 없습니다.")
    if not all(k in payload for k in ("description", "options", "answer")):
        raise BadRequestException("필수 값이 누락되었습니다.")

    new_question = StudyBookQuestion(
        study_book_id=study_book_id,
        description=payload["description"],
        options=payload["options"],
        answer=payload["answer"],
    )
    db.add(new_question)
    db.commit()
    db.refresh(new_question)

    return created(data={"question_id": new_question.id}, message="문제 등록 성공")



async def get_studybook_questions_usecase(
    studybook_id: int,
    current_user: User,
    db: AsyncSession  # 반드시 AsyncSession으로 타입 수정
):
    """
    문제집 내 문제 전체 조회

    예외:
    - 404: 문제집이 존재하지 않음
    - 403: 타인의 문제집에 접근
    """
    result = await db.execute(
        select(StudyBook).where(StudyBook.id == studybook_id)
    )
    studybook = result.scalars().first()

    if not studybook:
        raise NotFoundException("존재하지 않는 문제집입니다.")
    if studybook.user_id != current_user.id:
        raise ForbiddenException("접근 권한이 없습니다.")

    questions_result = await db.execute(
        select(StudyBookQuestion).where(StudyBookQuestion.study_book_id == studybook_id)
    )
    questions = questions_result.scalars().all()

    result = [
        {
            "question_id": q.id,
            "description": q.description,
            "options": q.options,
            "answer": q.answer,
            # "created_at": q.created_at
        }
        for q in questions
    ]

    return ok(data={"questions": result}, message="문제집 문제 목록 조회 성공")

async def delete_studybook_question_usecase(
    question_id: int,
    current_user: User,
    db: Session
):
    """
    특정 문제 삭제

    - 400: 잘못된 문제 ID입니다.
    - 403: 접근 권한이 없습니다.
    - 404: 존재하지 않는 문제입니다.
    - 200: 문제 삭제 성공
    """
    question = db.query(StudyBookQuestion).filter(
        StudyBookQuestion.id == question_id
    ).first()

    if not question:
        raise NotFoundException("존재하지 않는 문제입니다.")

    if question.studybook.user_id != current_user.id:
        raise ForbiddenException("접근 권한이 없습니다.")

    db.delete(question)
    db.commit()

    return ok(message="문제 삭제 성공")

async def update_studybook_question_usecase(
    question_id: int,
    payload: dict,
    current_user: User,
    db: Session
):
    """
    개별 문제 수정 API

    - 404: 존재하지 않는 문제입니다.
    - 403: 접근 권한 없음 (작성자가 아님)
    - 400: 입력 데이터 오류
    """
    question = db.query(StudyBookQuestion).filter(StudyBookQuestion.id == question_id).first()
    if not question:
        raise NotFoundException("존재하지 않는 문제입니다.")

    studybook = db.query(StudyBook).filter(StudyBook.id == question.study_book_id).first()
    if studybook.user_id != current_user.id:
        raise ForbiddenException("접근 권한이 없습니다.")

    try:
        question.description = payload.get("description", question.description)
        question.description_detail = payload.get("description_detail", question.description_detail)
        question.description_image = payload.get("description_image", question.description_image)
        question.options = payload.get("options", question.options)
        question.answer = payload.get("answer", question.answer)
        question.explanation = payload.get("explanation", question.explanation)
        question.option_explanations = payload.get("option_explanations", question.option_explanations)
    except Exception:
        raise BadRequestException("입력 데이터에 오류가 있습니다.")

    db.commit()
    return ok(message="문제가 성공적으로 수정되었습니다.")