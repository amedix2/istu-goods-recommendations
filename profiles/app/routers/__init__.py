from fastapi import APIRouter

from app.routers.profiles import router as profiles_router

main_router = APIRouter(prefix="/profile")  # главный роутер

main_router.include_router(profiles_router, tags=["users"])
