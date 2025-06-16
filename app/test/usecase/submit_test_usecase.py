from datetime import datetime, timezone, timedelta
from typing import Optional
from zoneinfo import ZoneInfo

from sqlalchemy.ext.asyncio import AsyncSession

from app.test.dto.request.submit_test_request import SubmitTestRequestDTO
from app.test.dto.response.submit_test_response import SubmitTestResponseDTO
from app.test.dto.response.test_log import TestLogDto
from domain.test.repository.test_repository import TestRepository
from domain.test.service.test_service import TestService


class SubmitTestUsecase:
    def __init__(self, db: AsyncSession):
        self.repository = TestRepository(db)
        self.service = TestService()

    # test 제출 버튼 클릭 시 로직
    async def execute(
            self,
            user_id: int,
            exam_id: int,
            payload: SubmitTestRequestDTO
    ) -> SubmitTestResponseDTO:

        # 문제 조회
        qustions = await self.repository.get_questions_from_exam(exam_id)
        total = len(qustions) # 총 문제 수

        # 채점 (맞은 문제 수, 정답 리스트, 문항별 답/해설 리스트, 과목별 정보)
        correct_count, correct_answer, info_list, per_question = await self.service.check_user_submit(
            user_answers=payload.answers,
            questions=qustions
        )

        # 합불
        is_passed = await self.service.pass_or_unpass(correct_count=correct_count, total=total)

        solved_at = datetime.now(ZoneInfo("Asia/Seoul"))

        #트래커 생성
        tracker = await self.repository.create_user_test_tracker(
            user_id=user_id,
            exam_id=exam_id,
            solved_at=solved_at,
            is_passed=is_passed,
            correct_count=correct_count,
            total_count=total
        )

        records = [
            {
                "study_tracker_id": tracker.id,
                "question_id": record["question_id"],
                "selected_answer": record["selected_answer"],
                "is_correct": record["is_correct"],
                "add_to_review": False,
            }
            for record in per_question
        ]

        await self.repository.create_user_question_tracker(tracker.id, records)

        # 과목별 통계 계산
        section_ids = {record["exam_section_id"] for record in per_question}
        section_names = await self.repository.get_section_names(list(section_ids))
        section_status = await self.service.section_status(per_question, section_names)

        # testlog DTO
        test_log = TestLogDto(
            test_tracker_id=tracker.id,
            is_passed=bool(is_passed),
            solved_at=tracker.solved_at,
            correct_count=correct_count,
            total_count=total
        )

        return SubmitTestResponseDTO(
            test_log=test_log,
            correct_answer=correct_answer,
            correct_answer_info=info_list,
            section_info=section_status
        )