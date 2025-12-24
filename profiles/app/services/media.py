import logging
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.media import add_media, get_media_by_id, update_media, delete_media
from app.repositories.user import get_user_by_id
from app.schemas import MediaCreateSchema, MediaUpdateSchema, MediaSchema
from app.exceptions import NotFoundError, ForbiddenError, ConflictError, UnauthorizedError

logger = logging.getLogger(__name__)


async def add_media_service(db: AsyncSession, user_id: int, media_data: MediaCreateSchema) -> MediaSchema:
    """Добавление медиа."""
    logger.info("Adding media service", extra={"user_id": user_id})
    user = await get_user_by_id(db, user_id)
    if not user:
        raise NotFoundError("User not found")
    try:
        media = await add_media(
            db,
            user_id=user_id,
            file_path=media_data.file_path,
            file_path_thumb=media_data.file_path_thumb,
            description=media_data.description,
            is_avatar=media_data.is_avatar,
        )
        logger.info("Media added successfully", extra={"media_id": media.id})
        return MediaSchema.model_validate(media)
    except IntegrityError:
        raise ConflictError("Media with such params already exists")


async def update_media_service(
        db: AsyncSession, media_id: int, update_data: MediaUpdateSchema, user_id: int) -> MediaSchema:
    """Обновление медиа."""
    logger.info("Updating media service", extra={"media_id": media_id, "user_id": user_id})
    media = await get_media_by_id(db, media_id, joined_load=True)
    if not media:
        raise NotFoundError("Media not found")
    if media.user.user_id != user_id:
        raise ForbiddenError("Can only update own media")
    fields = update_data.model_dump(exclude_unset=True)
    if not fields:
        raise ConflictError("No fields to update")
    try:
        updated_media = await update_media(db, media=media, **fields)
        logger.info("Media updated successfully", extra={"media_id": media_id})
        return MediaSchema.model_validate(updated_media)
    except IntegrityError:
        raise ConflictError("Updated data conflicts with existing records")


async def delete_media_service(db: AsyncSession, media_id: int, auth_user_id: int) -> None:
    """Удаление медиа."""
    logger.info("Deleting media service", extra={"media_id": media_id, "user_id": auth_user_id})
    if auth_user_id is None:
        raise UnauthorizedError("Authentication required")
    media = await get_media_by_id(db, media_id, joined_load=True)
    if not media:
        raise NotFoundError("Media not found")
    if media.user.user_id != auth_user_id:
        raise ForbiddenError("Can only delete own media")
    await delete_media(db, media)
    logger.info("Media deleted successfully", extra={"media_id": media_id})
