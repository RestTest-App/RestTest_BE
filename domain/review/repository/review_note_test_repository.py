from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from domain.review.entity import ReviewNoteByTest


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