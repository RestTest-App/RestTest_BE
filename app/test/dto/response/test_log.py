from datetime import datetime

from pydantic import BaseModel


class TestLogDto(BaseModel):
    test_tracker_id: int
    is_passed: bool
    solved_at: datetime
    correct_count: int
    total_count: int