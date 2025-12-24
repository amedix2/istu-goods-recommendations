import logging
from fastapi import APIRouter, Depends, Request, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from asyncio import to_thread

from app.utils.auth import decode_access_token
from app.services.proxy import proxy_request

logger = logging.getLogger(__name__)

router = APIRouter()

security = HTTPBearer(auto_error=False)


@router.api_route(
    "/{service_name}/{path:path}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"],
    include_in_schema=False
)
async def proxy(
        service_name: str,
        path: str,
        request: Request,
        credentials: HTTPAuthorizationCredentials | None = Depends(security)
):
    """Прокси-эндпоинт, который перенаправляет запросы на нужный сервис"""
    logger.info("Proxy endpoint called", extra={"service_name": service_name, "path": path, "method": request.method})
    token = credentials.credentials if credentials else None
    payload = None
    if token:
        payload = await to_thread(decode_access_token, token)
    status, content, headers = await proxy_request(service_name, path, request, payload)
    logger.info("Proxy response", extra={"status": status})
    return Response(content=content, status_code=status, headers=headers)
