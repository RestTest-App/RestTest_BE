from sqlalchemy.orm import Session
from domain.user.entity.user import User
from exception.success import ok
from exception.client_exception import (
    BadRequestException, UnauthorizedException,
    NotFoundException, UnprocessableEntityException, TooManyRequestsException
)
from exception.server_exception import (
    InternalServerErrorException, BadGatewayException
)
import random
import time

async def create_ai_explanation_usecase(
    exam_id: str,
    db: Session,
    current_user: User
):
    try:
        if not current_user:
            raise UnauthorizedException("access token이 만료되었습니다.")

        if not exam_id:
            raise BadRequestException("request body 필드 확인이 필요합니다.")

        if exam_id != "VALID_EXAM_ID":
            raise NotFoundException("시험 또는 문제 정보를 찾을 수 없습니다.")

        if random.random() < 0.1:
            raise UnprocessableEntityException("해설을 생성할 수 없습니다.")

        if random.random() < 0.05:
            raise TooManyRequestsException("너무 많은 OpenAI API 요청이 발생했습니다.")
        
        if random.random() < 0.05:
            raise BadGatewayException("OpenAI API 서버 오류")

        time.sleep(1.2)
        explanation = "블라블라블라블라블라블라블라블라블라블라블라블라블라블라블라블라"

        return ok(
            message="AI 해설 생성 성공",
            data={"ai_explanation": explanation}
        )

    except (
        BadRequestException,
        UnauthorizedException,
        NotFoundException,
        UnprocessableEntityException,
        TooManyRequestsException,
        BadGatewayException,
    ):
        raise
    except Exception:
        raise InternalServerErrorException("서버 오류")
