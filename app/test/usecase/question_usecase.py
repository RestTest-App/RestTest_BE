from sqlalchemy.ext.asyncio import AsyncSession
from app.test.dto.request.create_question_request import CreateQuestionRequest
from app.test.dto.response.create_question_response import CreateQuestionResponse
from domain.test.entity.question import Question
from domain.test.repository.test_repository import TestRepository
from domain.test.entity.exam import Exam
from domain.test.entity.exam_section import ExamSection
from exception.client_exception import NotFoundException
from app.test.dto.response.get_question_response import GetQuestionResponse

async def get_questions_by_exam_id_usecase(
    exam_id: int,
    db: AsyncSession
) -> list[GetQuestionResponse]:
    repo = TestRepository(db)

    questions = await repo.get_questions_by_exam_id(exam_id)

    return [
        GetQuestionResponse(
            question_id=q.id,
            section=q.section,
            description=q.description,
            options=q.options,
            answer=q.answer,
            exam_section_id=q.exam_section_id
        )
        for q in questions
    ]

async def create_question_usecase(
    exam_id: int,
    request_dto: CreateQuestionRequest,
    db: AsyncSession
) -> CreateQuestionResponse:
    # Repository 인스턴스 생성
    repo = TestRepository(db)

    # exam_id 존재 여부 확인
    exam = await db.get(Exam, exam_id)
    if not exam:
        raise NotFoundException("존재하지 않는 시험입니다.")

    # exam_section_id 존재 여부 확인
    exam_section = await db.get(ExamSection, request_dto.exam_section_id)
    if not exam_section:
        raise NotFoundException("존재하지 않는 과목(ExamSection)입니다.")

    # Question 엔티티 생성
    new_question = Question(
        section=request_dto.section,
        description=request_dto.description,
        description_detail=request_dto.description_detail,
        description_image=request_dto.description_image,
        options=request_dto.options,
        answer=request_dto.answer,
        option_explanations=request_dto.option_explanations,
        exam_id=exam_id,
        exam_section_id=request_dto.exam_section_id
    )

    # Question 저장
    saved_question = await repo.create_question(new_question)

    # Response 반환
    return CreateQuestionResponse(question_id=saved_question.id)
