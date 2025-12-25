import logging
from fastapi import Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError


class DatabaseServiceError(Exception):
    pass


class UnauthorizedError(DatabaseServiceError):
    def __init__(self, message="Unauthorized"):
        self.message = message
        super().__init__(self.message)


class NotFoundError(DatabaseServiceError):
    def __init__(self, message="Not found"):
        self.message = message
        super().__init__(self.message)


class ForbiddenError(DatabaseServiceError):
    def __init__(self, message="Forbidden"):
        self.message = message
        super().__init__(self.message)


class ConflictError(DatabaseServiceError):
    def __init__(self, message="Conflict"):
        self.message = message
        super().__init__(self.message)


async def unauthorized_handler(request: Request, exc: UnauthorizedError):
    logging.warning("401 Unauthorized", extra={"url": str(request.url), "exception": str(exc.message)})
    return JSONResponse(
        status_code=401,
        content={"detail": exc.message, "error": "UnauthorizedError", "path": str(request.url)},
    )


async def not_found_handler(request: Request, exc: NotFoundError):
    logging.warning("404 Not Found", extra={"url": str(request.url), "exception": str(exc.message)})
    return JSONResponse(
        status_code=404,
        content={"detail": exc.message, "error": "NotFoundError", "path": str(request.url)},
    )


async def forbidden_handler(request: Request, exc: ForbiddenError):
    logging.warning("403 Forbidden", extra={"url": str(request.url), "exception": str(exc.message)})
    return JSONResponse(
        status_code=403,
        content={"detail": exc.message, "error": "ForbiddenError", "path": str(request.url)},
    )


async def conflict_handler(request: Request, exc: ConflictError):
    logging.warning("409 Conflict", extra={"url": str(request.url), "exception": str(exc.message)})
    return JSONResponse(
        status_code=409,
        content={"detail": exc.message, "error": "ConflictError", "path": str(request.url)},
    )


async def sql_error_handler(request: Request, exc: SQLAlchemyError):
    logging.error("500 Database error", extra={"url": str(request.url), "exception": str(exc)})
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc), "error": "Database error", "path": str(request.url)},
    )
