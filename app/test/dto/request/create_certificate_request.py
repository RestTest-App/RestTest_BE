from pydantic import BaseModel, Field

class CreateCertificateRequest(BaseModel):
    name: str = Field(..., description="자격증 이름")
