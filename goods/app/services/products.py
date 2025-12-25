import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from app.repositories.product import (
    create_product,
    get_product_by_id,
    get_all_products,
    update_product,
    delete_product
)
from app.schemas import ProductCreateSchema, ProductSchema, ProductUpdateSchema, ProductShortSchema
from app.exceptions import ConflictError, NotFoundError, ForbiddenError

logger = logging.getLogger(__name__)


async def create_product_service(db: AsyncSession, product_data: ProductCreateSchema, user_id: int) -> ProductSchema:
    """Создание товара с привязкой к пользователю."""
    logger.info("Creating product service", extra={"product_name": product_data.name, "user_id": user_id})
    try:
        product = await create_product(
            db,
            joined_load=True,
            user_id=user_id,
            **product_data.model_dump()
        )
    except IntegrityError:
        raise ConflictError("Product creation failed")

    logger.info("Product created successfully", extra={"product_id": product.id})
    return ProductSchema.model_validate(product)


async def get_product(db: AsyncSession, product_id: int) -> ProductSchema:
    logger.info("Getting product service", extra={"product_id": product_id})
    product = await get_product_by_id(db, product_id, joined_load=False)
    if not product:
        raise NotFoundError("Product not found")
    return ProductSchema.model_validate(product)


async def get_product_details(db: AsyncSession, product_id: int) -> ProductSchema:
    logger.info("Getting product details", extra={"product_id": product_id})
    product = await get_product_by_id(db, product_id, joined_load=True)
    if not product:
        raise NotFoundError("Product not found")
    return ProductSchema.model_validate(product)


async def list_products(db: AsyncSession, skip: int = 0, limit: int = 10) -> list[ProductShortSchema]:
    logger.info("Listing products")
    products = await get_all_products(db, skip=skip, limit=limit, joined_load=False)
    return [ProductShortSchema.model_validate(p) for p in products]


async def update_product_service(
        db: AsyncSession,
        product_id: int,
        product_data: ProductUpdateSchema,
        user_id: int
) -> ProductSchema:
    """Обновление товара (только владелец)."""
    logger.info("Updating product service", extra={"product_id": product_id, "user_id": user_id})
    product = await get_product_by_id(db, product_id, joined_load=True)
    if not product:
        raise NotFoundError("Product not found")

    if product.user_id != user_id:
        raise ForbiddenError("You can only edit your own products")

    try:
        updated_product = await update_product(db, product, **product_data.model_dump(exclude_unset=True))
    except IntegrityError:
        raise ConflictError("Update failed")

    return ProductSchema.model_validate(updated_product)


async def delete_product_service(db: AsyncSession, product_id: int, user_id: int) -> None:
    """Удаление товара (только владелец)."""
    logger.info("Deleting product service", extra={"product_id": product_id, "user_id": user_id})
    product = await get_product_by_id(db, product_id)
    if not product:
        raise NotFoundError("Product not found")

    if product.user_id != user_id:
        raise ForbiddenError("You can only delete your own products")

    await delete_product(db, product)
