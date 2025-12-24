import logging
from fastapi import Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError


class DatabaseServiceError(Exception):
    """Базовое исключение для ошибок сервиса базы данных."""
    pass


class InvalidCredentials(DatabaseServiceError):
    """Ошибка при неверных учетных данных пользователя."""

    def __init__(self, message="Invalid credentials"):
        self.message = message
        super().__init__(self.message)


class UnauthorizedError(DatabaseServiceError):
    """Ошибка при попытке неавторизованного доступа."""

    def __init__(self, message="Unauthorized"):
        self.message = message
        super().__init__(self.message)


class ServiceNotFoundError(DatabaseServiceError):
    """Ошибка, если запрашиваемый сервис не найден."""

    def __init__(self, message="Service not found"):
        self.message = message
        super().__init__(self.message)


class ServiceUnavailableError(DatabaseServiceError):
    """Ошибка при недоступности сервиса."""

    def __init__(self, message="Service unavailable"):
        self.message = message
        super().__init__(self.message)


# Обработчики исключений для FastAPI
async def invalid_credentials_handler(request: Request, exc: InvalidCredentials):
    """Возвращает 401 при неверных учетных данных."""
    logging.warning(f"401 Unauthorized", extra={"url": str(request.url), "exception": str(exc.message)})
    return JSONResponse(
        status_code=401,
        content={
            "detail": exc.message,
            "error": "InvalidCredentials",
            "path": str(request.url),
        },
    )


async def unauthorized_handler(request: Request, exc: UnauthorizedError):
    """Возвращает 401 при неавторизованном доступе."""
    logging.warning(f"401 Unauthorized", extra={"url": str(request.url), "exception": str(exc.message)})
    return JSONResponse(
        status_code=401,
        content={
            "detail": exc.message,
            "error": "UnauthorizedError",
            "path": str(request.url),
        },
    )


async def service_not_found_handler(request: Request, exc: ServiceNotFoundError):
    """Возвращает 404, если сервис не найден."""
    logging.warning(f"404 Not Found", extra={"url": str(request.url), "exception": str(exc.message)})
    return JSONResponse(
        status_code=404,
        content={
            "detail": exc.message,
            "error": "ServiceNotFoundError",
            "path": str(request.url),
        },
    )


async def service_unavailable_handler(request: Request, exc: ServiceUnavailableError):
    """Возвращает 503, если сервис недоступен."""
    logging.warning(f"503 Service Unavailable", extra={"url": str(request.url), "exception": str(exc.message)})
    return JSONResponse(
        status_code=503,
        content={
            "detail": exc.message,
            "error": "ServiceUnavailableError",
            "path": str(request.url),
        },
    )


async def sql_error_handler(request: Request, exc: SQLAlchemyError):
    """Возвращает 500 при ошибке работы с базой данных."""
    logging.error(f"500 Database error", extra={"url": str(request.url), "exception": str(exc)})
    return JSONResponse(
        status_code=500,
        content={
            "detail": str(exc),
            "error": "Database error",
            "path": str(request.url),
        },
    )
