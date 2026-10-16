from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None

    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Email Settings
    SMTP_HOST: str
    SMTP_PORT: int = 587
    SMTP_USER: str
    SMTP_PASSWORD: str
    SMTP_FROM_EMAIL: str
    SMTP_FROM_NAME: str = "MJ API"
    SMTP_USE_TLS: bool = True

    # Verification
    VERIFICATION_CODE_EXPIRE_MINUTES: int = 15
    PASSWORD_RESET_TOKEN_EXPIRE_HOURS: int = 24

    # Rate Limiting
    REGISTER_RATE_LIMIT: int = 5
    REGISTER_RATE_WINDOW: int = 60  # seconds
    LOGIN_RATE_LIMIT: int = 10
    LOGIN_RATE_WINDOW: int = 60  # seconds
    VERIFICATION_RATE_LIMIT: int = 10
    VERIFICATION_RATE_WINDOW: int = 60  # seconds
    PASSWORD_RESET_RATE_LIMIT: int = 3
    PASSWORD_RESET_RATE_WINDOW: int = 3600  # seconds (1 hour)
    GLOBAL_RATE_LIMIT: int = 100
    GLOBAL_RATE_WINDOW: int = 60  # seconds

    # App
    APP_NAME: str = "MJ API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    class Config:
        env_file = ".env"


settings = Settings()