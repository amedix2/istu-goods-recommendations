import logging
import aiohttp
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Response, Request

from app.repositories.user import create_user, get_user_by_username, authenticate_user, _delete_user_by_id
from app.repositories.refresh_token import (
    get_refresh_token,
    delete_refresh_token,
    delete_all_refresh_tokens_for_user
)
from app.repositories.refresh_token import store_refresh_token
from app.utils.auth import create_access_token, create_refresh_token, set_refresh_cookie
from app.schemas import UserSchema, TokenSchema
from app.exceptions import InvalidCredentials, ServiceUnavailableError, UnauthorizedError
from app.config import settings

logger = logging.getLogger(__name__)


async def register_user(db: AsyncSession, user: UserSchema, response: Response, request: Request) -> TokenSchema:
    existing_user = await get_user_by_username(db, user.username)
    if existing_user:
        raise InvalidCredentials("Username already exists")
    db_user = await create_user(db, user.username, user.password)
    try:
        profile_url = f"{settings.MICRO_SERVICES['profiles']}/profile/"
        profile_data = {
            "username": db_user.username,
            "display_name": db_user.username,
        }

        headers = {"X-Auth-User-ID": str(db_user.id)}
        session = request.app.state.aiohttp_session

        async with session.post(profile_url, json=profile_data, headers=headers) as resp:
            if resp.status != 201 and resp.status != 200:
                error_detail = await resp.text()
                logger.error(f"Profiles service returned {resp.status}", extra={"detail": error_detail})
                raise ServiceUnavailableError("Profiles service failed")

    except Exception as e:
        logger.warning(f"Rolling back registration: deleting user {db_user.id} due to profile creation failure")
        await _delete_user_by_id(db, db_user.id)

        if isinstance(e, ServiceUnavailableError):
            raise e
        raise ServiceUnavailableError(f"External service error: {str(e)}")

    access_token = create_access_token(db_user)
    refresh_token = create_refresh_token()
    await store_refresh_token(db, db_user.id, refresh_token)
    set_refresh_cookie(response, refresh_token)

    return TokenSchema(access_token=access_token)


async def login_user(db: AsyncSession, user: UserSchema, response: Response) -> TokenSchema:
    """Бизнес-логика логина: аутентификация, удаление старых токенов, новые токены."""
    logger.info("Logging in user", extra={"username": user.username})
    db_user = await authenticate_user(db, user.username, user.password)
    if not db_user:
        raise InvalidCredentials("Invalid username or password")
    await delete_all_refresh_tokens_for_user(db, db_user.id)
    access_token = create_access_token(db_user)
    refresh_token = create_refresh_token()
    await store_refresh_token(db, db_user.id, refresh_token)
    set_refresh_cookie(response, refresh_token)
    logger.info("User logged in successfully", extra={"user_id": db_user.id})
    return TokenSchema(access_token=access_token)


async def refresh_access_token(db: AsyncSession, refresh_token: str | None, response: Response) -> TokenSchema:
    """Бизнес-логика рефреша: валидация, ротация токена, новый access."""
    logger.info("Refreshing access token")
    if not refresh_token:
        raise UnauthorizedError("Refresh token missing")
    db_token = await get_refresh_token(db, refresh_token, joined_load=True)
    if not db_token:
        raise UnauthorizedError("Invalid or expired refresh token")
    user = db_token.user
    if not user:
        raise UnauthorizedError("User not found")
    access_token = create_access_token(user)
    new_refresh_token = create_refresh_token()
    await store_refresh_token(db, db_token.user_id, new_refresh_token)
    await delete_refresh_token(db, refresh_token)  # Ротация
    set_refresh_cookie(response, new_refresh_token)
    logger.info("Access token refreshed", extra={"user_id": db_token.user_id})
    return TokenSchema(access_token=access_token)


async def logout_user(db: AsyncSession, refresh_token: str | None, response: Response) -> dict:
    """Бизнес-логика логаута: удаление токена и cookie."""
    logger.info("Logging out user")
    if not refresh_token:
        raise UnauthorizedError("Refresh token missing")
    await delete_refresh_token(db, refresh_token)
    response.delete_cookie("refresh_token", path="/")
    logger.info("User logged out")
    return {"detail": "Logged out"}
