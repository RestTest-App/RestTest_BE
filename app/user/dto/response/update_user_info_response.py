from pydantic import BaseModel


class UpdateUserInfoResponse(BaseModel):
    nickname: str
    profile_image: str