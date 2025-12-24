import logging
import sys
import os
from typing import AsyncGenerator
from datetime import datetime, timedelta, timezone
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
from app.models import RefreshToken, User
from app.utils.auth import get_password_hash

# Настройка тестовых значений
app_settings.MICRO_SERVICES = {"mock_service": "http://mock_service:8000"}
app_settings.JWT_SECRET_KEY = "testsecretkeyatleast32charslong1234567890"
app_settings.DEBUG = True
app_settings.LOG_LEVEL = logging.ERROR

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Создание асинхронного тестового движка и сессий
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
test_async_session_maker = async_sessionmaker(
    test_engine, expire_on_commit=False, class_=AsyncSession
)


# Фикстура для переопределения сессии БД в тестах
async def override_get_session() -> AsyncGenerator[AsyncSession, None]:
    """Возвращает тестовую асинхронную сессию БД."""
    async with test_async_session_maker() as session:
        yield session


app.dependency_overrides[get_session] = override_get_session


@pytest_asyncio.fixture(autouse=True)
def override_engine(monkeypatch):
    monkeypatch.setattr("app.database.engine", test_engine)


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
    """Очищает таблицы RefreshToken и User после каждого теста."""
    yield
    async with test_async_session_maker() as session:
        async with session.begin():
            await session.execute(delete(RefreshToken))
            await session.execute(delete(User))
        await session.commit()


@pytest_asyncio.fixture(scope="function")
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """Возвращает асинхронный HTTP-клиент для тестирования FastAPI с запущенным lifespan."""
    async with LifespanManager(
            app
    ) as manager:  # Запускаем lifespan для установки app.state
        transport = ASGITransport(app=manager.app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            yield ac


@pytest_asyncio.fixture(scope="function")
async def test_user() -> User:
    """Создаёт и возвращает тестового пользователя в БД."""
    async with test_async_session_maker() as session:
        user = User(
            username="existinguser",
            hashed_password=get_password_hash("testpassword"),
            role="user",
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user


@pytest_asyncio.fixture(scope="function")
async def test_refresh_token(test_user: User) -> RefreshToken:
    """Создаёт и возвращает тестовый refresh-токен для пользователя."""
    async with test_async_session_maker() as session:
        expire = datetime.now(timezone.utc) + timedelta(days=7)
        token = RefreshToken(
            user_id=test_user.id, token="testrefreshtoken", expires_at=expire
        )
        session.add(token)
        await session.commit()
        await session.refresh(token)
        return token
