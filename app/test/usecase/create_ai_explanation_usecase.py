from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from domain.test.entity.question import Question
from domain.test.entity.exam import Exam
from app.utils.openai_helper import generate_option_explanations
from exception.client_exception import NotFoundException
from app.utils.dto.success import created, ok
async def create_ai_explanation_usecase(exam_id: int, db: AsyncSession):
    exam = await db.get(Exam, exam_id)
    if not exam:
        raise NotFoundException("해당 시험을 찾을 수 없습니다.")

    result = await db.execute(select(Question).where(Question.exam_id == exam_id))
    questions = result.scalars().all()

    for q in questions:
        q.option_explanations = await generate_option_explanations({
            "description": q.description,
            "options": q.options
        })

    await db.commit()

    return ok(
        message="AI 해설 생성 성공",
        data={
            "questions": [
                {
                    "id": q.id,
                    "description": q.description,
                    "options": q.options,
                    "option_explanations": q.option_explanations
                }
                for q in questions
            ]
        }
    )
