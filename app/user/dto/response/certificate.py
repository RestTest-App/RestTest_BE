from pydantic import BaseModel


class CertificateDto(BaseModel):
    certificate_id: int
    name: str