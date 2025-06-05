from pydantic import BaseModel


class SignInRequest(BaseModel):
    # auth_provider: str
    # email: str
    code: str