from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from app.test.dto.response.rest_mode_response import RestModeQuestionDTO
from exception.client_exception import BadRequestException
from exception.server_exception import InternalServerErrorException
from exception.success import ok
from domain.test.entity.question import Question
import random


async def rest_mode_usecase(question_count: int, db: Session):
    try:
        if question_count <= 0 or question_count > 100:
            raise BadRequestException("잘못된 요청입니다.")

        max_id = db.query(func.max(Question.id)).scalar()
        if max_id is None:
            raise InternalServerErrorException("서버 오류")

        sampled_ids = set()
        while len(sampled_ids) < question_count:
            rand_id = random.randint(1, max_id)
            sampled_ids.add(rand_id)

        questions = db.query(Question).filter(
            Question.id.in_(sampled_ids)).limit(question_count).all()

        dto_list = [
            RestModeQuestionDTO(
                question_id=q.id,
                answer_rate=q.answer_rate,
                section=q.section,
                description=q.description,
                description_detail=q.description_detail,
                description_image=q.description_image,
                options=q.options,
                answer=q.answer,
                option_explanations=q.option_explanations
            ) for q in questions
        ]

        return ok(
            message="쉬엄모드 문제 조회 성공",
            data={
                "question_count": len(dto_list),
                "questions": [dto.dict() for dto in dto_list]
            }
        )

    except BadRequestException:
        raise
    except Exception:
        raise InternalServerErrorException("서버 오류")
