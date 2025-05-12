from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    PROJECT_NAME: str = "Mallicious Message Detector"
    PROJECT_DESCRIPTION: str = "A malicious message detector utilizing LLMs"
    PROJECT_VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"

    # SECURITY CONFIGURATION
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 120
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # DATABASE CONFIGURATION
    DATABASE_URL: str = ""

    # GEMINI CONFIGURATION
    GEMINI_API_KEY: str = ""

    # OAUTH CONFIGURATION
    OAUTH_PROVIDERS: List[str] = ["google"]
    GOOGLE_OAUTH_CLIENT_ID: str = ""
    GOOGLE_OAUTH_CLIENT_SECRET: str = ""
    GOOGLE_OAUTH_REDIRECT_URI: str = ""
    GOOGLE_OAUTH_AUTH_URI: str = "https://accounts.google.com/o/oauth2/auth"
    GOOGLE_OAUTH_TOKEN_URI: str = "https://oauth2.googleapis.com/token"
    GOOGLE_OAUTH_CERTS_URI: str = "https://www.googleapis.com/oauth2/v1/certs"

    # CORS CONFIGURATION
    CORS_ALLOWED_ORIGINS: List[str] = ["http://localhost:3000"]
    CORS_ALLOWED_METHODS: List[str] = ["*"]
    CORS_ALLOWED_HEADERS: List[str] = ["*"]


    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()