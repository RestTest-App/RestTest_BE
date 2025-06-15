from pydantic import BaseModel


class UpdateUserInfoRequest(BaseModel):
    nickname: str
    delete_image: bool = False # true 시 삭제 요청