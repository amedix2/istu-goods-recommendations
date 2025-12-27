from fastapi import APIRouter

from app.routers.products import router as products_router
from app.routers.reviews import router as reviews_router

main_router = APIRouter()

main_router.include_router(products_router, tags=["products"])
main_router.include_router(reviews_router, prefix="/reviews", tags=["reviews"])
