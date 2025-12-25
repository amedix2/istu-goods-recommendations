import logging
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.exc import IntegrityError

from app.config import settings

logger = logging.getLogger(__name__)

# URL для подключения к PostgreSQL
DATABASE_URL = (
    f"postgresql+asyncpg://{settings.DB_USER}:"
    f"{settings.DB_PASSWORD}@{settings.DB_HOST}:"
    f"{settings.DB_PORT}/{settings.DB_NAME}"
)

engine = create_async_engine(
    DATABASE_URL,
    pool_size=settings.POOL_SIZE,
    max_overflow=settings.MAX_OVERFLOW,
    pool_timeout=settings.POOL_TIMEOUT,
    pool_recycle=settings.POOL_RECYCLE,
)

async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


async def get_session() -> AsyncSession:
    """Генератор асинхронной сессии для работы с БД."""
    logger.debug("Opening database session")
    async with async_session_maker() as session:
        yield session
    logger.debug("Database session closed")


async def setup_database():
    """Создаёт все таблицы в базе данных на основе моделей."""
    logger.info("Setting up database tables")
    async with engine.begin() as conn:
        try:
            await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables created successfully")
        except IntegrityError as e:
            logger.warning("IntegrityError during table creation", extra={"error": str(e)})
            pass


class Base(DeclarativeBase):
    """Базовый класс для всех моделей SQLAlchemy."""
    pass
