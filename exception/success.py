# 200번대 성공 응답 처리
from fastapi import status
from starlette.responses import JSONResponse

class SuccessResponse(JSONResponse):
    def __init__(self, code: int, message: str = "success", data: dict | list | None = None):
        content = {
            "code": code,
            "message": message,
            "data": data if data is not None else {},
        }
        super().__init__(status_code=code, content=content)

# 200 OK
def ok(data=None, message="리소스 요청 성공"):
    return SuccessResponse(code=status.HTTP_200_OK, message=message, data=data)

# 201 Created
def created(data=None, message="리소스 생성 성공"):
    return SuccessResponse(code=status.HTTP_201_CREATED, message=message, data=data)

# 204 No Content - 본문이 없어야 하므로 JSONResponse로 반환
def no_content():
    return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content=None)