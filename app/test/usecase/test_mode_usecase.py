from sqlalchemy.orm import Session
from app.test.dto.response.test_mode_response import TestModeQuestionDTO
from exception.client_exception import BadRequestException, NotFoundException
from exception.server_exception import InternalServerErrorException
from exception.success import ok


async def test_mode_usecase(exam_id: str, db: Session):
    try:
        if not exam_id:
            raise BadRequestException("잘못된 요청입니다.")

        if exam_id != "VALID_EXAM_ID":
            raise NotFoundException("해당 시험을 찾을 수 없습니다.")

        mock_questions = [
            TestModeQuestionDTO(
                answer_rate=89.23,
                section="1과목",
                description="다음 중 수의 표현에 있어 진법에 대한 설명으로 옳지 않은 것은?",
                description_detail=None,
                description_image="https://...",
                options=[
                    "16진수는 0~9, A~F로 구성된다",
                    "각 자리수는 4비트로 표현된다",
                    "16진수는 이진수보다 효율적이다",
                    "문제가 복붙되었다"
                ]
            ),
        ]

        return ok(
            data={
                "pass_rate": 55.00,
                "questions": [q.dict() for q in mock_questions]
            },
            message="시험 조회 성공"
        )

    except BadRequestException:
        raise
    except NotFoundException:
        raise
    except Exception:
        raise InternalServerErrorException("서버 오류")
