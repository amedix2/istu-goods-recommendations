import logging
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from typing import Dict, List
from pytimeparse import parse


class Settings(BaseSettings):
    # Параметры подключения к PostgreSQL
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str
    POOL_SIZE: int = 10
    MAX_OVERFLOW: int = 20
    POOL_TIMEOUT: int = 30  # Значение в секундах
    POOL_RECYCLE: int = 60 * 60 * 30  # Значение в секундах

    # Настройки Granian
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 1
    LOG_LEVEL: int = logging.INFO

    # Настройки JWT
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE: int = 15 * 60  # Значение в секундах
    REFRESH_TOKEN_EXPIRE: int = 30 * 24 * 60 * 60  # Значение в секундах

    # Настройки паролей
    PASSWORD_HASH_ALGORITHM: str = "bcrypt"  # алгоритм шифрования паролей

    # Настройки CORS и микросервисов
    ALLOWED_ORIGINS: List[str] = []
    MICRO_SERVICES: Dict[str, str] = {}
    TOTAL_TIMEOUT: int = 10  # Значение в секундах

    # Режим отладки
    DEBUG: bool = False

    @field_validator("LOG_LEVEL", mode="before")
    @classmethod
    def parse_log_level(cls, v):
        if isinstance(v, int):
            return v
        if isinstance(v, str):
            return getattr(logging, v.upper(), logging.INFO)
        raise ValueError("Invalid LOG_LEVEL")

    @field_validator("JWT_SECRET_KEY")
    @classmethod
    def validate_jwt_secret(cls, v: str) -> str:
        if len(v) < 32:
            raise ValueError("JWT_SECRET_KEY must be at least 32 characters long")
        return v

    @field_validator("DEBUG", mode="before")
    @classmethod
    def parse_debug(cls, v):
        if isinstance(v, bool):
            return v
        if isinstance(v, (int, float)):
            return bool(v)
        if isinstance(v, str):
            return v.strip().lower() in {"1", "true", "yes", "y", "on"}
        return False

    @field_validator("ACCESS_TOKEN_EXPIRE", mode="before")
    @classmethod
    def parse_access_token_time(cls, v) -> int:
        if isinstance(v, int):
            return v
        parsed_time = parse(v)
        if parsed_time is None:
            raise ValueError(f"Could not parse ACCESS_TOKEN_EXPIRE: {v}")
        return int(parsed_time)

    @field_validator("REFRESH_TOKEN_EXPIRE", mode="before")
    @classmethod
    def parse_refresh_token_time(cls, v) -> int:
        if isinstance(v, int):
            return v
        parsed_time = parse(v)
        if parsed_time is None:
            raise ValueError(f"Could not parse REFRESH_TOKEN_EXPIRE: {v}")
        return int(parsed_time)

    @field_validator("POOL_TIMEOUT", mode="before")
    @classmethod
    def parse_pool_timeout_time(cls, v) -> int:
        if isinstance(v, int):
            return v
        parsed_time = parse(v)
        if parsed_time is None:
            raise ValueError(f"Could not parse POOL_TIMEOUT: {v}")
        return int(parsed_time)

    @field_validator("POOL_RECYCLE", mode="before")
    @classmethod
    def parse_pool_recycle_time(cls, v) -> int:
        if isinstance(v, int):
            return v
        parsed_time = parse(v)
        if parsed_time is None:
            raise ValueError(f"Could not parse POOL_RECYCLE: {v}")
        return int(parsed_time)

    @field_validator("TOTAL_TIMEOUT", mode="before")
    @classmethod
    def parse_total_timeout_time(cls, v) -> int:
        if isinstance(v, int):
            return v
        parsed_time = parse(v)
        if parsed_time is None:
            raise ValueError(f"Could not parse TOTAL_REQUEST_TIMEOUT: {v}")
        return int(parsed_time)

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
