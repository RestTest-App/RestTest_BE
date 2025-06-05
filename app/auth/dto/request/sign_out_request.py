from pydantic import BaseModel


class SignOutRequest(BaseModel):
    refresh_token: str