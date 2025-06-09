from sqlalchemy.orm import Session
from app.test.dto.response.create_today_questions_response import QuestionDTO
from exception.client_exception import (
    BadRequestException,
    NotFoundException,
    TooManyRequestsException
)
from exception.server_exception import (
    InternalServerErrorException,
    ServiceUnavailableException,
    GatewayTimeoutException
)
from exception.success import ok

async def create_today_questions_usecase(certificate_id: str, db: Session):
    try:
        if certificate_id != "244":
            raise NotFoundException("존재하지 않는 시험입니다.")

        # 추후에 수정
        mock_questions = [
            QuestionDTO(
                question_id="2352453",
                description="오늘의 문제에 해당하지 않는 것은?",
                description_detail="blabla~~",
                options=["안녕하세요", "감사합니다", "굿모닝", "좋은 아침"],
                answer=3,
                option_explanations=[
                    "안녕하세요는 좀 전에 나왔음",
                    "감사합니다는 아저씨 감사합니다에 나왔음",
                    "굿모닝은 나온 적 없음",
                    "좋은 아침은 굿모닝 대신 나왔음"
                ]
            ),
            QuestionDTO(
                question_id="34534522",
                description="오늘의 문제에 해당하지 않는 것은?",
                description_detail="blabla~~",
                options=["안녕하세요", "감사합니다", "굿모닝", "좋은 아침"],
                answer=3,
                option_explanations=[
                    "안녕하세요는 좀 전에 나왔음",
                    "감사합니다는 아저씨 감사합니다에 나왔음",
                    "굿모닝은 나온 적 없음",
                    "좋은 아침은 굿모닝 대신 나왔음"
                ]
            ),
        ]

        return ok(
            data={
                "question_count": len(mock_questions),
                "question": [q.dict() for q in mock_questions]
            },
            message="오늘의 문제 생성 성공"
        )

    except NotFoundException:
        raise
    except TooManyRequestsException:
        raise TooManyRequestsException("요청이 너무 많습니다. 잠시 후에 다시 시도해주세요.")
    except ServiceUnavailableException:
        raise ServiceUnavailableException("OpenAI 연결 실패")
    except GatewayTimeoutException:
        raise GatewayTimeoutException("OpenAI 응답시간 초과")
    except Exception:
        raise InternalServerErrorException("서버 오류")
