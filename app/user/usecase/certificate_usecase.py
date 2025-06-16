from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from app.user.dto.response.certificates_response import CertificateResponseDto
from app.utils.dto.pagination import PaginationDto
from domain.user.repository.certificate_repository import CertificateRepository
from domain.user.service.certificate_service import CertificateService
from exception.client_exception import NotFoundException, BadRequestException


class CertificateUseCase:

    @staticmethod
    async def execute(db: AsyncSession, offset: int, limit: int) -> CertificateResponseDto:
        certificates, total = await CertificateService.fetch_certificates(db, offset, limit)

        if offset >= total:
            raise BadRequestException(message="더이상 불러올 내용이 없습니다.")

        pagination = PaginationDto(
            offset=offset,
            limit=limit,
            total_count=total,
            next_page=(offset + limit < total)
        )

        return CertificateResponseDto(
            certificates=certificates,
            pagination=pagination
        )