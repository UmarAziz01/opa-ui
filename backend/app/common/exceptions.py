import logging
from typing import Any, Dict, Optional
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.common.utils import current_epoch

logger = logging.getLogger(__name__)


# ── Custom Domain Exception Classes ───────────────────────────────────────────

class AppException(Exception):
    """Base exception class untuk semua domain exception aplikasi OPA UI."""
    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        error_code: str = "BAD_REQUEST",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}


class EntityNotFoundException(AppException):
    def __init__(self, entity_name: str, identifier: Any):
        super().__init__(
            message=f"{entity_name} dengan ID/identitas '{identifier}' tidak ditemukan.",
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="ENTITY_NOT_FOUND",
        )


class PermissionDeniedException(AppException):
    def __init__(self, message: str = "Akses ditolak. Anda tidak memiliki izin untuk resource ini."):
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            error_code="FORBIDDEN_ACCESS",
        )


class ConflictException(AppException):
    def __init__(self, message: str):
        super().__init__(
            message=message,
            status_code=status.HTTP_409_CONFLICT,
            error_code="RESOURCE_CONFLICT",
        )


class TrialExpiredException(AppException):
    def __init__(self, tenant_slug: str):
        super().__init__(
            message=f"Masa percobaan tenant '{tenant_slug}' telah kedaluwarsa.",
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            error_code="TRIAL_EXPIRED",
        )


# ── Centralized Exception Handlers ────────────────────────────────────────────

def register_exception_handlers(app: FastAPI) -> None:
    """Mendaftarkan handler exception terpusat ke instance FastAPI."""

    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "status": "error",
                "error_code": exc.error_code,
                "message": exc.message,
                "details": exc.details,
                "timestamp": current_epoch(),
                "path": request.url.path,
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "status": "error",
                "error_code": "VALIDATION_ERROR",
                "message": "Payload atau parameter input tidak valid.",
                "details": exc.errors(),
                "timestamp": current_epoch(),
                "path": request.url.path,
            },
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        logger.exception("Unhandled Server Exception pada %s: %s", request.url.path, exc)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "status": "error",
                "error_code": "INTERNAL_SERVER_ERROR",
                "message": "Terjadi kesalahan internal server.",
                "details": {},
                "timestamp": current_epoch(),
                "path": request.url.path,
            },
        )