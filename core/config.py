from pydantic import BaseSettings

class JwtSetting(BaseSettings):
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int # access token 만료 시간

    class Config:
        env_file = ".env.dev"
        env_file_encoding = "utf-8"

settings = JwtSetting()