from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from app.user.dto.response.certificate import CertificateDto
from domain.user.repository.certificate_repository import CertificateRepository


class CertificateService:

    @staticmethod
    async def fetch_certificates(db: AsyncSession, offset: int, limit: int) -> (List[CertificateDto], int):
        certificates, total = await CertificateRepository.get_certificates_list(db, offset, limit)
        certificates_list = [
            CertificateDto(certificate_id=certificate.id, name=certificate.name) for certificate in certificates
        ]
        return certificates_list, total