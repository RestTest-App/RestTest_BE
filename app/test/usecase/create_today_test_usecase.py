from datetime import datetime, date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.utils.openai_helper import generate_today_questions
from domain.user.entity.certificate import Certificate
from domain.user.entity.user import User
from exception.client_exception import NotFoundException, ConflictException
from exception.server_exception import InternalServerErrorException
from domain.test.entity.today_test import TodayTest
from domain.test.entity.today_test_question import TodayTestQuestion
from app.utils.dto.success import created, ok
from domain.test.entity.user_today_test import UserTodayTest

async def submit_today_test_usecase(current_user: User, db: AsyncSession):
    user_id = current_user.id
    try:
        # 오늘 날짜의 user_today_test 가져오기
        today = datetime.utcnow().date()

        result = await db.execute(
            select(UserTodayTest)
            .where(UserTodayTest.user_id == user_id)
            .where(UserTodayTest.created_at >= today)
        )
        user_today_test = result.scalars().first()

        if not user_today_test:
            raise NotFoundException("오늘의 문제 응시 기록이 없습니다.")

        user_today_test.is_solved = True
        await db.commit()

        return ok(message="오늘의 문제 제출 완료")

    except NotFoundException:
        raise
    except Exception as e:
        await db.rollback()
        raise InternalServerErrorException(f"서버 오류: {str(e)}")


async def get_today_questions_usecase(current_user: User, db: AsyncSession):
    try:
        # 1. 오늘 날짜 기준 TodayTest 조회
        today = datetime.utcnow().date()
        result = await db.execute(
            select(TodayTest).where(
                TodayTest.created_at >= datetime(today.year, today.month, today.day)
            )
        )
        today_test = result.scalars().first()
        if not today_test:
            raise NotFoundException("오늘의 문제가 존재하지 않습니다.")

        # 2. UserTodayTest에서 해당 유저가 응시한 적 있는지 확인
        result = await db.execute(
            select(UserTodayTest).where(
                UserTodayTest.user_id == current_user.id,
                UserTodayTest.today_test_id == today_test.id
            )
        )
        user_today = result.scalars().first()
        is_solved = user_today.is_solved if user_today else False

        # 3. 오늘의 문제들 조회
        result = await db.execute(
            select(TodayTestQuestion).where(
                TodayTestQuestion.today_test_by_ai_id == today_test.id
            )
        )
        questions = result.scalars().all()

        return ok(
            data={
                "is_solved": is_solved,
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
            message="오늘의 문제 조회 성공"
        )
    except Exception as e:
        await db.rollback()
        raise InternalServerErrorException(f"서버 오류: {str(e)}")

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

        result = await db.execute(
            select(TodayTestQuestion)
            .where(TodayTestQuestion.today_test_by_ai_id == today_test.id)
        )
        questions = result.scalars().all()

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
