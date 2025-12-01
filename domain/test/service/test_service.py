import json  # [필수] json 라이브러리 임포트
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

        correct_answers = [question.answer for question in questions]
        correct_count = 0
        info_list: List[AnswerInfoDto] = []
        per_question: List[Dict] = []

        for idx, question in enumerate(questions):
            user_answer = user_answers[idx] if idx < len(user_answers) else None

            options_data = question.options
            if isinstance(options_data, str):
                try:
                    options_data = json.loads(options_data)
                except:
                    options_data = {}  # 파싱 실패 시 빈 값

            # options가 None이면 빈 딕셔너리로
            if options_data is None:
                options_data = {}

            # None이 아닐 때만 범위 검사
            if user_answer is not None:
                # 파싱된 options_data의 길이를 체크합니다.
                if not (1 <= user_answer <= len(options_data)):
                    # 로깅을 위해 에러 메시지에 상세 내용 포함
                    raise BadRequestException(message=f"보기 범위를 벗어났습니다. (문제ID: {question.id}, 입력: {user_answer})")

                is_correct = (user_answer == question.answer)
            else:
                is_correct = False

            if is_correct:
                correct_count += 1

            # [수정 2] option_explanations 데이터 파싱 (문자열 -> 딕셔너리)
            # 아까 발생했던 500 에러("str object has no attribute items") 해결 부분
            raw_explanations = question.option_explanations

            if raw_explanations is None:
                option_explanations_dict = {}
            elif isinstance(raw_explanations, str):
                try:
                    option_explanations_dict = json.loads(raw_explanations)
                except json.JSONDecodeError:
                    option_explanations_dict = {}
            elif isinstance(raw_explanations, dict):
                option_explanations_dict = raw_explanations
            else:
                option_explanations_dict = {}

            # 문제별 해설 DTO 생성
            info_list.append(AnswerInfoDto(
                answer=question.answer,
                option_explanations=option_explanations_dict
            ))

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
        if total == 0: return False
        return (correct_count / total) >= pass_grade