from typing import Optional, Tuple, List, Any, Coroutine

from app.test.dto.response.answer_info import AnswerInfoDto
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
    ) -> tuple[int | Any, list[int], list[int | None]]:

        correct_answers = [question.answer for question in questions] # 정답 리스트

        correct_count = 0
        info_list: List[AnswerInfoDto] = [] # 문제별 답, 해설 dto 리스트

        for idx, question in enumerate(questions):
            # 사용자가 선택한 답 가져오기 (null -> None 처리)
            user_answer = user_answers[idx] if idx < len(user_answers) else None

            if user_answer is not None:
                max_option = len(question.options)
                if not (1 <= user_answer <= max_option):
                    raise BadRequestException(message="보기 범위를 벗어났습니다.")
                if user_answer == question.answer:
                    correct_count += 1

            info_list.append(AnswerInfoDto(
                answer=question.answer,
                option_explanation=question.option_explanations
            ))

        return correct_count, correct_answers, user_answers


    # 합불 결정
    @staticmethod
    async def pass_or_unpass(
            self, correct_count: int, total: int, pass_grade: int
    ) -> bool:
        return (correct_count / total) >= pass_grade