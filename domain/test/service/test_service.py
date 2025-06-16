from typing import Optional, Tuple, List, Any, Coroutine, Dict

from typing_inspection.typing_objects import is_concatenate

from app.test.dto.response.answer_info import AnswerInfoDto
from app.test.dto.response.section_info import SectionInfoDto
from domain.test.entity import Question
from exception.client_exception import BadRequestException


class TestService:
    def __init__(self):
        pass

    # 사용자 정답지 채점
    @staticmethod
    async def check_user_submit(
            self,
            user_answers: List[Optional[int]],
            questions: List[Question]
    ) -> tuple[int | Any, list[int], list[int | None], list[dict]]:

        correct_answers = [question.answer for question in questions] # 정답 리스트

        correct_count = 0
        info_list: List[AnswerInfoDto] = [] # 문제별 답, 해설 dto 리스트
        per_question: List[Dict] = []

        for idx, question in enumerate(questions):
            # 사용자가 선택한 답 가져오기 (null -> None 처리)
            user_answer = user_answers[idx] if idx < len(user_answers) else None
            is_correct = (user_answer is not None and user_answer == question.answer)

            if not (1 <= user_answer <= len(question.options)):
                raise BadRequestException(message="보기 범위를 벗어났습니다.")

            if is_correct:
                correct_count += 1

            info_list.append(AnswerInfoDto(
                answer=question.answer,
                option_explanation=question.option_explanations
            ))

            per_question.append({
                "question_id": question.id,
                "selected_answer": user_answer,
                "is_correct": is_correct,
                "exam_section_id": question.exam_section_id,
            })

        return correct_count, correct_answers, user_answers, per_question


    # 과목별 점수 및 통계
    @staticmethod
    async def section_status(
            self,
            per_question: List[dict],
            section_names: Dict[int, str],
    ) -> List[SectionInfoDto]:

        status: Dict[int, List[int]] = {}
        for record in per_question:
            section_id = record["exam_section_id"]
            status.setdefault(section_id, [0, 0])[1] += 1
            if record["is_correct"]:
                status[section_id][0] += 1

        result: List[SectionInfoDto] = []
        for section_id, (correct, total) in status.items():
            result.append(SectionInfoDto(
                section_name=section_names.get(section_id),
                correct_count=correct,
                total_count=total,
                score=(correct / total) * 100
            ))

        return result


    # 합불 결정
    @staticmethod
    async def pass_or_unpass(
            self, correct_count: int, total: int, pass_grade: int
    ) -> bool:
        return (correct_count / total) >= pass_grade