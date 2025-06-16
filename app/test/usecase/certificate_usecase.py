from sqlalchemy.ext.asyncio import AsyncSession
from app.test.dto.request.create_certificate_request import CreateCertificateRequest
from app.test.dto.response.create_certificate_response import CreateCertificateResponse
from domain.test.repository.test_repository import TestRepository
from domain.user.entity.certificate import Certificate

async def create_certificate_usecase(
    request_dto: CreateCertificateRequest,
    db: AsyncSession
) -> CreateCertificateResponse:
    repo = TestRepository(db)

    new_certificate = Certificate(
        name=request_dto.name
    )

    saved_certificate = await repo.create_certificate(new_certificate)

    return CreateCertificateResponse(certificate_id=saved_certificate.id)
