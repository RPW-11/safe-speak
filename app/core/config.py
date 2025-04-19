from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "Mallicious Message Detector"
    PROJECT_DESCRIPTION: str = "A malicious message detector utilizing LLMs"
    PROJECT_VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"

    # SECURITY CONFIGURATION
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # DATABASE CONFIGURATION
    DATABASE_URL: str = ""


    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()