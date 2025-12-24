import logging
from fastapi import Header

from app.exceptions import UnauthorizedError

logger = logging.getLogger(__name__)


def get_auth_user_id(x_auth_user_id: str | None = Header(None)) -> int | None:
    logger.debug("Getting auth user ID", extra={"header_value": x_auth_user_id})
    if x_auth_user_id is None:
        raise UnauthorizedError("Authentication required")
    try:
        user_id = int(x_auth_user_id)
        logger.debug("Auth user ID retrieved", extra={"user_id": user_id})
        return user_id
    except ValueError:
        raise UnauthorizedError("Invalid user ID format")
