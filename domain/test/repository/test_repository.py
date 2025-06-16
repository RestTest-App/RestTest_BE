
from datetime import datetime
from pyexpat.errors import messages
from typing import Sequence, Dict, List
from sqlalchemy import select
from sqlalchemy.dialects.mysql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from domain.test.entity import Question, TestTracker, UserQuestionTracker, ExamSection
from domain.test.entity.exam import Exam
from exception.client_exception import NotFoundException
from domain.test.entity.exam import Exam
from sqlalchemy.ext.asyncio import AsyncSession
from domain.test.entity.question import Question
from domain.user.entity.certificate import Certificate
from domain.test.entity.exam_section import ExamSection
from sqlalchemy import select
from sqlalchemy import func


class TestRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_test(self, name: str) -> Exam:
        test = Exam(name=name)
        self.db.add(test)
        await self.db.commit()
        await self.db.refresh(test)
        return test

    # 정답 불러오기 (시험모드)
    async def get_questions_from_exam(self, exam_id: int) -> List[Question]:
        result = await self.db.execute(
            select(Question).where(Question.exam_id == exam_id).order_by(Question.id)
        )
        return result.scalars().all()


    # test tracker 등록
    async def create_user_test_tracker(self, user_id: int, exam_id: int, is_passed: bool, correct_count: int, total_count: int, solved_at: datetime) -> TestTracker:
        test_score = int((correct_count / total_count) * 100)
        tracker = TestTracker(
            user_id=user_id,
            exam_id=exam_id,
            solved_at=solved_at,
            score=test_score,
            is_passed=is_passed
        )
        self.db.add(tracker)
        await self.db.commit()
        await self.db.refresh(tracker)
        return tracker


    # question trakcer 등록하기
    async def create_user_question_tracker(
            self,
            test_tracker_id: int,
            records: List[Dict],
    ) -> None:
        instances = [
            UserQuestionTracker(
                study_tracker_id=test_tracker_id,
                question_id=record["question_id"],
                selected_answer=record["selected_answer"],
                is_correct=record["is_correct"],
                add_to_review=False,
            )
            for record in records
        ]
        self.db.add_all(instances)
        await self.db.flush()



    # section 불러오기
    async def get_section_names(self, section_ids: List[int]) -> Dict[int, str]:
        result = await self.db.execute(
            select(ExamSection).where(ExamSection.id.in_(section_ids))
        )
        sections = result.scalars().all()
        return {section.id: section.name for section in sections}

    # 시험 가져오기
    async def get_exam(self, exam_id: int) -> Exam:
        result = await self.db.execute(
            select(Exam).where(Exam.id == exam_id)
        )
        exam: Exam | None = result.scalar_one_or_none()
        if exam is None:
            raise NotFoundException(message="시험을 찾을 수 없습니다.")
        return exam

    async def get_test_all(self) -> list[Exam]:
        result = await self.db.execute(select(Exam))
        return result.scalars().all()

    async def create_exam(self, exam: Exam) -> Exam:
        self.db.add(exam)
        await self.db.commit()
        await self.db.refresh(exam)
        return exam

    async def create_question(self, question: Question) -> Question:
        self.db.add(question)
        await self.db.commit()
        await self.db.refresh(question)
        return question

    async def create_certificate(self, certificate: Certificate) -> Certificate:
        self.db.add(certificate)
        await self.db.commit()
        await self.db.refresh(certificate)
        return certificate

    async def create_exam_section(self, exam_section: ExamSection) -> ExamSection:
        self.db.add(exam_section)
        await self.db.commit()
        await self.db.refresh(exam_section)
        return exam_section

    async def get_exam_sections_by_exam_id(self, exam_id: int) -> list[ExamSection]:
        result = await self.db.execute(
            select(ExamSection).where(ExamSection.exam_id == exam_id).order_by(ExamSection.order)
        )
        return result.scalars().all()

    async def get_questions_by_exam_id(self, exam_id: int) -> list[Question]:
        result = await self.db.execute(
            select(Question).where(Question.exam_id == exam_id).order_by(Question.id)
        )
        return result.scalars().all()

    async def get_exam_total_count(self, certificate_id: int) -> int:
        result = await self.db.execute(
            select(func.count()).select_from(Exam).where(Exam.certificate_id == certificate_id)
        )
        return result.scalar()

    async def get_question_count_by_exam_id(self, exam_id: int) -> int:
        result = await self.db.execute(
            select(func.count()).select_from(Question).where(Question.exam_id == exam_id)
        )
        return result.scalar()

    async def get_exams_by_certificate_ids(self, certificate_ids: list[int]) -> list[Exam]:
        result = await self.db.execute(
            select(Exam)
            .where(Exam.certificate_id.in_(certificate_ids))
            .order_by(Exam.year.desc(), Exam.month.desc(), Exam.trial.desc())
        )
        return result.scalars().all()

    async def get_certificate_by_name(self, name: str) -> Certificate | None:
        result = await self.db.execute(
            select(Certificate).where(Certificate.name == name)
        )
        return result.scalars().first()

    async def get_exam_by_id(self, exam_id: int) -> Exam | None:
        result = await self.db.execute(
            select(Exam).where(Exam.id == exam_id)
        )
        return result.scalars().first()