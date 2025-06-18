from sqlalchemy.ext.asyncio import AsyncSession

from app.review.dto.response.review_note_detail_response import ReviewNoteDetailResponseDto
from domain.review.service.review_note_test_service import ReviewNoteTestService


class ReviewNoteDetailUseCase:
    def __init__(
            self,
            service: ReviewNoteTestService = ReviewNoteTestService()
    ):
        self.service = service

    async def execute(
        self,
        db: AsyncSession,
        user_id: int,
        review_note_id: int
    ) -> ReviewNoteDetailResponseDto:
        return await self.service.get_detail(db, user_id, review_note_id)