from pydantic import ConfigDict


class SignInResponse:
    model_config = ConfigDict(from_attributes=True)

    access_token: str
    token_type: str = "bearer"