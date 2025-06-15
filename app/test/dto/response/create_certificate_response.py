from pydantic import BaseModel, Field

class CreateCertificateResponse(BaseModel):
    certificate_id: int = Field(..., description="생성된 자격증 ID")
