import logging
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.services.reviews import (
    add_review_service,
    update_review_service,
    delete_review_service,
)
from app.schemas import ReviewCreateSchema, ReviewUpdateSchema, ReviewSchema
from app.utils.auth import get_auth_user_id

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/{product_id}", response_model=ReviewSchema)
async def add_review(
        product_id: int,
        review_data: ReviewCreateSchema,
        db: AsyncSession = Depends(get_session),
        auth_user_id: int = Depends(get_auth_user_id),
):
    logger.info("Add review endpoint called", extra={"product_id": product_id, "user_id": auth_user_id})
    return await add_review_service(db, product_id, auth_user_id, review_data)


@router.put("/{review_id}", response_model=ReviewSchema)
async def update_review(
        review_id: int,
        update_data: ReviewUpdateSchema,
        db: AsyncSession = Depends(get_session),
        auth_user_id: int = Depends(get_auth_user_id),
):
    logger.info("Update review endpoint called", extra={"review_id": review_id, "user_id": auth_user_id})
    return await update_review_service(db, review_id, update_data, auth_user_id)


@router.delete("/{review_id}")
async def delete_review(
        review_id: int,
        db: AsyncSession = Depends(get_session),
        auth_user_id: int | None = Depends(get_auth_user_id),
):
    logger.info("Delete review endpoint called", extra={"review_id": review_id, "user_id": auth_user_id})
    await delete_review_service(db, review_id, auth_user_id)
    return {"detail": "Review deleted"}
