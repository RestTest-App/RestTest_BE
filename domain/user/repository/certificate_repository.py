from sqlalchemy import Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from domain.user.entity.certificate import Certificate
from domain.user.entity.user import User
from exception.client_exception import NotFoundException


class CertificateRepository:

    # Certificate id 조회 검증
    @staticmethod
    async def get_certificates(db: AsyncSession, certificate_ids: Sequence[int]) -> list[Certificate]:
        certificates: list[Certificate] = []

        for cid in certificate_ids:
            certificate = await db.get(Certificate, cid)
            if not certificate:
                raise NotFoundException(message="자격증 정보를 찾을 수 없습니다.")
            else:
                certificates.append(certificate)
        return certificates


    # user.certificates에 Certificate 리스트 할당
    @staticmethod
    async def add_user_certificate(db: AsyncSession, user: User, certificates: Sequence[int]) -> User:
        certificates = CertificateRepository.get_certificates(db, certificates)
        user.certificate = certificates
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user
