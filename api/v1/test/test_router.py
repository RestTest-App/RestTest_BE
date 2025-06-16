from fastapi import APIRouter, Depends, Path
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from app.test.dto.request.submit_test_request import SubmitTestRequestDTO
from app.test.dto.response.submit_test_response import SubmitTestResponseDTO
from database.dependency import get_db
from sqlalchemy.ext.asyncio import AsyncSession
# 오늘의 문제
# 문제 풀기 (시험 모드)
from app.test.usecase.test_mode_usecase import get_test_mode_usecase
from app.test.usecase.submit_test_usecase import SubmitTestUsecase
from app.auth.dependency import get_current_user
from app.test.usecase.rest_mode_usecase import rest_mode_usecase
from app.test.dto.response.rest_mode_response import RestModeResponse
from domain.user.entity.user import User
from exception.success import ok
# 문제, 시험 등록하기
from app.test.dto.request.create_exam_request import CreateExamRequest
from app.test.dto.response.create_exam_response import CreateExamResponse
from app.test.dto.request.create_question_request import CreateQuestionRequest
from app.test.dto.response.create_question_response import CreateQuestionResponse
from app.test.usecase.question_usecase import create_question_usecase
# 자격증 등록하기
from app.test.dto.request.create_certificate_request import CreateCertificateRequest
from app.test.dto.response.create_certificate_response import CreateCertificateResponse
from app.test.usecase.certificate_usecase import create_certificate_usecase
from app.test.dto.request.create_exam_section_request import CreateExamSectionRequest
from app.test.dto.response.create_exam_section_response import CreateExamSectionResponse
from app.test.usecase.exam_section_usecase import create_exam_section_usecase
from typing import List
from app.test.usecase.exam_section_usecase import create_exam_sections_usecase
from app.test.dto.response.get_exam_section_response import GetExamSectionResponse
from app.test.usecase.exam_section_usecase import get_exam_sections_by_exam_id_usecase
from app.test.dto.response.get_question_response import GetQuestionResponse
from app.test.usecase.question_usecase import get_questions_by_exam_id_usecase
#더미 데이터 생성
from app.test.usecase.dummy_data_usecase import create_dummy_data_usecase
from app.test.usecase.dummy_data_usecase import reset_dummy_data_usecase
from app.test.dto.request.create_dummy_data_request import CreateDummyDataRequest
#시험모드 문제 리스트 출력
from app.test.dto.response.get_certificates_exam_list_response import GetCertificatesExamListResponse
from app.test.usecase.exam_usecase import get_certificates_exam_list_usecase
from app.test.usecase.exam_usecase import create_exam_usecase
from app.test.usecase.exam_usecase import get_exam_info_usecase
#시험모드에서 문제 내용 받기
from app.test.usecase.test_usecase import get_test_mode_usecase
#ai 해설 추가하기 & 오늘의 문제 만들기
from app.test.usecase.create_ai_explanation_usecase import create_ai_explanation_usecase
from app.test.usecase.create_today_test_usecase import create_today_questions_usecase, get_today_questions_usecase, submit_today_test_usecase

#이메일 보내기
from app.test.usecase.send_feedback_usecase import send_feedback_usecase
from app.test.dto.request.feedback_request_dto import FeedbackRequestDTO

router = APIRouter()

