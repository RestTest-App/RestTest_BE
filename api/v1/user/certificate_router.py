from typing import List

from fastapi import APIRouter, Query, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.user.dto.response.certificates_response import CertificateResponseDto
from app.user.usecase.certificate_usecase import CertificateUseCase
from database.dependency import get_db
from domain.user.repository.certificate_repository import CertificateRepository
from domain.user.service.certificate_service import CertificateService
from exception.success import ok

router = APIRouter()
@router.get("/get-certificates-list", response_model=CertificateResponseDto)
async def get_certificates_list(
        offset: int = Query(0, ge=0),
        limit: int = Query(20, ge=0),
        db: AsyncSession = Depends(get_db)
):
    usecase = CertificateUseCase()
    data = await usecase.execute(db=db, offset=offset, limit=limit)

    return ok(data=data.model_dump() ,message="자격증 리스트 조회 성공")