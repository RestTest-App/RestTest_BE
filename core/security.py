from datetime import datetime, timedelta, timezone
from typing import Optional
from core.config import settings
from jose import jwt
from jose.exceptions import JWTError, ExpiredSignatureError
from exception.client_exception import UnauthorizedException

# 토큰 발행
def create_access_token(
        data: dict,
        expires_delta: Optional[timedelta] = None
) -> str:
    to_encode = data.copy()

    now_utc = datetime.now(timezone.utc)
    expire = now_utc + expires_delta if expires_delta else timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({
        "iat": now_utc,
        "exp": expire
    })

    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

    return encoded_jwt

# 토큰 검증
def verify_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload

    except ExpiredSignatureError:
        raise UnauthorizedException(detail="토큰이 만료되었습니다.")

    except JWTError:
        raise UnauthorizedException(detail="유효하지 않은 토큰입니다.")