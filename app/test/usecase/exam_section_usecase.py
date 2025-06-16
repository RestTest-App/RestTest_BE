from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from app.test.dto.request.create_exam_section_request import CreateExamSectionRequest
from app.test.dto.response.create_exam_section_response import CreateExamSectionResponse
from domain.test.repository.test_repository import TestRepository
from domain.test.entity.exam_section import ExamSection
from domain.test.entity.exam import Exam
from exception.client_exception import NotFoundException
from app.test.dto.response.get_exam_section_response import GetExamSectionResponse

async def create_exam_section_usecase(
    request_dto: CreateExamSectionRequest,
    db: AsyncSession
) -> CreateExamSectionResponse:
    repo = TestRepository(db)

    # exam_id 존재 여부 확인
    exam = await db.get(Exam, request_dto.exam_id)
    if not exam:
        raise NotFoundException("존재하지 않는 시험입니다.")

    new_exam_section = ExamSection(
        name=request_dto.name,
        order=request_dto.order,
        exam_id=request_dto.exam_id
    )

    saved_exam_section = await repo.create_exam_section(new_exam_section)

    return CreateExamSectionResponse(exam_section_id=saved_exam_section.id)
async def create_exam_sections_usecase(
    request_dtos: List[CreateExamSectionRequest],
    db: AsyncSession
) -> List[CreateExamSectionResponse]:
    repo = TestRepository(db)
    responses = []

    for request_dto in request_dtos:
        exam = await db.get(Exam, request_dto.exam_id)
        if not exam:
            raise NotFoundException(f"존재하지 않는 시험입니다. exam_id={request_dto.exam_id}")

        new_exam_section = ExamSection(
            name=request_dto.name,
            order=request_dto.order,
            exam_id=request_dto.exam_id
        )

        saved_exam_section = await repo.create_exam_section(new_exam_section)
        responses.append(CreateExamSectionResponse(exam_section_id=saved_exam_section.id))

    return responses


async def get_exam_sections_by_exam_id_usecase(
    exam_id: int,
    db: AsyncSession
) -> list[GetExamSectionResponse]:
    repo = TestRepository(db)

    exam_sections = await repo.get_exam_sections_by_exam_id(exam_id)

    return [
        GetExamSectionResponse(
            exam_section_id=section.id,
            name=section.name,
            order=section.order
        )
        for section in exam_sections
    ]
