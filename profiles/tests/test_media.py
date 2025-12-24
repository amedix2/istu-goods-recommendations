import pytest
from httpx import AsyncClient
from app.models import Media, User


@pytest.mark.asyncio
async def test_add_media_success(async_client: AsyncClient, test_user: User):
    """Проверка успешного добавления медиа для аутентифицированного пользователя."""
    media_data = {
        "file_path": "new_path.jpg",
        "file_path_thumb": "new_thumb.jpg",
        "description": "New media",
        "is_avatar": False,
    }
    headers = {"X-Auth-User-ID": "1"}  # Аутентифицированный пользователь
    response = await async_client.post("/profile/media/", json=media_data, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["file_path"] == "new_path.jpg"
    assert data["user_id"] == 1


@pytest.mark.asyncio
async def test_add_media_unauthorized(async_client: AsyncClient):
    """Проверка добавления медиа без аутентификации."""
    media_data = {"file_path": "path.jpg"}
    response = await async_client.post("/profile/media/", json=media_data)
    assert response.status_code == 401
    assert response.json()["error"] == "UnauthorizedError"


@pytest.mark.asyncio
async def test_add_media_conflict(async_client: AsyncClient, test_media: Media):
    """Проверка добавления медиа с конфликтующими данными (дубликат file_path)."""
    media_data = {
        "file_path": "test_path.jpg",  # Уже существует
        "file_path_thumb": "test_thumb.jpg",
    }
    headers = {"X-Auth-User-ID": "1"}
    response = await async_client.post("/profile/media/", json=media_data, headers=headers)
    assert response.status_code == 409
    assert response.json()["error"] == "ConflictError"


@pytest.mark.asyncio
async def test_update_media_success(async_client: AsyncClient, test_media: Media):
    """Проверка успешного обновления медиа."""
    update_data = {"description": "Updated description", "is_avatar": False}
    headers = {"X-Auth-User-ID": "1"}
    response = await async_client.put(f"/profile/media/{test_media.id}", json=update_data, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["description"] == "Updated description"
    assert data["is_avatar"] is False


@pytest.mark.asyncio
async def test_update_media_not_found(async_client: AsyncClient):
    """Проверка обновления несуществующего медиа."""
    update_data = {"description": "Update"}
    headers = {"X-Auth-User-ID": "1"}
    response = await async_client.put("/profile/media/999", json=update_data, headers=headers)
    assert response.status_code == 404
    assert response.json()["error"] == "NotFoundError"


@pytest.mark.asyncio
async def test_update_media_forbidden(async_client: AsyncClient, test_media: Media):
    """Проверка обновления медиа чужого пользователя."""
    update_data = {"description": "Update"}
    headers = {"X-Auth-User-ID": "2"}  # Чужой пользователь
    response = await async_client.put(f"/profile/media/{test_media.id}", json=update_data, headers=headers)
    assert response.status_code == 403
    assert response.json()["error"] == "ForbiddenError"


@pytest.mark.asyncio
async def test_update_media_no_fields(async_client: AsyncClient, test_media: Media):
    """Проверка обновления без полей."""
    update_data = {}
    headers = {"X-Auth-User-ID": "1"}
    response = await async_client.put(f"/profile/media/{test_media.id}", json=update_data, headers=headers)
    assert response.status_code == 409
    assert response.json()["error"] == "ConflictError"


@pytest.mark.asyncio
async def test_delete_media_success(async_client: AsyncClient, test_media: Media):
    """Проверка успешного удаления медиа."""
    headers = {"X-Auth-User-ID": "1"}
    response = await async_client.delete(f"/profile/media/{test_media.id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["detail"] == "Media deleted"


@pytest.mark.asyncio
async def test_delete_media_not_found(async_client: AsyncClient):
    """Проверка удаления несуществующего медиа."""
    headers = {"X-Auth-User-ID": "1"}
    response = await async_client.delete("/profile/media/999", headers=headers)
    assert response.status_code == 404
    assert response.json()["error"] == "NotFoundError"


@pytest.mark.asyncio
async def test_delete_media_forbidden(async_client: AsyncClient, test_media: Media):
    """Проверка удаления медиа чужого пользователя."""
    headers = {"X-Auth-User-ID": "2"}
    response = await async_client.delete(f"/profile/media/{test_media.id}", headers=headers)
    assert response.status_code == 403
    assert response.json()["error"] == "ForbiddenError"


@pytest.mark.asyncio
async def test_delete_media_unauthorized(async_client: AsyncClient, test_media: Media):
    """Проверка удаления медиа без аутентификации."""
    response = await async_client.delete(f"/profile/media/{test_media.id}")
    assert response.status_code == 401
    assert response.json()["error"] == "UnauthorizedError"
