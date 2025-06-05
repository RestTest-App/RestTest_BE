from sqlalchemy.orm import Session
from app.test.dto.request.submit_test_request import SubmitTestRequest
from app.test.dto.response.submit_test_response import SubmitTestResponse
from domain.user.entity.user import User
from domain.test.entity.exam import Exam
from domain.test.entity.question import Question
from domain.test.entity.test_tracker import TestTracker
from exception.client_exception import BadRequestException, NotFoundException
from exception.server_exception import InternalServerErrorException
from exception.success import ok
from datetime import datetime


async def submit_test_usecase(test_id: str, request: SubmitTestRequest, db: Session, current_user: User):
    try:
        exam = db.query(Exam).filter(Exam.id == test_id).first()
        if not exam:
            raise NotFoundException("해당 시험을 찾을 수 없습니다.")

        questions = db.query(Question).filter(
            Question.exam_id == exam.id).order_by(Question.id).all()
        if not questions:
            raise InternalServerErrorException("시험 문제를 불러오지 못했습니다.")

        answers = request.answers
        if len(answers) != len(questions):
            raise BadRequestException("답안 수가 일치하지 않습니다.")

        correct_count = 0
        correct_answers = []
        correct_answer_info_list = []

        for idx, question in enumerate(questions):
            correct_answer = question.answer
            user_answer = answers[idx]
            correct_answers.append(correct_answer)

            is_correct = (
                user_answer is not None and user_answer == correct_answer)
            if is_correct:
                correct_count += 1

            correct_answer_info_list.append({
                "answer": correct_answer,
                "description": question.description,
                "option_explanations": question.option_explanations
            })

        total_count = len(questions)
        pass_rate = float(exam.pass_rate or 0.6)
        is_passed = correct_count / total_count >= pass_rate

        tracker = TestTracker(
            user_id=current_user.id,
            test_id=exam.id,
            correct_count=correct_count,
            total_count=total_count,
            is_passed=is_passed,
            solved_at=datetime.utcnow()
        )
        db.add(tracker)
        db.commit()
        db.refresh(tracker)

        return ok(
            message="시험 제출 성공",
            data={
                "test_log": {
                    "test_tracker_id": tracker.id,
                    "is_passed": is_passed,
                    "solved_at": tracker.solved_at,
                    "correct_count": correct_count,
                    "total_count": total_count
                },
                "correct_answer": correct_answers,
                "correct_answer_info": correct_answer_info_list
            }
        )

    except (BadRequestException, NotFoundException):
        raise
    except Exception:
        raise InternalServerErrorException("서버 오류")
