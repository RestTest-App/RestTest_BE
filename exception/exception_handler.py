from fastapi import Request
from fastapi.responses import JSONResponse

from .base import CustomException

async def custom_exception_handeler(request: Request, exception: CustomException):
    return JSONResponse(
        status_code=exception.status_code,
        content={
            "code": exception.status_code,
            "detail": exception.detail,
            "message": getattr(exception, "message", exception.detail),
        }
    )