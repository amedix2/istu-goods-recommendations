import pytest
from httpx import AsyncClient
from unittest.mock import patch, AsyncMock, MagicMock
import aiohttp
from app.utils.auth import decode_access_token


@pytest.mark.asyncio
@patch("app.services.proxy.aiohttp.ClientSession.request")
async def test_proxy_with_valid_token(mock_request, async_client: AsyncClient):
    """Проверка проксирования запроса с валидным access-токеном."""
    mock_response = MagicMock()
    mock_response.status = 200
    mock_response.read = AsyncMock(return_value=b"mock response")
    mock_response.headers = {"Content-Type": "text/plain"}

    mock_context = MagicMock()
    mock_context.__aenter__ = AsyncMock(return_value=mock_response)
    mock_context.__aexit__ = AsyncMock(return_value=False)
    mock_request.return_value = mock_context

    # Регистрация и логин для получения токена
    user_data = {"username": "proxyuser", "password": "testpass"}
    reg_resp = await async_client.post("/api/auth/register", json=user_data)
    user_id = decode_access_token(reg_resp.json()["access_token"])["sub"]

    login_resp = await async_client.post("/api/auth/login", json=user_data)
    access_token = login_resp.json()["access_token"]

    # Проксирование запроса с токеном
    headers = {"Authorization": f"Bearer {access_token}"}
    response = await async_client.get("/api/mock_service/some/path", headers=headers)
    assert response.status_code == 200
    assert response.content == b"mock response"

    # Проверка заголовков пользователя
    called_args = mock_request.call_args.kwargs
    assert called_args["headers"]["X-Auth-User-ID"] == user_id
    assert called_args["headers"]["X-Auth-User-Role"] == "user"
    assert "authorization" not in {k.lower() for k in called_args["headers"]}


@pytest.mark.asyncio
@patch("app.services.proxy.aiohttp.ClientSession.request")
async def test_proxy_without_token(mock_request, async_client: AsyncClient):
    """Проверка проксирования запроса без токена (анонимный доступ)."""
    mock_response = MagicMock()
    mock_response.status = 200
    mock_response.read = AsyncMock(return_value=b"no auth response")
    mock_response.headers = {"Content-Type": "text/plain"}

    mock_context = MagicMock()
    mock_context.__aenter__ = AsyncMock(return_value=mock_response)
    mock_context.__aexit__ = AsyncMock(return_value=False)
    mock_request.return_value = mock_context

    response = await async_client.get("/api/mock_service/noauth/path")
    assert response.status_code == 200
    assert response.content == b"no auth response"

    # Заголовки пользователя отсутствуют
    called_args = mock_request.call_args.kwargs
    assert "X-Auth-User-ID" not in called_args["headers"]
    assert "X-Auth-User-Role" not in called_args["headers"]


@pytest.mark.asyncio
@patch("app.services.proxy.aiohttp.ClientSession.request")
async def test_proxy_invalid_token(mock_request, async_client: AsyncClient):
    """Проверка проксирования с недействительным токеном (доступ запрещён)."""
    headers = {"Authorization": "Bearer invalidtoken"}
    response = await async_client.get("/api/mock_service/path", headers=headers)
    assert response.status_code == 401
    assert response.json()["error"] == "UnauthorizedError"
    assert response.json()["detail"] == "Invalid token"
    mock_request.assert_not_called()


@pytest.mark.asyncio
@patch("app.services.proxy.aiohttp.ClientSession.request")
async def test_proxy_service_not_found(mock_request, async_client: AsyncClient):
    """Проверка запроса к несуществующему сервису (404)."""
    response = await async_client.get("/api/unknown_service/path")
    assert response.status_code == 404
    assert response.json()["error"] == "ServiceNotFoundError"
    assert response.json()["detail"] == "Service unknown_service not found"
    mock_request.assert_not_called()


@pytest.mark.asyncio
@patch("app.services.proxy.aiohttp.ClientSession.request")
async def test_proxy_service_unavailable(mock_request, async_client: AsyncClient):
    """Проверка недоступного сервиса (503)."""
    mock_request.side_effect = aiohttp.ClientConnectorError(
        connection_key=None, os_error=OSError("Connection failed")
    )

    response = await async_client.get("/api/mock_service/path")
    assert response.status_code == 503
    assert response.json()["error"] == "ServiceUnavailableError"
    assert response.json()["detail"] == "Service mock_service is unavailable"


@pytest.mark.asyncio
@patch("app.services.proxy.aiohttp.ClientSession.request")
async def test_proxy_different_methods(mock_request, async_client: AsyncClient):
    """Проверка проксирования POST-запроса с передачей данных."""
    mock_response = MagicMock()
    mock_response.status = 201
    mock_response.read = AsyncMock(return_value=b"created")
    mock_response.headers = {}

    mock_context = MagicMock()
    mock_context.__aenter__ = AsyncMock(return_value=mock_response)
    mock_context.__aexit__ = AsyncMock(return_value=False)
    mock_request.return_value = mock_context

    response = await async_client.post(
        "/api/mock_service/create", json={"data": "test"}
    )
    assert response.status_code == 201
    assert mock_request.call_args.kwargs["method"] == "POST"
    request_data = mock_request.call_args.kwargs["data"]
    assert request_data == b'{"data":"test"}'


@pytest.mark.asyncio
async def test_proxy_integration_register_to_proxy(async_client: AsyncClient):
    """Интеграционный тест: регистрация пользователя и проксирование с токеном."""
    user_data = {"username": "integrateuser", "password": "integratepass"}
    reg_resp = await async_client.post("/api/auth/register", json=user_data)
    access_token = reg_resp.json()["access_token"]
    payload = decode_access_token(access_token)
    user_id = payload["sub"]

    # Патчим proxied-запрос
    with patch("app.services.proxy.aiohttp.ClientSession.request") as mock_request:
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.read = AsyncMock(return_value=b"user matched")
        mock_response.headers = {}

        mock_context = MagicMock()
        mock_context.__aenter__ = AsyncMock(return_value=mock_response)
        mock_context.__aexit__ = AsyncMock(return_value=False)
        mock_request.return_value = mock_context

        headers = {"Authorization": f"Bearer {access_token}"}
        response = await async_client.get("/api/mock_service/secure", headers=headers)
        assert response.status_code == 200
        called_headers = mock_request.call_args.kwargs["headers"]
        assert called_headers["X-Auth-User-ID"] == user_id
        assert called_headers["X-Auth-User-Role"] == "user"