# 오늘의 문제
@router.post("/create-today-questions/{certificate_id}", summary="오늘의 문제 생성 또는 불러오기")
async def create_today_questions(
    certificate_id: int = Path(..., description="자격증 ID"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await create_today_questions_usecase(
        certificate_id=certificate_id,
        current_user=current_user,
        db=db
    )

@router.get("/today-questions")
async def get_today_questions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await get_today_questions_usecase(current_user, db)

@router.post("/submit-today-test")
async def submit_today_test(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await submit_today_test_usecase(current_user, db)

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

# 시험 등록 API
@router.post("/exam", response_model=CreateExamResponse, summary="시험 등록 API")
async def create_exam(
    request: CreateExamRequest,
    db: AsyncSession = Depends(get_db)
):
    return await create_exam_usecase(request, db)

@router.get("/exam/{exam_id}/info", summary="시험 정보 조회 API")
async def get_exam_info(
    exam_id: int,
    db: AsyncSession = Depends(get_db)
):
    result = await get_exam_info_usecase(exam_id, db)
    return {
        "code": 200,
        "message": "시험 정보 조회 성공",
        "data": result
    }
# 문제 등록 API
@router.post("/exam/{exam_id}/question", response_model=CreateQuestionResponse, summary="문제 등록 API")
async def create_question(
    exam_id: int = Path(..., description="시험 ID"),
    request: CreateQuestionRequest = ...,
    db: AsyncSession = Depends(get_db)
):
    return await create_question_usecase(exam_id, request, db)

@router.post("/certificate", response_model=CreateCertificateResponse, summary="자격증 등록 API")
async def create_certificate(
    request: CreateCertificateRequest,
    db: AsyncSession = Depends(get_db)
):
    return await create_certificate_usecase(request, db)

@router.post("/exam-section", response_model=CreateExamSectionResponse, summary="과목 등록 API")
async def create_exam_section(
    request: CreateExamSectionRequest,
    db: AsyncSession = Depends(get_db)
):
    return await create_exam_section_usecase(request, db)


@router.post("/exam-sections", response_model=List[CreateExamSectionResponse], summary="과목 배치 등록 API")
async def create_exam_sections(
    request: List[CreateExamSectionRequest],
    db: AsyncSession = Depends(get_db)
):
    return await create_exam_sections_usecase(request, db)

@router.get("/exam/{exam_id}/exam-sections", response_model=list[GetExamSectionResponse], summary="과목 목록 조회 API")
async def get_exam_sections_by_exam_id(
    exam_id: int,
    db: AsyncSession = Depends(get_db)
):
    result = await get_exam_sections_by_exam_id_usecase(exam_id, db)
    return ok(data=[r.dict() for r in result], message="과목 목록 조회 성공")

@router.get("/exam/{exam_id}/questions", response_model=list[GetQuestionResponse], summary="문제 목록 조회 API")
async def get_questions_by_exam_id(
    exam_id: int,
    db: AsyncSession = Depends(get_db)
):
    result = await get_questions_by_exam_id_usecase(exam_id, db)
    return ok(data=[item.dict() for item in result], message="문제 목록 조회 성공")

@router.post("/dummy-data", summary="유형별 Dummy Data 생성 API")
async def create_dummy_data(
    request: CreateDummyDataRequest,   # ← 여기에 request 추가 필요!
    db: AsyncSession = Depends(get_db)
):
    result = await create_dummy_data_usecase(request, db)   # ← 여기에도 request 넣어서 호출
    return {
        "code": 200,
        "message": "Dummy data 생성 성공",
        "data": result
    }

@router.delete("/reset-dummy-data", summary="Dummy 데이터 초기화 API")
async def reset_dummy_data(
    db: AsyncSession = Depends(get_db)
):
    result = await reset_dummy_data_usecase(db)
    return {
        "code": 200,
        "message": result["message"]
    }

@router.get("/certificates/exams", response_model=GetCertificatesExamListResponse, summary="전체 자격증별 시험 목록 조회 API")
async def get_certificates_exam_list(
    offset: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
):
    return await get_certificates_exam_list_usecase(offset, limit, db)

@router.get("/test-mode/{exam_id}")
async def get_test_mode(
    exam_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await get_test_mode_usecase(exam_id, current_user, db)

@router.post("/create-ai-explanations/{exam_id}")
async def create_ai_explanation(
    exam_id: int = Path(...),
    db: AsyncSession = Depends(get_db),
):
    return await create_ai_explanation_usecase(exam_id, db)


@router.post("/submit-test/{exam_id}", response_model=SubmitTestResponseDTO)
async def submit_test(
        payload: SubmitTestRequestDTO,
        exam_id: int = Path(..., gt=0),
        db: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user)
):
    usecase = SubmitTestUsecase(db)

    result = await usecase.execute(user.id, exam_id, payload)
    safe_data = jsonable_encoder(result)
    return ok(data=safe_data, message="시험 제출 성공")
  

@router.post("/send-answer-feedback")
async def send_feedback(dto: FeedbackRequestDTO):
    return await send_feedback_usecase(dto)