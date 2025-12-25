import logging
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.services.products import (
    create_product_service,
    get_product_details,
    update_product_service,
    delete_product_service,
    list_products
)
from app.schemas import ProductCreateSchema, ProductUpdateSchema, ProductSchema, ProductShortSchema
from app.utils.auth import get_auth_user_id

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/", response_model=ProductSchema)
async def create_product(
        product_data: ProductCreateSchema,
        db: AsyncSession = Depends(get_session),
        auth_user_id: int = Depends(get_auth_user_id),
):
    logger.info("Create product endpoint called", extra={"user_id": auth_user_id})
    return await create_product_service(db, product_data, user_id=auth_user_id)


@router.get("/{product_id}", response_model=ProductSchema)
async def get_product(product_id: int, db: AsyncSession = Depends(get_session)):
    logger.info("Get product endpoint called", extra={"product_id": product_id})
    return await get_product_details(db, product_id)


@router.put("/{product_id}", response_model=ProductSchema)
async def update_product(
        product_id: int,
        update_data: ProductUpdateSchema,
        db: AsyncSession = Depends(get_session),
        auth_user_id: int = Depends(get_auth_user_id),
):
    logger.info("Update product endpoint called", extra={"product_id": product_id, "user_id": auth_user_id})
    return await update_product_service(db, product_id, update_data, user_id=auth_user_id)


@router.delete("/{product_id}")
async def delete_product(
        product_id: int,
        db: AsyncSession = Depends(get_session),
        auth_user_id: int = Depends(get_auth_user_id),
):
    logger.info("Delete product endpoint called", extra={"product_id": product_id, "user_id": auth_user_id})
    await delete_product_service(db, product_id, user_id=auth_user_id)
    return {"detail": "Product deleted"}


@router.get("/", response_model=list[ProductShortSchema])
async def get_products(
        skip: int = 0,
        limit: int = 10,
        db: AsyncSession = Depends(get_session)
):
    logger.info("List products endpoint called", extra={"skip": skip, "limit": limit})
    return await list_products(db, skip=skip, limit=limit)
