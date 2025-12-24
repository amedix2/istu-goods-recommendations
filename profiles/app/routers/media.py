import logging
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.services.media import (
    add_media_service,
    update_media_service,
    delete_media_service,
)
from app.schemas import MediaCreateSchema, MediaUpdateSchema, MediaSchema
from app.utils.auth import get_auth_user_id

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/", response_model=MediaSchema)
async def add_media(
        media_data: MediaCreateSchema,
        db: AsyncSession = Depends(get_session),
        auth_user_id: int = Depends(get_auth_user_id),
):
    logger.info("Add media endpoint called", extra={"user_id": auth_user_id})
    return await add_media_service(db, auth_user_id, media_data)


@router.put("/{media_id}", response_model=MediaSchema)
async def update_media(
        media_id: int,
        update_data: MediaUpdateSchema,
        db: AsyncSession = Depends(get_session),
        auth_user_id: int = Depends(get_auth_user_id),
):
    logger.info("Update media endpoint called", extra={"media_id": media_id, "user_id": auth_user_id})
    return await update_media_service(db, media_id, update_data, auth_user_id)


@router.delete("/{media_id}")
async def delete_media(
        media_id: int,
        db: AsyncSession = Depends(get_session),
        auth_user_id: int | None = Depends(get_auth_user_id),
):
    logger.info("Delete media endpoint called", extra={"media_id": media_id, "user_id": auth_user_id})
    await delete_media_service(db, media_id, auth_user_id)
    return {"detail": "Media deleted"}
