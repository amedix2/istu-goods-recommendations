import pytest
from httpx import AsyncClient
from app.utils.auth import decode_access_token


@pytest.mark.asyncio
async def test_register_success(async_client: AsyncClient):
    """Проверка успешной регистрации нового пользователя."""
    user_data = {"username": "testuser", "password": "testpass"}
    response = await async_client.post("/api/auth/register", json=user_data)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in response.cookies
    payload = decode_access_token(data["access_token"])
    assert payload["sub"] == "1"  # Первый пользователь
    assert payload["role"] == "user"


@pytest.mark.asyncio
async def test_register_duplicate_username(async_client: AsyncClient):
    """Проверка регистрации с существующим именем пользователя."""
    user_data = {"username": "testuser", "password": "testpass"}
    await async_client.post("/api/auth/register", json=user_data)
    response = await async_client.post("/api/auth/register", json=user_data)
    assert response.status_code == 401
    assert response.json()["error"] == "InvalidCredentials"
    assert response.json()["detail"] == "Username already exists"


@pytest.mark.asyncio
async def test_login_success(async_client: AsyncClient):
    """Проверка успешного входа зарегистрированного пользователя."""
    user_data = {"username": "testuser", "password": "testpass"}
    await async_client.post("/api/auth/register", json=user_data)
    response = await async_client.post("/api/auth/login", json=user_data)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in response.cookies


@pytest.mark.asyncio
async def test_login_invalid_credentials(async_client: AsyncClient):
    """Проверка входа с неверными учетными данными."""
    user_data = {"username": "testuser", "password": "testpass"}
    await async_client.post("/api/auth/register", json=user_data)
    invalid_data = {"username": "testuser", "password": "wrongpass"}
    response = await async_client.post("/api/auth/login", json=invalid_data)
    assert response.status_code == 401
    assert response.json()["error"] == "InvalidCredentials"
    assert response.json()["detail"] == "Invalid username or password"


@pytest.mark.asyncio
async def test_refresh_success(async_client: AsyncClient):
    """Проверка успешного обновления access-токена с refresh-токеном."""
    user_data = {"username": "testuser", "password": "testpass"}
    await async_client.post("/api/auth/register", json=user_data)
    login_resp = await async_client.post("/api/auth/login", json=user_data)
    refresh_token = login_resp.cookies["refresh_token"]
    headers = {"Cookie": f"refresh_token={refresh_token}"}
    response = await async_client.post("/api/auth/refresh", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    new_refresh = response.cookies["refresh_token"]
    assert new_refresh != refresh_token


@pytest.mark.asyncio
async def test_refresh_missing_token(async_client: AsyncClient):
    """Проверка обновления токена без предоставленного refresh-токена."""
    response = await async_client.post("/api/auth/refresh")
    assert response.status_code == 401
    assert response.json()["error"] == "UnauthorizedError"
    assert response.json()["detail"] == "Refresh token missing"


@pytest.mark.asyncio
async def test_refresh_invalid_token(async_client: AsyncClient):
    """Проверка обновления токена с недействительным или просроченным refresh-токеном."""
    headers = {"Cookie": "refresh_token=invalidtoken"}
    response = await async_client.post("/api/auth/refresh", headers=headers)
    assert response.status_code == 401
    assert response.json()["error"] == "UnauthorizedError"
    assert response.json()["detail"] == "Invalid or expired refresh token"


@pytest.mark.asyncio
async def test_logout_success(async_client: AsyncClient):
    """Проверка успешного выхода пользователя и удаления refresh-токена."""
    user_data = {"username": "testuser", "password": "testpass"}
    await async_client.post("/api/auth/register", json=user_data)  # Register first
    login_resp = await async_client.post("/api/auth/login", json=user_data)
    refresh_token = login_resp.cookies["refresh_token"]
    headers = {"Cookie": f"refresh_token={refresh_token}"}
    response = await async_client.post("/api/auth/logout", headers=headers)
    assert response.status_code == 200
    assert response.json()["detail"] == "Logged out"
    assert "refresh_token" not in response.cookies


@pytest.mark.asyncio
async def test_logout_missing_token(async_client: AsyncClient):
    """Проверка выхода без предоставленного refresh-токена."""
    response = await async_client.post("/api/auth/logout")
    assert response.status_code == 401
    assert response.json()["error"] == "UnauthorizedError"
    assert response.json()["detail"] == "Refresh token missing"
