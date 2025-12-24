import aiohttp
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import setup_database, engine
from app.routers import main_router
from app.config import settings
from app.exceptions import *
from app.logs import setup_logging

setup_logging(debug=settings.DEBUG, level=settings.LOG_LEVEL, exclude_extra_fields=["message", "asctime"])
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Настройка жизненного цикла приложения: инициализация и завершение работы БД."""
    safe_settings = settings.model_dump(exclude={"DB_PASSWORD", "JWT_SECRET_KEY", "DB_USER"})
    logger.info("Loaded settings from .env", extra={"settings": safe_settings})

    logger.info("Application startup: Initializing aiohttp session")
    app.state.aiohttp_session = aiohttp.ClientSession(
        timeout=aiohttp.ClientTimeout(total=settings.TOTAL_TIMEOUT))
    await setup_database()  # создаём таблицы в базе при старте
    logger.info(f"Application startup complete.")
    if settings.DEBUG:
        host = "127.0.0.1" if settings.HOST == "0.0.0.0" else settings.HOST
        logger.info(f"Docs on http://{host}:{settings.PORT}/docs")

    yield

    logger.info("Application shutdown: Closing aiohttp session")
    await app.state.aiohttp_session.close()
    await engine.dispose()  # закрываем соединение с базой при остановке
    logger.info("Application shutdown complete")


app = FastAPI(lifespan=lifespan)

# Настройка CORS middleware для разрешённых источников
if not settings.DEBUG and settings.ALLOWED_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,  # список разрешённых доменов
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    logger.warning("CORS disabled")

app.include_router(main_router)

# Подключаем обработчики исключений для FastAPI
app.add_exception_handler(InvalidCredentials, invalid_credentials_handler)
app.add_exception_handler(UnauthorizedError, unauthorized_handler)
app.add_exception_handler(ServiceNotFoundError, service_not_found_handler)
app.add_exception_handler(SQLAlchemyError, sql_error_handler)
app.add_exception_handler(ServiceUnavailableError, service_unavailable_handler)
