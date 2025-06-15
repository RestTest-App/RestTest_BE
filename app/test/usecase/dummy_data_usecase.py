from app.test.dto.request.create_dummy_data_request import CreateDummyDataRequest
from sqlalchemy.ext.asyncio import AsyncSession
from domain.test.repository.test_repository import TestRepository
from domain.user.entity.certificate import Certificate
from domain.test.entity.exam import Exam
from domain.test.entity.exam_section import ExamSection
from domain.test.entity.question import Question
from sqlalchemy import delete
from domain.test.entity.question import Question
from domain.test.entity.exam_section import ExamSection
from domain.test.entity.exam import Exam
from domain.user.entity.certificate import Certificate

async def reset_dummy_data_usecase(db: AsyncSession):
    await db.execute(delete(Question))
    await db.execute(delete(ExamSection))
    await db.execute(delete(Exam))
    await db.execute(delete(Certificate))

    await db.commit()

    return {"message": "Dummy data 초기화 완료"}

async def create_dummy_data_usecase(
    request_dto: CreateDummyDataRequest,
    db: AsyncSession
):
    repo = TestRepository(db)

    # Certificate 조회 or 생성
    existing_certificate = await repo.get_certificate_by_name(request_dto.certificate_name)
    if existing_certificate:
        saved_certificate = existing_certificate
    else:
        certificate = Certificate(name=request_dto.certificate_name)
        saved_certificate = await repo.create_certificate(certificate)

    # Exam 생성
    saved_exam_ids = []
    for exam_name in request_dto.exam_names:
        exam = Exam(
            name=exam_name,
            pass_rate=request_dto.pass_rate,
            year=2025,
            month=6,
            trial=None,
            time=request_dto.exam_time,
            certificate_id=saved_certificate.id
        )
        saved_exam = await repo.create_exam(exam)
        saved_exam_ids.append(saved_exam.id)

        # ExamSection → RequestBody 기준으로 생성
        saved_exam_sections = []

        for idx, name in enumerate(request_dto.section_names):
            section = ExamSection(
                name=name,
                order=idx + 1,
                exam_id=saved_exam.id
            )
            saved_section = await repo.create_exam_section(section)
            saved_exam_sections.append(saved_section)

        # Questions → RequestBody.questions_per_section 기준으로 생성
        for section in saved_exam_sections:
            for i in range(request_dto.questions_per_section):
                question = Question(
                    section=section.name,
                    description=f"{section.name} 더미 문제 {i+1}",
                    description_detail=f"{section.name} 더미 문제 상세 설명 {i+1}",
                    description_image=None,
                    options=["옵션1", "옵션2", "옵션3", "옵션4"],
                    answer=1,
                    option_explanations=["설명1", "설명2", "설명3", "설명4"],
                    exam_id=saved_exam.id,
                    exam_section_id=section.id
                )
                await repo.create_question(question)

    return {
        "certificate_id": saved_certificate.id,
        "exam_ids": saved_exam_ids
    }
