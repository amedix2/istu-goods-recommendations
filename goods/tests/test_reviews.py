import pytest
from httpx import AsyncClient


def auth_header(user_id: int):
    return {"X-Auth-User-ID": str(user_id)}


@pytest.mark.asyncio
async def test_add_review_success(async_client, test_product):
    response = await async_client.post(
        f"/reviews/{test_product.id}",
        json={"rating": 5, "text": "Perfect"},
        headers=auth_header(2)
    )
    assert response.status_code == 200
    assert response.json()["rating"] == 5

    prod_resp = await async_client.get(f"/{test_product.id}")
    prod_data = prod_resp.json()
    assert prod_data["rating"] == 5.0
    assert prod_data["reviews_count"] == 1


@pytest.mark.asyncio
async def test_add_duplicate_review(async_client: AsyncClient, test_product):
    """Запрет на повторный отзыв от одного пользователя."""
    payload = {"rating": 4}
    # Первый отзыв
    await async_client.post(
        f"/reviews/{test_product.id}",
        json=payload,
        headers=auth_header(2)
    )
    # Второй отзыв от того же пользователя
    response = await async_client.post(
        f"/reviews/{test_product.id}",
        json=payload,
        headers=auth_header(2)
    )

    assert response.status_code == 409
    assert "already reviewed" in response.json()["detail"]


@pytest.mark.asyncio
async def test_add_review_invalid_rating(async_client: AsyncClient, test_product):
    """Валидация рейтинга (должен быть 1-5)."""
    payload = {"rating": 6}  # Некорректно
    response = await async_client.post(
        f"/reviews/{test_product.id}",
        json=payload,
        headers=auth_header(2)
    )
    assert response.status_code == 422  # Ошибка валидации Pydantic


@pytest.mark.asyncio
async def test_update_review(async_client, test_product):
    # 1. Создаем отзыв
    res = await async_client.post(
        f"/reviews/{test_product.id}",
        json={"rating": 2, "text": "Bad"},
        headers=auth_header(2)
    )
    review_id = res.json()["id"]

    # 2. Обновляем: PUT /reviews/{review_id}
    update_res = await async_client.put(
        f"/reviews/{review_id}",
        json={"rating": 4},
        headers=auth_header(2)
    )
    assert update_res.status_code == 200

    # 3. Проверяем продукт
    prod_data = (await async_client.get(f"/{test_product.id}")).json()
    assert prod_data["rating"] == 4.0


@pytest.mark.asyncio
async def test_update_review_forbidden(async_client: AsyncClient, test_product):
    """Попытка изменить чужой отзыв."""
    # Отзыв от user 2
    create_resp = await async_client.post(
        f"/reviews/{test_product.id}",
        json={"rating": 4},
        headers=auth_header(2)
    )
    review_id = create_resp.json()["id"]

    # User 3 пытается изменить
    response = await async_client.put(
        f"/reviews/{review_id}",
        json={"rating": 1},
        headers=auth_header(3)
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_delete_review(async_client, test_product):
    # 1. Создаем
    res = await async_client.post(f"/reviews/{test_product.id}", json={"rating": 5}, headers=auth_header(2))
    review_id = res.json()["id"]

    # 2. Удаляем: DELETE /reviews/{review_id}
    response = await async_client.delete(f"/reviews/{review_id}", headers=auth_header(2))
    assert response.status_code == 200
    assert response.json()["detail"] == "Review deleted"

    # 3. Проверяем продукт
    prod_data = (await async_client.get(f"/{test_product.id}")).json()
    assert prod_data["rating"] == 0.0


@pytest.mark.asyncio
async def test_rating_aggregation(async_client, test_product):
    await async_client.post(f"/reviews/{test_product.id}", json={"rating": 5}, headers=auth_header(2))
    await async_client.post(f"/reviews/{test_product.id}", json={"rating": 1}, headers=auth_header(3))

    prod_resp = await async_client.get(f"/{test_product.id}")
    data = prod_resp.json()

    # (5 + 1) / 2 = 3.0
    assert data["rating"] == 3.0
    assert data["reviews_count"] == 2
