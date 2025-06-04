import datetime
from typing import List

from pydantic import BaseModel, ConfigDict


class GetUserInfoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    profile_image: str | None
    nickname: str
    created_at: datetime.datetime
    total_study_days: int
    monthly_study_date: List[int]