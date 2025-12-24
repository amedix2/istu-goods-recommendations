import logging
from fastapi import APIRouter

from app.routers.auth import router as auth_router
from app.routers.proxy import router as proxy_router

logger = logging.getLogger(__name__)

main_router = APIRouter(prefix="/api")  # главный роутер

main_router.include_router(auth_router, prefix="/auth", tags=["auth"])  # роутер аутентефикации
main_router.include_router(proxy_router, tags=["proxy"])  # роутер прокси

logger.debug("Main router initialized with auth and proxy routers")
