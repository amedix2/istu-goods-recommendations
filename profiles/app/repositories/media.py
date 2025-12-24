import logging
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models import Media

logger = logging.getLogger(__name__)


async def add_media(
        db: AsyncSession,
        user_id: int,
        file_path: str,
        file_path_thumb: str,
        description: str | None = None,
        is_avatar: bool = False,
) -> Media:
    """Добавляет фото пользователя."""
    logger.debug("Adding media", extra={"user_id": user_id, "file_path": file_path})
    media = Media(
        user_id=user_id,
        file_path=file_path,
        file_path_thumb=file_path_thumb,
        description=description,
        is_avatar=is_avatar,
    )
    try:
        db.add(media)
        await db.commit()
        await db.refresh(media)
    except Exception:
        await db.rollback()
        raise
    logger.debug("Media added successfully", extra={"media_id": media.id})
    return media


async def get_media_by_id(db: AsyncSession, media_id: int, joined_load: bool = False) -> Media | None:
    """Возвращает фото по ID."""
    logger.debug("Fetching media by ID", extra={"media_id": media_id})
    stmt = select(Media).where(Media.id == media_id)
    if joined_load:
        stmt = stmt.options(joinedload(Media.user))
    result = await db.execute(stmt)
    media = result.scalar_one_or_none()
    if media:
        logger.debug("Media found", extra={"media_id": media_id})
    else:
        logger.debug("Media not found", extra={"media_id": media_id})
    return media


async def update_media(db: AsyncSession, media: Media, **fields) -> Media:
    """Обновляет запись медиа."""
    logger.debug("Updating media", extra={"media_id": media.id, "fields": fields})
    for key, value in fields.items():
        if hasattr(media, key) and value is not None:
            setattr(media, key, value)
    try:
        await db.commit()
        await db.refresh(media)
    except Exception:
        await db.rollback()
        raise
    logger.debug("Media updated successfully", extra={"media_id": media.id})
    return media


async def delete_media(db: AsyncSession, media: Media) -> None:
    """Удаляет фото."""
    logger.debug("Deleting media", extra={"media_id": media.id})
    try:
        await db.delete(media)
        await db.commit()
    except Exception:
        await db.rollback()
        raise
    logger.debug("Media deleted successfully", extra={"media_id": media.id})
