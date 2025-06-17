from typing import List, Callable

from sqlalchemy.ext.asyncio import AsyncSession

from app.review.dto.request.question_info import QuestionInfoResponseDto
from domain.review.repository.review_note_test_repository import ReviewNoteTestRepository
from domain.test.repository.test_repository import TestRepository


class QuestionInfoRequestDto:
    pass


class ReviewNoteTestService:
    def __init__(
            self,
            review_repository: ReviewNoteTestRepository = ReviewNoteTestRepository(),
            tracker_repository: Callable[[AsyncSession], TestRepository] = TestRepository,
    ):
        self.review_repository = review_repository
        self.tracker_repository = tracker_repository

    async def add_review_note_test(
            self,
            db: AsyncSession,
            user_id: int,
            question_list: list[QuestionInfoRequestDto]
    ) -> None:
        tracker_repo = TestRepository(db)
        for q in question_list:
            await self.review_repository.add_review_note(db, user_id, q.test_tracker_id)
            await tracker_repo.add_question_to_review(
                study_tracker_id=q.test_tracker_id,
                question_id=q.question_id,
                add_to_review=True
            )


