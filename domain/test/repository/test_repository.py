from datetime import datetime
from typing import Sequence, Dict, List
from sqlalchemy import select
from sqlalchemy.dialects.mysql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from domain.test.entity import Question, TestTracker, UserQuestionTracker, ExamSection
from domain.test.entity.exam import Exam


class TestRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    def create_test(self, name: str) -> Exam:
        test = Exam(name=name)
        self.db.add(test)
        self.db.commit()
        self.db.refresh(test)
        return test

    def get_test_all(self) -> list[Exam]:
        return self.db.query(Exam).all()

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