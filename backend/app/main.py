import time
import logging
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import close_db_connection
from app.core.logging_config import setup_logging
from app.core.storage import ensure_bucket

from app.common.exceptions import register_exception_handlers

from app.workers.trial_checker import start_trial_checker_loop

from app.modules.auth.router import router as auth_router
from app.modules.tenants.router import router as tenant_router
from app.modules.organizations.router import router as orgs_router
from app.modules.audit.router import router as audit_router
from app.modules.bundles.router import router as bundle_router
from app.modules.governance.router import router as governance_router
from app.modules.policies.router import router as policies_router
from app.modules.applications.router import router as application_router

from app.modules.bundles.router import router as bundles_router

logger = logging.getLogger("app.main")

@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    logger.info(
        f"Server OPA UI Backend berjalan di env: [{settings.APP_ENV}] | Debug: {settings.DEBUG}"
    )
    await ensure_bucket()
    logger.info(
        f"Bucket ditemukan"
    )
    trial_task = asyncio.create_task(start_trial_checker_loop(interval_seconds=3600))
    yield
    trial_task.cancel()
    try:
        await trial_task
    except asyncio.CancelledError:
        pass

    await close_db_connection()
    logger.info("Server OPA UI Backend mematikan koneksi...")

app = FastAPI(
    title="OPA UI Multi-Tenant Authz Engine",
    version="1.0.0",
    docs_url=f"{settings.API_V1_PREFIX}/docs" if settings.DEBUG else None,
    redoc_url=None,
    lifespan=lifespan,
)

register_exception_handlers(app)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware HTTP Request/Response Logger
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration_ms = round((time.time() - start_time) * 1000, 2)

    logger.info(
        f"HTTP {request.method} {request.url.path} - Status: {response.status_code} - {duration_ms}ms"
    )
    return response

@app.get("/health", tags=["System"])
async def health_check():
    return {
        "status": "healthy",
        "env": settings.APP_ENV,
        "debug": settings.DEBUG,
    }


app.include_router(auth_router, prefix=settings.API_V1_PREFIX)
app.include_router(tenant_router, prefix=settings.API_V1_PREFIX)
app.include_router(orgs_router, prefix=settings.API_V1_PREFIX)
app.include_router(audit_router, prefix=settings.API_V1_PREFIX)
app.include_router(bundle_router, prefix=settings.API_V1_PREFIX)
app.include_router(governance_router, prefix=settings.API_V1_PREFIX)
app.include_router(policies_router, prefix=settings.API_V1_PREFIX)
app.include_router(application_router, prefix=settings.API_V1_PREFIX)