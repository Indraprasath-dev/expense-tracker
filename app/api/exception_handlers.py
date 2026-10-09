import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.exceptions import AppException

logger = logging.getLogger(__name__)

HTTP_ERROR_CODES = {404: "not_found", 405: "method_not_allowed"}


def _error_response(
    status_code: int, code: str, message: str, headers: dict[str, str] | None = None
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"error": {"code": code, "message": message}},
        headers=headers,
    )


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    return _error_response(exc.status_code, exc.code, exc.message)


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    problems = []
    for error in exc.errors():
        if error["type"] == "json_invalid":
            problems.append("Request body is not valid JSON.")
            continue
        if error["type"] == "missing" and tuple(error["loc"]) == ("body",):
            problems.append("Request body is required.")
            continue
        field = ".".join(str(part) for part in error["loc"][1:])
        reason = error["msg"].removeprefix("Value error, ").removeprefix("Assertion failed, ")
        problems.append(f"{field}: {reason}" if field else reason)
    return _error_response(422, "validation_error", "; ".join(problems))


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """Errors FastAPI raises by itself: unknown URL (404), wrong method (405) and so on."""
    code = HTTP_ERROR_CODES.get(exc.status_code, "http_error")
    return _error_response(exc.status_code, code, str(exc.detail), headers=exc.headers)


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Anything unexpected (500). The details stay on the server, not in the response."""
    logger.exception(
        "Unhandled %s while processing %s %s", type(exc).__name__, request.method, request.url.path
    )
    return _error_response(500, "internal_error", "Something went wrong.")


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)
