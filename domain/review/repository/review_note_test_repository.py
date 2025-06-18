from datetime import datetime
from typing import Tuple, List, Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from domain.review.entity import ReviewNoteByTest
from domain.test.entity import Exam, TestTracker, Question, UserQuestionTracker
from domain.user.entity import Certificate, UserCertificate


class ReviewNoteTestRepository:

    @staticmethod
    async def add_review_note(db: AsyncSession, user_id: int, study_tracker_id: int) -> ReviewNoteByTest:
        review = ReviewNoteByTest(
            user_id=user_id,
            study_tracker_id=study_tracker_id,
            created_at = datetime.now()

        )
        db.add(review)
        await db.commit()
        await db.refresh(review)

    @staticmethod
    async def review_notes_info(
            db: AsyncSession,
            user_id: int,
            certificate_id: Optional[int] = None
    ) -> Tuple[List[tuple], List[str]]:
        cat_stmt = (
            select(Certificate.name)
            .select_from(UserCertificate)
            .join(Certificate, UserCertificate.certificate_id == Certificate.id)
            .where(UserCertificate.user_id == user_id)
        )
        cat_res = await db.execute(cat_stmt)
        categories = [row[0] for row in cat_res.all()]

        notes_stmt = (
            select(
                ReviewNoteByTest.id.label("review_note_id"),
                Exam.id.label("exam_id"),
                Exam.name,
                TestTracker.is_passed,
                Certificate.name.label("certificate"),
                func.count(ReviewNoteByTest.id).label("read_count"),
                (Exam.pass_rate * 100).label("pass_rate")
            )
            .select_from(ReviewNoteByTest)
            .join(TestTracker, ReviewNoteByTest.study_tracker_id == TestTracker.id)
            .join(Exam, TestTracker.exam_id == Exam.id)
            .join(Certificate, Exam.certificate_id == Certificate.id)
            .where(ReviewNoteByTest.user_id == user_id)
        )
        if certificate_id is not None:
            notes_stmt = notes_stmt.where(Exam.certificate_id == certificate_id)

        notes_stmt = notes_stmt.group_by(ReviewNoteByTest.id).order_by(ReviewNoteByTest.created_at.desc())

        notes_res = await db.execute(notes_stmt)
        notes = notes_res.all()

        return notes, categories


    @staticmethod
    async def get_master(
        db: AsyncSession,
        user_id: int,
        review_note_id: int
    ) -> Optional[tuple]:
        stmt = (
            select(
                ReviewNoteByTest.id.label("review_note_id"),
                ReviewNoteByTest.created_at,
                Exam.id.label("exam_id"),
                Exam.name,
                Exam.year,
                Exam.month,
                Exam.trial,
                Exam.time,
                Exam.pass_rate,
                TestTracker.score,
                TestTracker.is_passed,
                TestTracker.solved_at,
                TestTracker.id.label("study_tracker_id")
            )
            .join(TestTracker, ReviewNoteByTest.study_tracker_id == TestTracker.id)
            .join(Exam, TestTracker.exam_id == Exam.id)
            .where(
                ReviewNoteByTest.user_id == user_id,
                ReviewNoteByTest.id == review_note_id
            )
        )
        res = await db.execute(stmt)
        return res.first()


    @staticmethod
    async def get_questions(
        db: AsyncSession,
        study_tracker_id: int
    ) -> List[tuple]:
        stmt = (
            select(
                Question.id.label("question_id"),
                Question.answer_rate,
                Question.section,
                Question.description,
                Question.description_detail,
                Question.description_image,
                Question.options,
                Question.option_explanations,
                Question.answer,
                UserQuestionTracker.selected_answer,
                UserQuestionTracker.is_correct
            )
            .join(UserQuestionTracker, UserQuestionTracker.question_id == Question.id)
            .where(UserQuestionTracker.study_tracker_id == study_tracker_id)
        )
        res = await db.execute(stmt)
        return res.all()