from pydantic_settings import BaseSettings


# JWT
class JwtSetting(BaseSettings):
    JWT_SECRET_KEY: str = ""
    JWT_ALGORITHM: str = ""
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 0 # access token 만료 시간
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 0 # refresh token 만료 일

    class Config:
        env_file = ".env.dev"
        env_file_encoding = "utf-8"
        extra = "ignore"


# KAKAO
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


# OPENAI & NAVER OCR
class GPTSetting(BaseSettings):
    OPENAI_API_KEY: str = ""
    NAVER_OCR_URL: str = ""
    NAVER_SECRET_KEY: str = ""

    class Config:
        env_file = ".env.dev"
        env_file_encoding = "utf-8"
        extra = "ignore"


# AWS
class AWSSettings(BaseSettings):
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_REGION_NAME: str = ""
    AWS_STORAGE_BUCKET_NAME: str = ""

    class Config:
        env_file = ".env.dev"
        env_file_encoding = "utf-8"
        extra = "ignore"


# REDIS
class RedisSettings(BaseSettings):
    REDIS_HOST: str = ""
    REDIS_PORT: int

    class Config:
        env_file = ".env.dev"
        env_file_encoding = "utf-8"
        extra = "ignore"



settings = JwtSetting()
kakao_settings = KakaoSettings()
gpt_settings = GPTSetting()
aws_settings = AWSSettings()
redis_settings = RedisSettings()
