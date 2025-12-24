import logging
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.services.profiles import (
    create_user_service,
    get_user_profile,
    get_user_brief,
    update_user_service,
    delete_user_service,
)
from app.schemas import UserCreateSchema, UserUpdateSchema, UserSchema, UserBriefSchema
from app.utils.auth import get_auth_user_id

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/", response_model=UserSchema)
async def create_profile(
        user_data: UserCreateSchema,
        db: AsyncSession = Depends(get_session),
        auth_user_id: int = Depends(get_auth_user_id),
):
    logger.info("Create profile endpoint called", extra={"user_id": auth_user_id})
    return await create_user_service(db, auth_user_id, user_data)


@router.get("/", response_model=UserSchema)
async def get_profile_self(
        db: AsyncSession = Depends(get_session),
        auth_user_id: int = Depends(get_auth_user_id),
):
    logger.info("Get self profile endpoint called", extra={"user_id": auth_user_id})
    return await get_user_profile(db, auth_user_id)


@router.get("/brief", response_model=UserBriefSchema)
async def get_profile_brief_self(
        db: AsyncSession = Depends(get_session),
        auth_user_id: int = Depends(get_auth_user_id),
):
    logger.info("Get self brief profile endpoint called", extra={"user_id": auth_user_id})
    return await get_user_brief(db, auth_user_id)


@router.get("/{user_id}", response_model=UserSchema)
async def get_profile(user_id: int, db: AsyncSession = Depends(get_session)):
    logger.info("Get profile endpoint called", extra={"user_id": user_id})
    return await get_user_profile(db, user_id)


@router.get("/{user_id}/brief", response_model=UserBriefSchema)
async def get_profile_brief(user_id: int, db: AsyncSession = Depends(get_session)):
    logger.info("Get brief profile endpoint called", extra={"user_id": user_id})
    return await get_user_brief(db, user_id)


@router.put("/", response_model=UserSchema)
async def update_profile_self(
        update_data: UserUpdateSchema,
        db: AsyncSession = Depends(get_session),
        auth_user_id: int = Depends(get_auth_user_id),
):
    logger.info("Update self profile endpoint called", extra={"user_id": auth_user_id})
    return await update_user_service(db, auth_user_id, update_data)


@router.delete("/")
async def delete_profile_self(
        db: AsyncSession = Depends(get_session),
        auth_user_id: int = Depends(get_auth_user_id),
):
    logger.info("Delete self profile endpoint called", extra={"user_id": auth_user_id})
    await delete_user_service(db, auth_user_id)
    return {"detail": "User deleted"}
