from typing import List, Callable, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.review.dto.request.question_info import QuestionInfoResponseDto
from app.review.dto.response.exam_info import ExamInfo
from app.review.dto.response.exam_item_info import ExamItemInfo
from app.review.dto.response.question_info import QuestionInfo
from app.review.dto.response.review_note_detail_response import ReviewNoteDetailResponseDto
from app.review.dto.response.review_note_list_response import ReviewNoteListResponseDto
from domain.review.repository.review_note_test_repository import ReviewNoteTestRepository
from domain.test.repository.test_repository import TestRepository
from exception.client_exception import NotFoundException


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

    async def list_review_notes(
        self,
        db: AsyncSession,
        user_id: int,
        certificate_id: Optional[int]
    ) -> ReviewNoteListResponseDto:
        notes, categories = await self.review_repository.review_notes_info(db, user_id, certificate_id)

        if certificate_id is not None:
            selected = next((c for c in categories if c and True), categories[0])
        else:
            selected = categories[0] if categories else None

        exams = [
            ExamItemInfo(
                review_note_id = r.review_note_id,
                exam_id = r.exam_id,
                name = r.name,
                is_passed = r.is_passed,
                certificate = r.certificate,
                read_count = r.read_count,
                pass_rate = float(r.pass_rate)
            )
            for r in notes
        ]

        return ReviewNoteListResponseDto(
            category = categories,
            selected_category = selected or "",
            exams = exams
        )

    async def get_detail(
            self,
            db: AsyncSession,
            user_id: int,
            review_note_id: int
    ) -> ReviewNoteDetailResponseDto:
        master = await self.review_repository.get_master(db, user_id, review_note_id)
        if not master:
            raise NotFoundException(message="해당 복습노트를 찾을 수 없습니다.")

        (
            review_note_id, created_at,
            exam_id, name, year, month, trial, time, pass_rate,
            score, is_passed, solved_at,
            study_tracker_id
        ) = master

        q_rows = await self.review_repository.get_questions(db, study_tracker_id)
        questions = [
            QuestionInfo(
                question_id=r.question_id,
                answer_rate=float(r.answer_rate) if r.answer_rate is not None else 0.0,
                section=r.section,
                description=r.description,
                description_detail=r.description_detail,
                description_image=r.description_image,
                options=r.options,
                option_explanations=r.option_explanations,
                answer=r.answer,
                selected_answer=r.selected_answer,
                is_correct=r.is_correct
            )
            for r in q_rows
        ]

        exam = ExamInfo(
            exam_id=exam_id,
            name=name,
            year=year,
            month=month,
            trial=trial,
            time=time,
            pass_rate=float(pass_rate),
            score=score,
            is_passed=is_passed,
            solved_at=solved_at
        )

        return ReviewNoteDetailResponseDto(
            review_note_id=review_note_id,
            created_at=created_at,
            exam=exam,
            questions=questions
        )

