import logging
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.review import add_review, get_review_by_id, update_review, delete_review, \
    get_review_by_user_and_product
from app.repositories.product import get_product_by_id
from app.schemas import ReviewCreateSchema, ReviewUpdateSchema, ReviewSchema
from app.exceptions import NotFoundError, ForbiddenError, ConflictError, UnauthorizedError

logger = logging.getLogger(__name__)


async def _recalculate_product_rating(db: AsyncSession, product_id: int):
    """Служебная функция пересчета рейтинга товара."""
    product = await get_product_by_id(db, product_id, joined_load=True)
    if not product:
        return

    total_reviews = len(product.reviews)
    if total_reviews > 0:
        avg_rating = sum(r.rating for r in product.reviews) / total_reviews
    else:
        avg_rating = 0.0

    product.rating = avg_rating
    product.reviews_count = total_reviews
    await db.commit()
    logger.debug("Product rating recalculated", extra={"product_id": product_id, "new_rating": avg_rating})


async def add_review_service(
        db: AsyncSession,
        product_id: int,
        user_id: int,
        review_data: ReviewCreateSchema
) -> ReviewSchema:
    """Добавление отзыва."""
    logger.info("Adding review service", extra={"product_id": product_id, "user_id": user_id})

    product = await get_product_by_id(db, product_id)
    if not product:
        raise NotFoundError("Product not found")

    existing_review = await get_review_by_user_and_product(db, user_id, product_id)
    if existing_review:
        raise ConflictError("User has already reviewed this product")

    try:
        review = await add_review(
            db,
            product_id=product_id,
            user_id=user_id,
            rating=review_data.rating,
            text=review_data.text,
        )
        await _recalculate_product_rating(db, product_id)

        logger.info("Review added successfully", extra={"review_id": review.id})
        return ReviewSchema.model_validate(review)
    except IntegrityError:
        raise ConflictError("Review creation error")


async def update_review_service(
        db: AsyncSession, review_id: int, update_data: ReviewUpdateSchema, user_id: int) -> ReviewSchema:
    """Обновление отзыва."""
    logger.info("Updating review service", extra={"review_id": review_id, "user_id": user_id})
    review = await get_review_by_id(db, review_id, joined_load=True)
    if not review:
        raise NotFoundError("Review not found")
    if review.user_id != user_id:
        raise ForbiddenError("Can only update own reviews")

    fields = update_data.model_dump(exclude_unset=True)
    if not fields:
        raise ConflictError("No fields to update")
    try:
        updated_review = await update_review(db, review=review, **fields)
        if "rating" in fields:
            await _recalculate_product_rating(db, review.product_id)

        logger.info("Review updated successfully", extra={"review_id": review_id})
        return ReviewSchema.model_validate(updated_review)
    except IntegrityError:
        raise ConflictError("Updated data conflicts")


async def delete_review_service(db: AsyncSession, review_id: int, auth_user_id: int) -> None:
    """Удаление отзыва."""
    logger.info("Deleting review service", extra={"review_id": review_id, "user_id": auth_user_id})
    if auth_user_id is None:
        raise UnauthorizedError("Authentication required")
    review = await get_review_by_id(db, review_id, joined_load=True)
    if not review:
        raise NotFoundError("Review not found")
    if review.user_id != auth_user_id:
        raise ForbiddenError("Can only delete own reviews")

    product_id = review.product_id
    await delete_review(db, review)
    await _recalculate_product_rating(db, product_id)

    logger.info("Review deleted successfully", extra={"review_id": review_id})
