"""Конфигурация приложения — читается из .env."""

from functools import lru_cache
from typing import List

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Приложение
    APP_ENV: str = "production"
    APP_DEBUG: bool = False
    APP_DOMAIN: str = "taxrep.finitin.us"
    APP_SECRET_KEY: str

    # База данных
    DATABASE_URL: str

    # Redis / Celery
    REDIS_URL: str = "redis://redis:6379/0"
    CELERY_BROKER_URL: str = "redis://redis:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://redis:6379/2"

    # Telegram
    TELEGRAM_BOT_TOKEN: str
    TELEGRAM_BOT_USERNAME: str

    # JWT
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # Шифрование полей
    FIELD_ENCRYPTION_KEY: str

    # CORS
    CORS_ORIGINS: List[str] = ["https://taxrep.finitin.us"]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors(cls, v):
        if isinstance(v, str):
            import json
            return json.loads(v)
        return v

    # OCR
    OCR_PROVIDER: str = "yandex"
    YANDEX_OCR_API_KEY: str = ""
    GOOGLE_APPLICATION_CREDENTIALS: str = ""
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_REGION: str = "us-east-1"

    # Валюта
    CBR_API_URL: str = "https://www.cbr.ru/scripts/XML_daily.asp"
    OPEN_EXCHANGE_RATES_APP_ID: str = ""

    # SMTP
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    EMAIL_FROM: str = ""

    # Первый админ (bootstrap)
    FIRST_ADMIN_TELEGRAM_ID: str = ""


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
