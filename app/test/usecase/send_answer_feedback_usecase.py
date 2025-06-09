from sqlalchemy.orm import Session
from app.test.dto.request.send_answer_feedback_request import SendAnswerFeedbackRequest
from domain.test.entity.feedback import Feedback

from exception.client_exception import BadRequestException
from exception.server_exception import InternalServerErrorException
from exception.success import ok


async def send_answer_feedback_usecase(db: Session, request: SendAnswerFeedbackRequest):
    if not request.test_id or not request.question_id or not request.ai_explanation or not request.feedback:
        raise BadRequestException("누락된 필드가 존재합니다.")

    try:
        feedback = Feedback(
            test_id=request.test_id,
            question_id=request.question_id,
            ai_explanation=request.ai_explanation,
            feedback=request.feedback
        )
        db.add(feedback)
        db.commit()
        db.refresh(feedback)

        return ok(
            data=None,
            message="피드백이 성공적으로 제출되었습니다."
        )

    except Exception:
        db.rollback()
        raise InternalServerErrorException("서버 오류")
