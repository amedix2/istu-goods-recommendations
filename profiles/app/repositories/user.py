import logging
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models import User

logger = logging.getLogger(__name__)


async def create_user(
        db: AsyncSession,
        user_id: int,
        username: str,
        display_name: str,
        email: str,
        description: str | None = None,
) -> User:
    """Создает нового пользователя."""
    logger.debug("Creating user", extra={"user_id": user_id, "username": username})
    user = User(
        user_id=user_id,
        username=username,
        display_name=display_name,
        email=email,
        description=description,
    )
    try:
        db.add(user)
        await db.commit()
        await db.refresh(user)
    except Exception:
        await db.rollback()
        raise
    logger.debug("User created successfully", extra={"user_id": user.user_id})
    return user


async def get_user_by_id(db: AsyncSession, user_id: int, joined_load: bool = False) -> User | None:
    """Возвращает пользователя по user_id."""
    logger.debug("Fetching user by ID", extra={"user_id": user_id})
    stmt = select(User).where(User.user_id == user_id)
    if joined_load:
        stmt = stmt.options(joinedload(User.media))
    result = await db.execute(stmt)
    if joined_load:
        user = result.unique().scalar_one_or_none()
    else:
        user = result.scalar_one_or_none()
    if user:
        logger.debug("User found", extra={"user_id": user_id})
    else:
        logger.debug("User not found", extra={"user_id": user_id})
    return user


async def update_user(db: AsyncSession, user: User, **fields) -> User:
    """Обновляет данные пользователя."""
    logger.debug("Updating user", extra={"user_id": user.user_id, "fields": fields})
    for key, value in fields.items():
        if hasattr(user, key) and value is not None:
            setattr(user, key, value)
    try:
        await db.commit()
        await db.refresh(user)
    except Exception:
        await db.rollback()
        raise
    logger.debug("User updated successfully", extra={"user_id": user.user_id})
    return user


async def delete_user(db: AsyncSession, user: User) -> None:
    """Удаляет пользователя."""
    logger.debug("Deleting user", extra={"user_id": user.user_id})
    try:
        await db.delete(user)
        await db.commit()
    except Exception:
        await db.rollback()
        raise
    logger.debug("User deleted successfully", extra={"user_id": user.user_id})
