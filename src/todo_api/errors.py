"""Error model: one place that produces the contract's error body."""

from __future__ import annotations

import structlog
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from todo_api.metrics import ERROR_COUNT

MSG_TITLE_REQUIRED = "Title is required"
MSG_TITLE_TOO_LONG = "Title must be at most 200 characters"
MSG_INVALID_REQUEST = "Request body is invalid"
MSG_TODO_NOT_FOUND = "This todo no longer exists"
MSG_UNAVAILABLE = "Todos are unavailable, please try again"

_GENERIC_CODES = {
    404: ("not_found", "Not found"),
    405: ("method_not_allowed", "Method not allowed"),
}

logger = structlog.get_logger()


class ApiError(Exception):
    """An error answered with the contract's body."""

    def __init__(self, status: int, code: str, message: str) -> None:
        super().__init__(message)
        self.status = status
        self.code = code
        self.message = message


class DatabaseUnavailable(Exception):  # noqa: N818
    """The database could not be reached within the deadline."""


def error_response(status: int, code: str, message: str) -> JSONResponse:
    return JSONResponse(status_code=status, content={"error": {"code": code, "message": message}})


async def _api_error(_: Request, exc: Exception) -> JSONResponse:
    if not isinstance(exc, ApiError):
        raise exc
    return error_response(exc.status, exc.code, exc.message)


async def _unavailable(_: Request, __: Exception) -> JSONResponse:
    ERROR_COUNT.labels(error_type="database_unavailable").inc()
    return error_response(503, "unavailable", MSG_UNAVAILABLE)


async def _validation(_: Request, __: Exception) -> JSONResponse:
    return error_response(422, "invalid_request", MSG_INVALID_REQUEST)


async def _http_exception(_: Request, exc: Exception) -> JSONResponse:
    if not isinstance(exc, StarletteHTTPException):
        raise exc
    code, message = _GENERIC_CODES.get(exc.status_code, ("http_error", "Request failed"))
    return error_response(exc.status_code, code, message)


async def _unexpected(_: Request, exc: Exception) -> JSONResponse:
    ERROR_COUNT.labels(error_type="internal_error").inc()
    logger.error("unhandled_exception", error=type(exc).__name__, exc_info=exc)
    return error_response(500, "internal_error", "Internal server error")


def install_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(ApiError, _api_error)
    app.add_exception_handler(DatabaseUnavailable, _unavailable)
    app.add_exception_handler(RequestValidationError, _validation)
    app.add_exception_handler(StarletteHTTPException, _http_exception)
    app.add_exception_handler(Exception, _unexpected)
