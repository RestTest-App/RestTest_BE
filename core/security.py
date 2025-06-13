from datetime import datetime, timedelta, timezone
from typing import Optional
from core.config import settings
from jose import jwt
from jose.exceptions import JWTError, ExpiredSignatureError
from exception.client_exception import UnauthorizedException


class JWTService:

    def __init__(self):
        self.algorithm = settings.JWT_ALGORITHM
        self.secret_key = settings.JWT_SECRET_KEY
        self.access_token_expire_minutes = settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        self.refresh_token_expire_minutes = settings.JWT_REFRESH_TOKEN_EXPIRE_MINUTES

    def _encode_jwt(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()

        now = datetime.now(timezone.utc)
        expire = now + expires_delta

        to_encode.update({
            "iat": now,
            "exp": expire,
        })
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

    def _create_token(self, data: dict, expires_delta: Optional[timedelta] = None):
        return self._encode_jwt(data, expires_delta)

    def create_access_token(self, data) -> str:
        access_delta = timedelta(minutes=self.access_token_expire_minutes)
        return self._create_token(data, access_delta)

    def create_refresh_token(self, data) -> str:
        refresh_delta = timedelta(minutes=self.refresh_token_expire_minutes)
        return self._create_token(data, refresh_delta)

    @staticmethod
    def verify_token(token: str) -> dict:
        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM]
            )
            return payload
        except ExpiredSignatureError:
            raise UnauthorizedException(detail="토큰이 만료되었습니다.")  # 401
        except JWTError:
            raise UnauthorizedException(detail="유효하지 않은 토큰입니다.")  # 401
