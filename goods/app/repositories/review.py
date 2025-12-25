import logging
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models import Review

logger = logging.getLogger(__name__)


async def add_review(
        db: AsyncSession,
        product_id: int,
        user_id: int,
        rating: int,
        text: str | None = None,
) -> Review:
    """Добавляет отзыв к товару."""
    logger.debug("Adding review", extra={"product_id": product_id, "user_id": user_id, "rating": rating})
    review = Review(
        product_id=product_id,
        user_id=user_id,
        rating=rating,
        text=text,
    )
    try:
        db.add(review)
        await db.commit()
        await db.refresh(review)
    except Exception:
        await db.rollback()
        raise
    logger.debug("Review added successfully", extra={"review_id": review.id})
    return review


async def get_review_by_id(db: AsyncSession, review_id: int, joined_load: bool = False) -> Review | None:
    """Возвращает отзыв по ID."""
    logger.debug("Fetching review by ID", extra={"review_id": review_id})
    stmt = select(Review).where(Review.id == review_id)
    if joined_load:
        stmt = stmt.options(joinedload(Review.product))
    result = await db.execute(stmt)
    review = result.scalar_one_or_none()
    return review


async def get_review_by_user_and_product(db: AsyncSession, user_id: int, product_id: int) -> Review | None:
    """Ищет отзыв пользователя к конкретному товару."""
    stmt = select(Review).where(Review.user_id == user_id, Review.product_id == product_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def update_review(db: AsyncSession, review: Review, **fields) -> Review:
    """Обновляет отзыв."""
    logger.debug("Updating review", extra={"review_id": review.id, "fields": fields})
    for key, value in fields.items():
        if hasattr(review, key) and value is not None:
            setattr(review, key, value)
    try:
        await db.commit()
        await db.refresh(review)
    except Exception:
        await db.rollback()
        raise
    logger.debug("Review updated successfully", extra={"review_id": review.id})
    return review


async def delete_review(db: AsyncSession, review: Review) -> None:
    """Удаляет отзыв."""
    logger.debug("Deleting review", extra={"review_id": review.id})
    try:
        await db.delete(review)
        await db.commit()
    except Exception:
        await db.rollback()
        raise
    logger.debug("Review deleted successfully", extra={"review_id": review.id})
