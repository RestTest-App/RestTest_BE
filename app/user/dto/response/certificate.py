from pydantic import BaseModel


class CertificateDto(BaseModel):
    certificate_id: str
    name: str