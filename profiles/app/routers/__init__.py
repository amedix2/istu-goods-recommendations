from fastapi import APIRouter

from app.routers.profiles import router as profiles_router
from app.routers.media import router as media_router

main_router = APIRouter(prefix="/profile")  # главный роутер

main_router.include_router(profiles_router, tags=["users"])
main_router.include_router(media_router, prefix="/media", tags=["media"])
