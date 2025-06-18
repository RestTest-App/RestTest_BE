from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.review.dto.response.review_note_list_response import ReviewNoteListResponseDto
from domain.review.service.review_note_test_service import ReviewNoteTestService


class ReviewNoteListUseCase:
    def __init__(
            self,
            service: ReviewNoteTestService = ReviewNoteTestService()
    ):
        self.service = service

    async def execute(
            self,
            db: AsyncSession,
            user_id: int,
            certificate_id: Optional[int] = None
    ) -> ReviewNoteListResponseDto:
        return await self.service.list_review_notes(db, user_id, certificate_id)