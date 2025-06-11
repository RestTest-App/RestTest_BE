from typing import Type
from datetime import datetime,UTC
from sqlalchemy.orm import Session, Query
from domain.review.entity.review_note_by_test import ReviewNoteByTest


class ReviewNoteRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_review_test_mode(self) -> Query[Type[ReviewNoteByTest]]:
        return self.db.query(ReviewNoteByTest)

    def create_review_note_test_mode(self, user_id:int, study_tracker_id:int):
        review_note = ReviewNoteByTest(
            created_at=datetime.now(UTC),
            user_id = user_id,
            study_tracker_id = study_tracker_id,
        )

        self.db.add(review_note)
        self.db.commit()
        self.db.refresh(review_note)
        return review_note