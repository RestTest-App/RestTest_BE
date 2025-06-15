from sqlalchemy.ext.asyncio import AsyncSession
from app.test.dto.response.get_certificates_exam_list_response import GetCertificatesExamListResponse, CertificateExamResponse, ExamItemResponse, PaginationResponse
from domain.test.repository.test_repository import TestRepository
from domain.user.entity.certificate import Certificate
from domain.test.entity.exam import Exam
from sqlalchemy import select, func
from app.test.dto.response.get_exam_info_response import GetExamInfoResponse
from app.test.dto.request.create_exam_request import CreateExamRequest
from app.test.dto.response.create_exam_response import CreateExamResponse

async def create_exam_usecase(
    request: CreateExamRequest,
    db: AsyncSession
) -> CreateExamResponse:
    repo = TestRepository(db)

    # Exam 생성
    exam = Exam(
        name=request.name,
        pass_rate=request.pass_rate,
        year=request.year,
        month=request.month,
        time=request.time,
        certificate_id=request.certificate_id
    )
    saved_exam = await repo.create_exam(exam)

    return CreateExamResponse(
        exam_id=saved_exam.id
    )

async def get_exam_info_usecase(
    exam_id: int,
    db: AsyncSession
) -> GetExamInfoResponse:
    repo = TestRepository(db)

    exam = await repo.get_exam_by_id(exam_id)
    if exam is None:
        # 그냥 빈 응답 or 404 처리 원하는 경우 여기서 처리 가능 (지금은 Exception 안 쓸 거라면 pass)
        return None

    question_count = await repo.get_question_count_by_exam_id(exam.id)

    return GetExamInfoResponse(
        year=exam.year,
        month=exam.month,
        name=exam.name,
        question_count=question_count,
        time=exam.time,
        exam_attempt=exam.trial if exam.trial is not None else 0,
        pass_rate=exam.pass_rate if exam.pass_rate is not None else 0.0
    )

async def get_certificates_exam_list_usecase(
    offset: int,
    limit: int,
    db: AsyncSession
) -> GetCertificatesExamListResponse:
    repo = TestRepository(db)

    # Certificate 전체 목록 조회 + pagination 적용
    result = await db.execute(
        select(Certificate)
        .order_by(Certificate.id)
        .offset(offset)
        .limit(limit)
    )
    certificates = result.scalars().all()

    total_count_result = await db.execute(
        select(func.count()).select_from(Certificate)
    )
    total_count = total_count_result.scalar()

    certificate_ids = [c.id for c in certificates]

    # Exam 전체 조회 (certificate_id in (certificate_ids))
    exams = await repo.get_exams_by_certificate_ids(certificate_ids)

    # certificate_id -> exams mapping 구성
    exam_map = {cid: [] for cid in certificate_ids}

    for exam in exams:
        question_count = await repo.get_question_count_by_exam_id(exam.id)
        exam_item = ExamItemResponse(
            exam_id=exam.id,
            exam_name=exam.name,
            question_count=question_count,
            exam_time=exam.time,
            pass_rate=exam.pass_rate
        )
        exam_map[exam.certificate_id].append(exam_item)

    # CertificateExamResponse 구성
    certificate_exam_responses = []

    for certificate in certificates:
        certificate_exam_responses.append(
            CertificateExamResponse(
                certificate_id=certificate.id,
                certificate_name=certificate.name,
                exams=exam_map.get(certificate.id, [])
            )
        )

    next_page = (offset + limit) < total_count

    pagenation = PaginationResponse(
        offset=offset,
        limit=limit,
        total_count=total_count,
        next_page=next_page
    )

    return GetCertificatesExamListResponse(
        goal=None,
        archive=None,
        certificates=certificate_exam_responses,
        pagenation=pagenation
    )

