from sqlalchemy import func
from sqlalchemy.future import select
from domain.test.entity.exam import Exam
from domain.test.entity.question import Question
from domain.user.entity.user import User
from app.utils.dto.success import ok
from sqlalchemy.ext.asyncio import AsyncSession
from app.test.dto.response.exam_response_dto import ExamResponseDTO
from domain.test.repository.test_repository import TestRepository
from exception.client_exception import NotFoundException

async def get_test_mode_usecase(
    exam_id: int,
    current_user: User,
    db: AsyncSession
):
    result = await db.execute(
        select(Exam).where(Exam.id == exam_id)
    )
    exam = result.scalars().first()

    if not exam:
        raise NotFoundException("시험 정보를 찾을 수 없습니다.")

    result = await db.execute(
        select(Question).where(Question.exam_id == exam_id)
    )
    questions = result.scalars().all()

    question_list = [
        {
            "answer_rate": float(q.answer_rate) if q.answer_rate is not None else None,
            "section": q.section,
            "description": q.description,
            "description_detail": q.description_detail,
            "description_image": q.description_image,
            "options": q.options,
            "option_explanations": None  # GPT 해설 붙일 자리
        }
        for q in questions
    ]

    return ok(
        data={
            "pass_rate": float(exam.pass_rate) if exam.pass_rate is not None else None,
            "questions": question_list
        },
        message="시험 조회 성공"
    )

async def get_exam_list_by_certificate_id_usecase(certificate_id: int, db: AsyncSession):
    repo = TestRepository(db)
    exams = await repo.get_exams_by_certificate_id(certificate_id)

    if not exams:
        raise NotFoundException("해당 자격증에 대한 시험이 존재하지 않습니다.")

    exam_list = []

    for exam in exams:
        stmt = select(func.count()).where(Question.exam_id == exam.id)
        result = await db.execute(stmt)
        question_count = result.scalar_one()

        dto = ExamResponseDTO(
            id=exam.id,
            name=exam.name,
            year=exam.year,
            month=exam.month,
            trial=exam.trial,
            time=exam.time,
            pass_rate=exam.pass_rate,
            question_count=question_count
        )
        exam_list.append(dto.model_dump())

    return ok(data={"exams": exam_list}, message="시험 리스트 조회 성공")
