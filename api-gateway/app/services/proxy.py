import aiohttp
from fastapi import Request

from app.exceptions import ServiceNotFoundError, ServiceUnavailableError
from app.config import settings
import logging

logger = logging.getLogger(__name__)

REQUEST_HEADERS_WHITELIST = {
    "content-type",
    "content-length",
    "accept",
    "accept-encoding",
    "user-agent",
    "cache-control",
    "x-request-id",
}

RESPONSE_HEADERS_BLACKLIST = {
    "set-cookie",
    "connection",
    "transfer-encoding",
}


async def proxy_request(
        service_name: str, path: str, request: Request, payload: dict | None
) -> tuple[int, bytes, dict]:
    """Перенаправляет HTTP-запрос к микросервису и возвращает ответ."""
    logger.debug("Proxying request", extra={"service_name": service_name, "path": path, "method": request.method})
    service_url = settings.MICRO_SERVICES.get(service_name)
    if not service_url:
        raise ServiceNotFoundError(f"Service {service_name} not found")

    url = f"{service_url}/{path}"
    headers = {
        k: v
        for k, v in request.headers.items()
        if k.lower() in REQUEST_HEADERS_WHITELIST
    }

    if payload:
        headers["X-Auth-User-ID"] = str(payload["sub"])
        headers["X-Auth-User-Role"] = payload["role"]

    body = await request.body()
    session = request.app.state.aiohttp_session
    try:
        async with session.request(
                method=request.method,
                url=url,
                headers=headers,
                params=request.query_params,
                data=body if body else None,
        ) as r:
            content = await r.read()
            logger.debug("Proxy response received", extra={"status": r.status, "service_name": service_name})
            response_headers = {
                k: v for k, v in r.headers.items()
                if k.lower() not in RESPONSE_HEADERS_BLACKLIST
            }
            return r.status, content, response_headers
    except (aiohttp.ClientConnectorError, aiohttp.ClientOSError, aiohttp.client_exceptions.ServerDisconnectedError):
        raise ServiceUnavailableError(f"Service {service_name} is unavailable")
