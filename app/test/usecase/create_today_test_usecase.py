from datetime import datetime, date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.utils.openai_helper import generate_today_questions
from domain.test.entity.today_test import TodayTest
from domain.test.entity.today_test_question import TodayTestQuestion
from domain.test.entity.user_today_test import UserTodayTest
from domain.user.entity.certificate import Certificate
from domain.user.entity.user import User
from exception.client_exception import NotFoundException, ConflictException
from exception.server_exception import InternalServerErrorException
from exception.success import ok

async def create_today_questions_usecase(certificate_id: int, current_user: User, db: AsyncSession):
    try:
        # 1. 자격증 존재 확인
        certificate = await db.get(Certificate, certificate_id)
        if not certificate:
            raise NotFoundException("존재하지 않는 시험입니다.")

        # 2. 오늘 날짜 기준으로 기존 TodayTest 존재 여부 확인
        today = date.today()
        result = await db.execute(
            select(TodayTest)
            .where(
                TodayTest.certificate_id == certificate_id,
                TodayTest.created_at >= datetime(today.year, today.month, today.day)
            )
        )
        today_test = result.scalars().first()

        # 3. 없으면 새로 생성
        if not today_test:
            questions_data = await generate_today_questions(certificate.name)
            today_test = TodayTest(
                created_at=datetime.utcnow(),
                certificate_id=certificate_id
            )
            db.add(today_test)
            await db.flush()  # today_test.id 확보

            for q in questions_data:
                db.add(TodayTestQuestion(
                    today_test_by_ai_id=today_test.id,
                    description=q["description"],
                    description_detail=q.get("description_detail"),
                    options=q["options"],
                    answer=q["answer"],
                    option_explanations=q["option_explanations"]
                ))

        # 4. 유저가 이미 응시했는지 확인
        result = await db.execute(
            select(UserTodayTest)
            .where(and_(
                UserTodayTest.user_id == current_user.id,
                UserTodayTest.today_test_id == today_test.id
            ))
        )
        existing_user_test = result.scalars().first()
        if existing_user_test:
            raise ConflictException("이미 오늘의 문제를 응시했습니다.")

        # 5. 유저-오늘의 시험 매핑 저장
        user_today_test = UserTodayTest(
            user_id=current_user.id,
            today_test_id=today_test.id,
            is_solved=False
        )
        db.add(user_today_test)

        # 6. 결과 반환용 문제 가져오기
        result = await db.execute(
            select(TodayTestQuestion)
            .where(TodayTestQuestion.today_test_by_ai_id == today_test.id)
        )
        questions = result.scalars().all()

        await db.commit()

        return ok(
            data={
                "question_count": len(questions),
                "question": [
                    {
                        "question_id": q.id,
                        "description": q.description,
                        "description_detail": q.description_detail,
                        "options": q.options,
                        "answer": q.answer,
                        "option_explanations": q.option_explanations
                    }
                    for q in questions
                ]
            },
            message="오늘의 문제 생성 성공"
        )

    except (NotFoundException, ConflictException):
        raise
    except Exception as e:
        await db.rollback()
        raise InternalServerErrorException(f"서버 오류: {str(e)}")
