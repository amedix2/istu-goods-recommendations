import logging
from asyncio import to_thread
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User
from app.utils.auth import get_password_hash, verify_password

logger = logging.getLogger(__name__)


async def create_user(db: AsyncSession, username: str, password: str) -> User:
    """Создает нового пользователя с хэшированным паролем."""
    logger.debug("Creating user", extra={"username": username})
    hashed_password = await to_thread(get_password_hash, password)
    db_user = User(username=username, hashed_password=hashed_password, role="user")
    try:
        db.add(db_user)
        await db.commit()
    except Exception:
        await db.rollback()
        raise
    await db.refresh(db_user)
    logger.debug("User created", extra={"user_id": db_user.id, "username": username})
    return db_user


async def get_user_by_username(db: AsyncSession, username: str) -> User | None:
    """Возвращает пользователя по username."""
    logger.debug("Fetching user by username", extra={"username": username})
    result = await db.execute(select(User).filter(User.username == username))
    user = result.scalar_one_or_none()
    if user:
        logger.debug("User found", extra={"user_id": user.id})
    else:
        logger.debug("User not found")
    return user


async def get_user_by_id(db: AsyncSession, user_id: int) -> User | None:
    """Возвращает пользователя по ID."""
    logger.debug("Fetching user by ID", extra={"user_id": user_id})
    result = await db.execute(select(User).filter(User.id == user_id))
    user = result.scalar_one_or_none()
    if user:
        logger.debug("User found", extra={"username": user.username})
    else:
        logger.debug("User not found")
    return user


async def authenticate_user(db: AsyncSession, username: str, password: str) -> User | None:
    """Аутентифицирует пользователя по username и password."""
    logger.debug("Authenticating user", extra={"username": username})
    user = await get_user_by_username(db, username)
    if not user or not await to_thread(verify_password, password, user.hashed_password):
        return None
    logger.debug("User authenticated successfully", extra={"user_id": user.id})
    return user
