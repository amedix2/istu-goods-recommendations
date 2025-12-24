import logging
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import joinedload

from app.models import RefreshToken
from app.config import settings

logger = logging.getLogger(__name__)


async def store_refresh_token(db: AsyncSession, user_id: int, token: str) -> None:
    """Сохраняет refresh-токен с expiration."""
    logger.debug("Storing refresh token", extra={"user_id": user_id})
    expire = datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(seconds=settings.REFRESH_TOKEN_EXPIRE)
    db_token = RefreshToken(user_id=user_id, token=token, expires_at=expire)
    try:
        db.add(db_token)
        await db.commit()
    except Exception:
        await db.rollback()
        raise
    logger.debug("Refresh token stored successfully", extra={"user_id": user_id})


async def get_refresh_token(db: AsyncSession, token: str, joined_load: bool = False) -> RefreshToken | None:
    """Возвращает refresh-токен, если валиден и не expired."""
    logger.debug("Fetching refresh token", extra={"token": token[:10] + "..."})
    stmt = select(RefreshToken).filter(RefreshToken.token == token)
    if joined_load:
        stmt = stmt.options(joinedload(RefreshToken.user))
    result = await db.execute(stmt)
    db_token = result.scalar_one_or_none()
    if db_token and db_token.expires_at >= datetime.now(timezone.utc).replace(tzinfo=None):
        logger.debug("Valid refresh token found")
        return db_token
    return None


async def delete_refresh_token(db: AsyncSession, token: str) -> None:
    """Удаляет конкретный refresh-токен."""
    logger.debug("Deleting refresh token", extra={"token": token[:10] + "..."})
    try:
        await db.execute(delete(RefreshToken).filter(RefreshToken.token == token))
        await db.commit()
    except Exception:
        await db.rollback()
        raise
    logger.debug("Refresh token deleted")


async def delete_all_refresh_tokens_for_user(db: AsyncSession, user_id: int) -> None:
    """Удаляет все refresh-токены для пользователя."""
    logger.debug("Deleting all refresh tokens for user", extra={"user_id": user_id})
    try:
        await db.execute(delete(RefreshToken).filter(RefreshToken.user_id == user_id))
        await db.commit()
    except Exception:
        await db.rollback()
        raise
    logger.debug("All refresh tokens deleted for user", extra={"user_id": user_id})
