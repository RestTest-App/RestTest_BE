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