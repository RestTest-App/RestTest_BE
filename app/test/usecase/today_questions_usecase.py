from sqlalchemy.orm import Session
from domain.user.entity.user import User
from app.test.dto.response.today_questions_response import TodayQuestionDTO
from exception.success import ok
from exception.client_exception import BadRequestException, UnauthorizedException, NotFoundException
from exception.server_exception import InternalServerErrorException
from datetime import datetime

async def today_questions_usecase(
    certificate_id: str,
    date_str: str,
    db: Session,
    current_user: User
):
    try:
        if not current_user:
            raise UnauthorizedException("access token이 만료되었습니다.")

        if not certificate_id or not date_str:
            raise BadRequestException("잘못된 요청입니다.")

        try:
            today = datetime.fromisoformat(date_str)
        except ValueError:
            raise BadRequestException("잘못된 날짜 형식입니다. (YYYY-MM-DD)")

        # 3. 문제 조회 (Mock)
        if certificate_id != "VALID_CERT_ID":
            raise NotFoundException("오늘의 문제를 찾을 수 없습니다.")

        # 실제로는 solved 여부는 DB 체크해야 함
        is_solved = False

        mock_questions = [
            TodayQuestionDTO(
                description="웃음소리가 아닌 것은?",
                description_detail=None,
                options=["하하", "호호", "히히", "음메"],
                answer=4,
                option_explanations=[
                    "하하는 웃음소리임",
                    "호호는 웃음소리임",
                    "히히는 웃음소리임",
                    "음메는 소 울음소리임"
                ]
            )
            for _ in range(10)
        ]

        return ok(
            message="오늘의 문제 불러오기 성공",
            data={
                "is_solved": is_solved,
                "question_count": len(mock_questions),
                "questions": [q.dict() for q in mock_questions]
            }
        )

    except (BadRequestException, UnauthorizedException, NotFoundException):
        raise
    except Exception:
        raise InternalServerErrorException("서버 오류")
