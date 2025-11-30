from typing import Optional, List, Any, Dict
from app.test.dto.response.answer_info import AnswerInfoDto
from app.test.dto.response.section_info import SectionInfoDto
from domain.test.entity import Question
from exception.client_exception import BadRequestException


class TestService:

    # 사용자 정답지 채점
    @staticmethod
    async def check_user_submit(
            user_answers: List[Optional[int]],
            questions: List[Question]
    ) -> tuple[int | Any, list[int], list[int | None], list[dict]]:

        correct_answers = [question.answer for question in questions] # 정답 리스트
        correct_count = 0
        info_list: List[AnswerInfoDto] = [] # 문제별 답, 해설 dto 리스트
        per_question: List[Dict] = []

        for idx, question in enumerate(questions):
            # 답이 없으면 None 처리
            user_answer = user_answers[idx] if idx < len(user_answers) else None

            # None이 아닐 때만 범위 검사
            if user_answer is not None:
                if not (1 <= user_answer <= len(question.options)):
                    raise BadRequestException(message="보기 범위를 벗어났습니다.")
                is_correct = (user_answer == question.answer)
            else:
                is_correct = False

            # 정답 카운트
            if is_correct:
                correct_count += 1

            raw_list = question.option_explanations or []
            option_explanations_dict: dict[str, str] = {
                key: val
                for item in raw_list
                for key, val in item.items()
            }

            # 문제별 해설 DTO
            info_list.append(AnswerInfoDto(
                answer=question.answer,
                option_explanations=option_explanations_dict
            ))

            # 문제별 사용자 응답 기록
            per_question.append({
                "question_id": question.id,
                "selected_answer": user_answer,
                "is_correct": is_correct,
                "exam_section_id": question.exam_section_id,
            })

        return correct_count, correct_answers, info_list, per_question


    # 과목별 점수 및 통계
    @staticmethod
    async def section_status(
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
            correct_count: int, total: int, pass_grade: float
    ) -> bool:
        return (correct_count / total) >= pass_grade