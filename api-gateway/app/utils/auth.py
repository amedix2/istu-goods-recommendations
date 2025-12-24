import jwt
import logging
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from fastapi import Response
import secrets

from app.config import settings
from app.exceptions import UnauthorizedError
from app.models import User

logger = logging.getLogger(__name__)

pwd_context = CryptContext(
    schemes=[settings.PASSWORD_HASH_ALGORITHM], deprecated="auto"
)


def get_password_hash(password: str) -> str:
    """Хеширует пароль пользователя для безопасного хранения."""
    logger.debug("Hashing password")
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверяет соответствие введённого пароля и хеша из базы."""
    logger.debug("Verifying password")
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(user: User) -> str:
    """Создаёт JWT access-токен с ID и ролью пользователя."""
    logger.debug("Creating access token", extra={"user_id": user.id})
    expire = datetime.now(timezone.utc) + timedelta(seconds=settings.ACCESS_TOKEN_EXPIRE)
    to_encode = {"sub": str(user.id), "role": user.role, "exp": expire}
    token = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    logger.debug("Access token created", extra={"user_id": user.id})
    return token


def create_refresh_token() -> str:
    """Создаёт случайный refresh-токен для обновления сессии."""
    logger.debug("Creating refresh token")
    token = secrets.token_hex(32)
    logger.debug("Refresh token created")
    return token


def decode_access_token(token: str) -> dict:
    """Декодирует JWT access-токен и проверяет валидность."""
    logger.debug("Decoding access token")
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        if payload.get("sub") is None or payload.get("role") is None:
            raise UnauthorizedError("Invalid token claims")
        logger.debug("Access token decoded successfully", extra={"payload": payload})
        return payload
    except jwt.ExpiredSignatureError:
        raise UnauthorizedError("Token expired")
    except jwt.InvalidTokenError:
        raise UnauthorizedError("Invalid token")


def set_refresh_cookie(response: Response, refresh_token: str) -> None:
    """Установка cookie."""
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=not settings.DEBUG,
        samesite="lax",
        max_age=settings.REFRESH_TOKEN_EXPIRE,
        path="/",
    )
    logger.debug("Refresh cookie set")
