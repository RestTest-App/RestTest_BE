from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from app.user.dto.response.certificate import CertificateDto
from domain.user.repository.certificate_repository import CertificateRepository


class CertificateService:
    def __init__(self, repository: CertificateRepository):
        self.repository = repository

    async def fetch(self, db: AsyncSession, offset: int, limit: int) -> (List[CertificateDto], int):
        certificates, total = await self.repository.get_certificates_list(db, offset, limit)
        certificates_list = [
            CertificateDto(certificate_id=certificate.id, name=certificate.name) for certificate in certificates
        ]
        return certificates_list, total