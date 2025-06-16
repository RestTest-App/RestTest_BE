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
    async def get_test_correct_answer(self, exam_id: int) -> Sequence[Question]:
        result = await self.db.execute(
            select(Question).where(Question.exam_id == exam_id).order_by(Question.id)
        )
        return result.scalars().all()


    # test tracker 등록
    async def create_user_test_tracker(self, user_id: int, exam_id: int, is_passed: bool, correct_count: int, total_count: int, solved_at: datetime) -> TestTracker:
        test_score = int((correct_count / total_count) * 100)
        result = await self.db.execute(
            insert(TestTracker).values(
                user_id=user_id,
                exam_id=exam_id,
                is_passed=is_passed,
                score=test_score,
                solved_at=solved_at
            )
        )
        tracker_id = result.inserted_primary_key[0]
        await self.db.commit()
        await self.db.refresh(tracker_id)
        return TestTracker(
            id=tracker_id,
            exam_id=exam_id,
            user_id=user_id,
            is_passed=is_passed,
            score=test_score,
            solved_at=solved_at
        )


    # question trakcer 등록하기
    async def create_user_question_tracker(
            self,
            test_tracker_id: int,
            records: List[Dict],
    ) -> None:
        await self.db.execute(insert(UserQuestionTracker), records)
        await self.db.commit()
        await self.db.refresh(test_tracker_id)


    # section 불러오기
    async def get_section_names(self, section_ids: List[int]) -> Dict[int, str]:
        result = await self.db.execute(
            select(ExamSection).where(ExamSection.id.in_(section_ids))
        )
        sections = result.scalars().all()
        return {section.id: section.name for section in sections}