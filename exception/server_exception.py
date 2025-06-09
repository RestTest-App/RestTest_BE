# 500번대 서버 예외 처리 명세
from fastapi import status
from .base import CustomException

# 500 InternalServerError
class InternalServerErrorException(CustomException):
    def __init__(self, detail: str = "Internal Server Error", message: str = None):
        super().__init__(status.HTTP_500_INTERNAL_SERVER_ERROR, detail, message)

# 501 BadGatewayException
class BadGatewayException(CustomException):
    def __init__(self, detail: str = "Bad Gateway", message: str = None):
        super().__init__(status.HTTP_501_NOT_IMPLEMENTED, detail, message)

# 503 ServiceUnavailable
class ServiceUnavailableException(CustomException):
    def __init__(self, detail: str = "Service Unavailable", message: str = None):
        super().__init__(status.HTTP_503_SERVICE_UNAVAILABLE, detail, message)

# 504 GatewayTimeout
class GatewayTimeoutException(CustomException):
    def __init__(self, detail: str = "Gateway Timeout", message: str = None):
        super().__init__(status.HTTP_504_GATEWAY_TIMEOUT, detail, message)