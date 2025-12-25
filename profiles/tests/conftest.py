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
from app.models import User

app_settings.DEBUG = True
app_settings.LOG_LEVEL = logging.ERROR

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Создание асинхронного тестового движка и сессий
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
async_session_maker = async_sessionmaker(
    test_engine, expire_on_commit=False, class_=AsyncSession
)


# Фикстура для переопределения сессии БД в тестах
async def override_get_session() -> AsyncGenerator[AsyncSession, None]:
    """Возвращает тестовую асинхронную сессию БД."""
    async with async_session_maker() as session:
        yield session


app.dependency_overrides[get_session] = override_get_session


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_database():
    """Создаёт и удаляет таблицы БД перед и после всех тестов."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function", autouse=True)
async def clear_tables():
    """Очищает таблицу User после каждого теста."""
    yield
    async with async_session_maker() as session:
        async with session.begin():
            await session.execute(delete(User))
        await session.commit()


@pytest_asyncio.fixture(scope="function")
async def async_client(monkeypatch) -> AsyncGenerator[AsyncClient, None]:
    """Возвращает асинхронный HTTP-клиент для тестирования FastAPI с запущенным lifespan."""

    async def no_setup():
        pass

    monkeypatch.setattr("app.main.setup_database", no_setup)

    async with LifespanManager(app) as manager:
        transport = ASGITransport(app=manager.app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            yield ac


@pytest_asyncio.fixture(scope="function")
async def test_user() -> User:
    """Создаёт и возвращает тестового пользователя в БД."""
    async with async_session_maker() as session:
        user = User(
            user_id=1,
            username="testuser",
            display_name="Test User",
            email="test@example.com",
            description="Test description",
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user
