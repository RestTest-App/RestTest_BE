from sqlalchemy.ext.asyncio import AsyncSession

from app.review.dto.request.add_review_note_test_request import AddReviewNoteTestRequestDto
from domain.review.service.review_note_test_service import ReviewNoteTestService


class ReviewNoteTestUseCase:

    def __init__(
            self,
            service: ReviewNoteTestService = ReviewNoteTestService()
    ):
        self.service = service

    async def execute(
            self,
            request: AddReviewNoteTestRequestDto,
            user_id: int,
            db: AsyncSession
    ) -> None:
        await self.service.add_review_note_test(
            db=db,
            user_id=user_id,
            question_list=request.question_list
        )
