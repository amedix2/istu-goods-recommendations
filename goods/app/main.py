import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.database import setup_database, engine
from app.routers import main_router
from app.exceptions import *
from app.config import settings
from app.logs import setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Настройка жизненного цикла приложения: инициализация и завершение работы БД."""
    setup_logging(debug=settings.DEBUG, level=settings.LOG_LEVEL, exclude_extra_fields=["message", "asctime"])
    logger = logging.getLogger(__name__)
    safe_settings = settings.model_dump(exclude={"DB_PASSWORD", "DB_USER"})
    logger.info("Loaded settings from .env", extra={"settings": safe_settings})

    logger.info("Application startup")
    await setup_database()  # создаём таблицы в базе при старте
    logger.info("Application startup complete")
    if settings.DEBUG:
        host = "127.0.0.1" if settings.HOST == "0.0.0.0" else settings.HOST
        logger.info(f"Docs on http://{host}:{settings.PORT}/docs")

    yield
    await engine.dispose()  # закрываем соединение с базой при остановке
    logger.info("Application shutdown complete")


app = FastAPI(lifespan=lifespan)
app.include_router(main_router)

# Подключаем обработчики исключений для FastAPI
app.add_exception_handler(UnauthorizedError, unauthorized_handler)
app.add_exception_handler(NotFoundError, not_found_handler)
app.add_exception_handler(ForbiddenError, forbidden_handler)
app.add_exception_handler(ConflictError, conflict_handler)
app.add_exception_handler(SQLAlchemyError, sql_error_handler)
