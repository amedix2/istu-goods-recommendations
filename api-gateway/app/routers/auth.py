import logging
from fastapi import APIRouter, Depends, Response, Cookie
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.services.auth import register_user, login_user, refresh_access_token, logout_user
from app.schemas import UserSchema, TokenSchema

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/register", response_model=TokenSchema)
async def register(user: UserSchema, response: Response, db: AsyncSession = Depends(get_session)):
    logger.info("Register endpoint called", extra={"username": user.username})
    return await register_user(db, user, response)


@router.post("/login", response_model=TokenSchema)
async def login(user: UserSchema, response: Response, db: AsyncSession = Depends(get_session)):
    logger.info("Login endpoint called", extra={"username": user.username})
    return await login_user(db, user, response)


@router.post("/refresh", response_model=TokenSchema)
async def refresh(
        response: Response,
        refresh_token: str = Cookie(None),
        db: AsyncSession = Depends(get_session)):
    logger.info("Refresh token endpoint called")
    return await refresh_access_token(db, refresh_token, response)


@router.post("/logout")
async def logout(
        response: Response,
        refresh_token: str = Cookie(None),
        db: AsyncSession = Depends(get_session)):
    logger.info("Logout endpoint called")
    return await logout_user(db, refresh_token, response)
