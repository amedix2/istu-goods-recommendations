import logging
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from app.models import Product

logger = logging.getLogger(__name__)


async def create_product(db: AsyncSession, joined_load: bool = False, **kwargs) -> Product:
    logger.debug("Creating product", extra={"product_name": kwargs.get("name"), "product_price": kwargs.get("price")})
    try:
        product = Product(**kwargs)
        db.add(product)
        await db.commit()

        stmt = select(Product).where(Product.id == product.id)
        if joined_load:
            stmt = stmt.options(joinedload(Product.reviews))

        result = await db.execute(stmt)
        if joined_load:
            return result.unique().scalar_one()
        return result.scalar_one()
    except Exception as e:
        await db.rollback()
        logger.error("Error creating product", extra={"error": str(e)})
        raise e


async def get_product_by_id(db: AsyncSession, product_id: int, joined_load: bool = False) -> Product | None:
    logger.debug("Fetching product by ID", extra={"product_id": product_id})
    stmt = select(Product).where(Product.id == product_id)
    if joined_load:
        stmt = stmt.options(joinedload(Product.reviews))

    result = await db.execute(stmt)
    if joined_load:
        return result.unique().scalar_one_or_none()
    return result.scalar_one_or_none()


async def get_all_products(db: AsyncSession, skip: int = 0, limit: int = 10, joined_load: bool = False) -> list[
    Product]:
    logger.debug("Fetching products", extra={"skip": skip, "limit": limit})
    stmt = select(Product).offset(skip).limit(limit)
    if joined_load:
        stmt = stmt.options(joinedload(Product.reviews))

    result = await db.execute(stmt)
    if joined_load:
        products = result.unique().scalars().all()
    else:
        products = result.scalars().all()
    return list(products)


async def update_product(db: AsyncSession, product: Product, **kwargs) -> Product:
    logger.debug("Updating product", extra={"product_id": product.id})
    try:
        for key, value in kwargs.items():
            setattr(product, key, value)
        await db.commit()
        await db.refresh(product)
        return product
    except Exception as e:
        await db.rollback()
        logger.error("Error updating product", extra={"error": str(e)})
        raise e


async def delete_product(db: AsyncSession, product: Product) -> None:
    logger.debug("Deleting product", extra={"product_id": product.id})
    try:
        await db.delete(product)
        await db.commit()
    except Exception as e:
        await db.rollback()
        logger.error("Error deleting product", extra={"error": str(e)})
        raise e
