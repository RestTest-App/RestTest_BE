from fastapi import HTTPException

class CustomException(HTTPException):
    def __init__(self, status_code: int, detail: str=None, message: str=None):
        detail = detail or "Error"
        message = message or detail
        super().__init__(status_code=status_code, detail=detail)
        self.message = message