from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.orm import Session
from core.dependency import get_db
from app.test.dto.request.test_request import TestRequest
from app.test.dto.response.test_response import TestResponse
from app.test.usecase.test_usecase import create_test_usecae, get_tests_usecase
# 오늘의 문제
from app.test.dto.response.create_today_questions_response import CreateTodayQuestionsResponse
from app.test.usecase.create_today_questions_usecase import create_today_questions_usecase
# 문제 풀기 (시험 모드)
from app.test.usecase.test_mode_usecase import test_mode_usecase
from app.test.dto.response.test_mode_response import TestModeResponse
# 시험 결과 제출 (시험 모드)
from app.test.dto.request.submit_test_request import SubmitTestRequest
from app.test.dto.response.submit_test_response import SubmitTestResponse
from app.test.usecase.submit_test_usecase import submit_test_usecase
from domain.user.entity.user import User
from core.auth import get_current_user
# 문제 풀기 (쉬엄 모드)
from app.test.usecase.rest_mode_usecase import rest_mode_usecase
from app.test.dto.response.rest_mode_response import RestModeResponse
from core.dependency import get_db
# 문제 풀기 (오늘의 문제)
from domain.user.entity.user import User
from app.test.dto.response.today_questions_response import TodayQuestionsResponse
from app.test.usecase.today_questions_usecase import today_questions_usecase
# AI 해설 생성하기
from app.test.usecase.create_ai_explanation_usecase import create_ai_explanation_usecase
from app.test.dto.response.create_ai_explanation_response import CreateAIExplanationResponse
# 개발자에게 피드백 제출하기
from app.test.dto.request.send_answer_feedback_request import SendAnswerFeedbackRequest
from app.test.dto.response.send_answer_feedback_response import SendAnswerFeedbackResponse
from app.test.usecase.send_answer_feedback_usecase import send_answer_feedback_usecase

router = APIRouter(prefix="/test", tags=["test"])


@router.post("/", response_model=TestResponse)
def create_test(request: TestRequest, db: Session = Depends(get_db)):
    return create_test_usecae(db, request)


@router.get("/", response_model=list[TestResponse])
def get_tests(db: Session = Depends(get_db)):
    return get_tests_usecase(db)


# 오늘의 문제
@router.post("/create-today-questions/{certificate_id}", response_model=CreateTodayQuestionsResponse)
async def create_today_questions(
    certificate_id: str = Path(...),
    db: Session = Depends(get_db)
):
    return await create_today_questions_usecase(certificate_id, db)


# 문제 풀기 (시험 모드)
@router.get("/test-mode/{exam_id}", response_model=TestModeResponse)
async def test_mode(
    exam_id: str,
    db: Session = Depends(get_db)
):
    return await test_mode_usecase(exam_id, db)


# 시험 결과 제출 (시험 모드)
@router.post("/submit/{test_id}", response_model=SubmitTestResponse)
async def submit_test(
    test_id: str = Path(...),
    request: SubmitTestRequest = Depends(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await submit_test_usecase(test_id, request, db, current_user)


# 문제 풀기 (쉬엄 모드)
@router.get("/rest-mode/{question_count}", response_model=RestModeResponse)
async def get_relax_mode_questions(
    question_count: int = Path(...),
    db: Session = Depends(get_db)
):
    return await rest_mode_usecase(question_count, db)


# 문제 풀기 (오늘의 문제)
@router.get("/today-questions", response_model=TodayQuestionsResponse)
async def today_questions(
    certificate_id: str = Query(...),
    datetime: str = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await today_questions_usecase(certificate_id, datetime, db, current_user)


# AI 해설 생성하기
@router.post("/create-ai-explanations/{exam_id}", response_model=CreateAIExplanationResponse)
async def create_ai_explanation(
    exam_id: str = Path(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await create_ai_explanation_usecase(exam_id, db, current_user)


# 개발자에게 피드백 제출하기
@router.post("/send-answer-feedback", response_model=SendAnswerFeedbackResponse)
def send_answer_feedback(request: SendAnswerFeedbackRequest, db: Session = Depends(get_db)):
    return send_answer_feedback_usecase(db, request)
