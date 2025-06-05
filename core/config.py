from pydantic_settings import BaseSettings


class JwtSetting(BaseSettings):
    JWT_SECRET_KEY: str = ""
    JWT_ALGORITHM: str = ""
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 0 # access token 만료 시간
    JWT_REFRESH_TOKEN_EXPIRE_MINUTES: int = 0 # refresh token 만료 시간

    class Config:
        env_file = ".env.dev"
        env_file_encoding = "utf-8"
        extra = "ignore"

class KakaoSettings(BaseSettings):
    KAKAO_CLIENT_ID: str = ""
    KAKAO_CLIENT_SECRET_KEY: str = ""
    KAKAO_REDIRECT_URI: str = ""
    KAKAO_AUTHORIZE_URL: str = ""
    KAKAO_TOKEN_URL: str = ""
    KAKAO_PROFILE_URL: str = ""

    class Config:
        env_file = ".env.dev"
        env_file_encoding = "utf-8"
        extra = "ignore"

class StorageSetting(BaseSettings):
    pass



settings = JwtSetting()
kakao_settings = KakaoSettings()