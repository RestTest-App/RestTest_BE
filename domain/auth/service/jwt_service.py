import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict
from zoneinfo import ZoneInfo

from typing_extensions import Tuple

from core.config import settings
from jose import jwt
from jose.exceptions import JWTError, ExpiredSignatureError
from exception.client_exception import UnauthorizedException


class JWTService:

    def __init__(self):
        self.algorithm = settings.JWT_ALGORITHM
        self.secret_key = settings.JWT_SECRET_KEY
        self.access_token_expire = settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        self.refresh_token_expire = settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS
        self.timezone = ZoneInfo("Asia/Seoul")

    # jwt 인코딩
    def _encode_jwt(self, data: dict, expires_delta: timedelta) -> str:
        now = datetime.now(self.timezone)
        payload = data.copy()
        payload.update({
            "iat": now,
            "exp": now + expires_delta
        })
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    # Access Token 생성
    def create_access_token(self, user_id: int) -> str:
        data = {
            "sub": str(user_id),
        }
        token = self._encode_jwt(
            data=data,
            expires_delta=timedelta(minutes=self.access_token_expire)
        )
        return token

    # Refresh Token 생성
    def create_refresh_token(self, user_id: int) -> Tuple[str, str]:
        new_jti = str(uuid.uuid4())
        data = {
            "sub": str(user_id),
            "jti": new_jti
        }
        token = self._encode_jwt(
            data=data,
            expires_delta=timedelta(days=self.refresh_token_expire)
        )
        return token, new_jti


    # 토큰 디코딩 및 유효성 예외처리
    def verify_token(self, token: str) -> Dict:
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm]
            )
            return payload
        except ExpiredSignatureError:
            raise UnauthorizedException(detail="토큰이 만료되었습니다.")  # 401
        except JWTError:
            raise UnauthorizedException(detail="유효하지 않은 토큰입니다.")  # 401
