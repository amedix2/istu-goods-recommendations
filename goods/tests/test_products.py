import pytest
from httpx import AsyncClient


# Хедер, имитирующий Gateway
def auth_header(user_id: int):
    return {"X-Auth-User-ID": str(user_id)}


@pytest.mark.asyncio
async def test_create_product_success(async_client: AsyncClient):
    """Проверка успешного создания продукта."""
    payload = {
        "name": "New Phone",
        "description": "Latest model",
        "price": 999.99,
        "image_url": "http://img.com/1.png"
    }
    # Запрос от пользователя с ID 10
    response = await async_client.post("/", json=payload, headers=auth_header(10))

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == payload["name"]
    assert data["user_id"] == 10
    assert data["id"] is not None
    assert data["rating"] == 0.0


@pytest.mark.asyncio
async def test_create_product_unauthorized(async_client: AsyncClient):
    """Проверка создания без заголовка авторизации."""
    payload = {"name": "Test", "price": 10}
    response = await async_client.post("/", json=payload)
    # Ожидаем 401, так как нет хедера X-Auth-User-ID
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_product_details(async_client: AsyncClient, test_product):
    """Проверка получения деталей продукта."""
    response = await async_client.get(f"/{test_product.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_product.id
    assert data["name"] == "Test Product"


@pytest.mark.asyncio
async def test_get_product_not_found(async_client: AsyncClient):
    """Проверка получения несуществующего продукта."""
    response = await async_client.get("/99999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_product_owner(async_client: AsyncClient, test_product):
    """Владелец обновляет свой продукт."""
    update_data = {"price": 150.0, "name": "Updated Name"}
    # test_product принадлежит user_id=1
    response = await async_client.put(
        f"/{test_product.id}",
        json=update_data,
        headers=auth_header(1)
    )
    assert response.status_code == 200
    data = response.json()
    assert data["price"] == 150.0
    assert data["name"] == "Updated Name"


@pytest.mark.asyncio
async def test_update_product_forbidden(async_client: AsyncClient, test_product):
    """Другой пользователь пытается обновить чужой продукт."""
    update_data = {"price": 50.0}
    # Попытка обновления от user_id=2 (владелец - 1)
    response = await async_client.put(
        f"/{test_product.id}",
        json=update_data,
        headers=auth_header(2)
    )
    assert response.status_code == 403
    assert response.json()["error"] == "ForbiddenError"


@pytest.mark.asyncio
async def test_delete_product_owner(async_client: AsyncClient, test_product):
    """Владелец удаляет продукт."""
    response = await async_client.delete(
        f"/{test_product.id}",
        headers=auth_header(1)
    )
    assert response.status_code == 200

    # Проверяем, что продукт удален
    check_resp = await async_client.get(f"/{test_product.id}")
    assert check_resp.status_code == 404


@pytest.mark.asyncio
async def test_list_products(async_client: AsyncClient, test_product):
    """Проверка получения списка продуктов."""
    response = await async_client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["id"] == test_product.id
