from typing import List
from pydantic import BaseModel
from app.user.dto.response.certificate import CertificateDto
from app.utils.dto.pagination import PaginationDto


class CertificateResponseDto(BaseModel):
    certificates: List[CertificateDto]
    pagination: PaginationDto