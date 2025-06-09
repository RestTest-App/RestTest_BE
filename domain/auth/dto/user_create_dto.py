from pydantic import BaseModel, ConfigDict


class UserCreateDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    auth_provider: str
    email: str
    nickname: str
    gender: str
    birthday: str
    job: str
    certificates: list[int]
    agree_to_terms: bool