# 400번대 클라이언트 예외 처리 명세
from fastapi import status
from .base import CustomException

# 400 BadRequest
class BadRequestException(CustomException):
    def __init__(self, detail: str = "Bad Request", message: str = None):
        super().__init__(status.HTTP_400_BAD_REQUEST, detail, message)

# 401 Unauthorized
class UnauthorizedException(CustomException):
    def __init__(self, detail: str = "Unauthorized", message: str = None):
        super().__init__(status.HTTP_401_UNAUTHORIZED, detail, message)

# 403 Forbidden
class ForbiddenException(CustomException):
    def __init__(self, detail: str = "Forbidden", message: str = None):
        super().__init__(status.HTTP_403_FORBIDDEN, detail, message)

# 404 NotFound
class NotFoundException(CustomException):
    def __init__(self, detail: str = "Not Found", message: str = None):
        super().__init__(status.HTTP_404_NOT_FOUND, detail, message)

# 409 Conflict
class ConflictException(CustomException):
    def __init__(self, detail: str = "Confict", message: str = None):
        super().__init__(status.HTTP_409_CONFLICT, detail, message)

# 413 RequestEntityTooLarge
class RequestEntityTooLargeException(CustomException):
    def __init__(self, detail: str = "Request Entity too large", message: str = None):
        super().__init__(status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail, message)

# 415 UnsupportedMediaType
class UnsupportedMediaTypeException(CustomException):
    def __init__(self, detail: str = "Unsupported Media Type", message: str = None):
        super().__init__(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail, message)

# 416 RequestedRangeNotSatisfiable
class RequestedRangeNotSatisfiableException(CustomException):
    def __init__(self, detail: str = "Requested Range Not Satisfiable"):
        super().__init__(status.HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE, detail)

# 422 UnprocessableEntity
class UnprocessableEntityException(CustomException):
    def __init__(self, detail: str = "Unprocessable Entity"):
        super().__init__(status.HTTP_422_UNPROCESSABLE_ENTITY, detail)

# 429 TooManyRequests
class TooManyRequestsException(CustomException):
    def __init__(self, detail: str = "Too Many Requests"):
        super().__init__(status.HTTP_429_TOO_MANY_REQUESTS, detail)

# 429 Rate Limit Exceeded (API 사용량 제한 초과)
class RateLimitExceededException(CustomException):
    def __init__(self, detail: str = "Rate Limit Exceeded", message: str = None):
        if message is None:
            message = "일일 무료 사용 횟수를 초과했습니다. 프리미엄 구독을 이용해주세요."
        super().__init__(status.HTTP_429_TOO_MANY_REQUESTS, detail, message)