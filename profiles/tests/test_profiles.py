import pytest
from httpx import AsyncClient
from app.models import User
from conftest import async_session_maker


@pytest.mark.asyncio
async def test_create_profile_success(async_client: AsyncClient):
    """Проверка успешного создания профиля."""
    user_data = {
        "username": "newuser",
        "display_name": "New User",
        "email": "new@example.com",
        "description": "New description",
    }
    headers = {"X-Auth-User-ID": "2"}  # Новый user_id
    response = await async_client.post("/profile/", json=user_data, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == 2
    assert data["username"] == "newuser"


@pytest.mark.asyncio
async def test_create_profile_conflict(async_client: AsyncClient, test_user: User):
    """Проверка создания профиля с конфликтующими данными (дубликат username)."""
    user_data = {
        "username": "testuser",  # Уже существует
        "display_name": "Test User",
        "email": "new@example.com",
    }
    headers = {"X-Auth-User-ID": "2"}
    response = await async_client.post("/profile/", json=user_data, headers=headers)
    assert response.status_code == 409
    assert response.json()["error"] == "ConflictError"


@pytest.mark.asyncio
async def test_get_profile_self_success(async_client: AsyncClient, test_user: User):
    """Проверка получения своего полного профиля."""
    headers = {"X-Auth-User-ID": "1"}
    response = await async_client.get("/profile/", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == 1


@pytest.mark.asyncio
async def test_get_profile_self_not_found(async_client: AsyncClient):
    """Проверка получения своего профиля, если он не существует."""
    headers = {"X-Auth-User-ID": "999"}
    response = await async_client.get("/profile/", headers=headers)
    assert response.status_code == 404
    assert response.json()["error"] == "NotFoundError"


@pytest.mark.asyncio
async def test_get_profile_success(async_client: AsyncClient, test_user: User):
    """Проверка получения полного профиля другого пользователя."""
    response = await async_client.get("/profile/1")
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == 1


@pytest.mark.asyncio
async def test_get_profile_not_found(async_client: AsyncClient):
    """Проверка получения несуществующего профиля."""
    response = await async_client.get("/profile/999")
    assert response.status_code == 404
    assert response.json()["error"] == "NotFoundError"


@pytest.mark.asyncio
async def test_update_profile_self_success(async_client: AsyncClient, test_user: User):
    """Проверка успешного обновления своего профиля."""
    update_data = {"display_name": "Updated Name", "description": "Updated desc"}
    headers = {"X-Auth-User-ID": "1"}
    response = await async_client.put("/profile/", json=update_data, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["display_name"] == "Updated Name"
    assert data["description"] == "Updated desc"


@pytest.mark.asyncio
async def test_update_profile_self_not_found(async_client: AsyncClient):
    """Проверка обновления несуществующего профиля."""
    update_data = {"display_name": "Update"}
    headers = {"X-Auth-User-ID": "999"}
    response = await async_client.put("/profile/", json=update_data, headers=headers)
    assert response.status_code == 404
    assert response.json()["error"] == "NotFoundError"


@pytest.mark.asyncio
async def test_update_profile_self_no_fields(async_client: AsyncClient, test_user: User):
    """Проверка обновления без полей."""
    update_data = {}
    headers = {"X-Auth-User-ID": "1"}
    response = await async_client.put("/profile/", json=update_data, headers=headers)
    assert response.status_code == 409
    assert response.json()["error"] == "ConflictError"


@pytest.mark.asyncio
async def test_update_profile_self_conflict(async_client: AsyncClient, test_user: User):
    """Проверка обновления с конфликтующими данными (дубликат email)."""
    async with async_session_maker() as session:
        user2 = User(
            user_id=2,
            username="user2",
            display_name="User2",
            email="user2@example.com",
        )
        session.add(user2)
        await session.commit()

    update_data = {"email": "user2@example.com"}  # Конфликт
    headers = {"X-Auth-User-ID": "1"}
    response = await async_client.put("/profile/", json=update_data, headers=headers)
    assert response.status_code == 409
    assert response.json()["error"] == "ConflictError"


@pytest.mark.asyncio
async def test_delete_profile_self_success(async_client: AsyncClient, test_user: User):
    """Проверка успешного удаления своего профиля."""
    headers = {"X-Auth-User-ID": "1"}
    response = await async_client.delete("/profile/", headers=headers)
    assert response.status_code == 200
    assert response.json()["detail"] == "User deleted"


@pytest.mark.asyncio
async def test_delete_profile_self_not_found(async_client: AsyncClient):
    """Проверка удаления несуществующего профиля."""
    headers = {"X-Auth-User-ID": "999"}
    response = await async_client.delete("/profile/", headers=headers)
    assert response.status_code == 404
    assert response.json()["error"] == "NotFoundError"
