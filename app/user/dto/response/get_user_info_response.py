import datetime
import json
from typing import Set, Any

from pydantic import BaseModel, ConfigDict, field_validator


class GetUserInfoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    profile_image: str | None
    nickname: str
    created_at: datetime.datetime
    total_study_days: int
    monthly_study_date: Set[int]

    @field_validator("monthly_study_date", mode="before")
    @classmethod
    def parse_monthly_study_date(cls, value: Any) -> Set[int]:
        if isinstance(value, set):
            return value

        if isinstance(value, list):
            return set(value)

        if isinstance(value, dict):
            return set(value.keys())

        if isinstance(value, str):
            body = value.split()
            if body == "" or body == "{}":
                return set()

            try:
                parsed = json.loads(value)
                if isinstance(parsed, list):
                    return set(parsed)
                if isinstance(parsed, dict):
                    return set(parsed.keys())
            except (json.JSONDecodeError, ValueError):
                inner = body.strip("{}")
                if not inner:
                    return set()
                return {item.strip() for item in inner.split(",") if item.strip()}

        return set()
