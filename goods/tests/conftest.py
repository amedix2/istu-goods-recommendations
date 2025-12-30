import logging
import sys
import os
from typing import AsyncGenerator
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy import delete
from sqlalchemy.pool import StaticPool
from asgi_lifespan import LifespanManager

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.config import settings as app_settings
from app.database import Base, get_session
from app.main import app
from app.models import Product, Review

# Настройка тестового окружения
app_settings.DB_USER = "test"
app_settings.DB_PASSWORD = "test"
app_settings.DB_HOST = "localhost"
app_settings.DB_NAME = "testdb"
app_settings.DEBUG = True
app_settings.LOG_LEVEL = logging.ERROR

# Использование SQLite в памяти для тестов
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

test_async_session_maker = async_sessionmaker(
    test_engine, expire_on_commit=False, class_=AsyncSession
)


async def override_get_session() -> AsyncGenerator[AsyncSession, None]:
    """Возвращает тестовую асинхронную сессию БД."""
    async with test_async_session_maker() as session:
        yield session


app.dependency_overrides[get_session] = override_get_session


@pytest_asyncio.fixture(autouse=True)
def override_engine(monkeypatch):
    """Подменяет движок БД в модуле database."""
    monkeypatch.setattr("app.database.engine", test_engine)


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_database():
    """Создаёт таблицы БД перед тестами и удаляет после."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function", autouse=True)
async def clear_tables():
    """Очищает таблицы данных после каждого теста."""
    yield
    async with test_async_session_maker() as session:
        async with session.begin():
            await session.execute(delete(Review))
            await session.execute(delete(Product))
        await session.commit()


@pytest_asyncio.fixture(scope="function")
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """Возвращает асинхронный HTTP-клиент."""
    async with LifespanManager(app) as manager:
        transport = ASGITransport(app=manager.app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            yield ac


@pytest_asyncio.fixture(scope="function")
async def test_product() -> Product:
    """Создаёт тестовый продукт (владелец: user_id=1)."""
    async with test_async_session_maker() as session:
        product = Product(
            user_id=1,
            name="Test Product",
            description="A generic test product",
            price=100.0,
            image_url="http://example.com/img.jpg"
        )
        session.add(product)
        await session.commit()
        await session.refresh(product)
        return product
