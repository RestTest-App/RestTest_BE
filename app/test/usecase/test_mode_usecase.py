from domain.user.entity.user import User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from domain.test.entity.exam import Exam
from domain.test.entity.question import Question
from exception.client_exception import NotFoundException
from exception.success import ok


async def get_test_mode_usecase(exam_id: int, current_user: User, db: AsyncSession):
    result = await db.execute(select(Exam).where(Exam.id == exam_id))
    exam = result.scalars().first()

    if not exam:
        raise NotFoundException("해당 시험을 찾을 수 없습니다.")

    result = await db.execute(
        select(Question).where(Question.exam_id == exam_id)
    )
    questions = result.scalars().all()

    return ok(
        data={
            "pass_rate": float(exam.pass_rate or 0.0),
            "questions": [
                {
                    "answer_rate": float(q.answer_rate or 0.0),
                    "section": q.section,
                    "description": q.description,
                    "description_detail": q.description_detail,
                    "description_image": q.description_image,
                    "options": q.options
                }
                for q in questions
            ]
        },
        message="시험 조회 성공"
    )
