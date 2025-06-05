from pydantic import ConfigDict, BaseModel


class SignInResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    access_token: str
    refresh_token: str