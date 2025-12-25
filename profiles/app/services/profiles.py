import logging
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.user import create_user, get_user_by_id, update_user, delete_user
from app.schemas import UserCreateSchema, UserUpdateSchema, UserSchema, UserBriefSchema
from app.exceptions import NotFoundError, ConflictError

logger = logging.getLogger(__name__)


async def create_user_service(db: AsyncSession, user_id: int, user_data: UserCreateSchema) -> UserSchema:
    """Создание пользователя."""
    logger.info("Creating user service", extra={"user_id": user_id})
    try:
        user = await create_user(db, user_id, **user_data.model_dump())
    except IntegrityError:
        raise ConflictError("User with such data already exists")
    logger.info("User created successfully", extra={"user_id": user.user_id})
    return UserSchema.model_validate(user)


async def get_user_profile(db: AsyncSession, user_id: int) -> UserSchema:
    """Получение полного профиля."""
    logger.info("Getting user profile", extra={"user_id": user_id})
    user = await get_user_by_id(db, user_id)
    if not user:
        raise NotFoundError("User not found")
    logger.info("User retrieved successfully", extra={"user_id": user.user_id})
    return UserSchema.model_validate(user)


async def update_user_service(db: AsyncSession, user_id: int, update_data: UserUpdateSchema) -> UserSchema:
    """Обновление профиля."""
    logger.info("Updating user service", extra={"user_id": user_id})
    fields = update_data.model_dump(exclude_unset=True)
    if not fields:
        raise ConflictError("No fields to update")
    user = await get_user_by_id(db, user_id)
    if not user:
        raise NotFoundError("User not found")
    try:
        updated_user = await update_user(db, user=user, **fields)
    except IntegrityError:
        raise ConflictError("Updated data conflicts with existing records")
    logger.info("User updated successfully", extra={"user_id": user_id})
    return UserSchema.model_validate(updated_user)


async def delete_user_service(db: AsyncSession, user_id: int) -> None:
    """Удаление профиля."""
    logger.info("Deleting user service", extra={"user_id": user_id})
    user = await get_user_by_id(db, user_id)
    if not user:
        raise NotFoundError("User not found")
    await delete_user(db, user)
    logger.info("User deleted successfully", extra={"user_id": user_id})
