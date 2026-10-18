from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.dependencies import get_current_user, get_db_session
from app.modules.applications.docker_runner import (
    get_opa_container_health,
    restart_opa_container,
    stream_container_logs,
)
from app.modules.applications.schemas import (
    ApplicationCreateRequest,
    ApplicationResponse,
    ApplicationUpdateRequest,
    ServiceTokenCreatedResponse,
    ServiceTokenCreateRequest,
    ServiceTokenResponse,
    SidecarDeployResponse,
    SidecarHealthResponse,
)
from app.modules.applications.service import (
    create_application,
    create_service_token,
    deploy_application_sidecar,
    get_application_context,
    list_applications,
    list_service_tokens,
    revoke_service_token,
    update_application,
)
from app.modules.auth.models import User
from app.modules.tenants.dependencies import require_active_tenant_subscription
from app.modules.tenants.models import Tenant

router = APIRouter(
    prefix="/tenants/{tenant_id}/orgs/{org_id}/apps",
    tags=["Applications & OPA Sidecars"],
)


@router.post(
    "",
    response_model=ApplicationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Daftarkan aplikasi baru dengan alokasi port dinamis (18100-18999)",
)
async def create_app_endpoint(
    tenant_id: UUID,
    org_id: UUID,
    payload: ApplicationCreateRequest,
    current_user: User = Depends(get_current_user),
    tenant: Tenant = Depends(require_active_tenant_subscription),
    db: AsyncSession = Depends(get_db_session),
):
    return await create_application(db, tenant_id, org_id, payload, current_user)


@router.get(
    "",
    response_model=List[ApplicationResponse],
    status_code=status.HTTP_200_OK,
    summary="Daftar seluruh aplikasi di organisasi",
)
async def list_apps_endpoint(
    tenant_id: UUID,
    org_id: UUID,
    tenant: Tenant = Depends(require_active_tenant_subscription),
    db: AsyncSession = Depends(get_db_session),
):
    return await list_applications(db, org_id)


@router.get(
    "/{app_id}",
    response_model=ApplicationResponse,
    status_code=status.HTTP_200_OK,
    summary="Detail aplikasi",
)
async def get_app_endpoint(
    tenant_id: UUID,
    org_id: UUID,
    app_id: UUID,
    tenant: Tenant = Depends(require_active_tenant_subscription),
    db: AsyncSession = Depends(get_db_session),
):
    app, _, _ = await get_application_context(db, tenant_id, org_id, app_id)
    return app


@router.patch(
    "/{app_id}",
    response_model=ApplicationResponse,
    status_code=status.HTTP_200_OK,
    summary="Update metadata aplikasi",
)
async def update_app_endpoint(
    tenant_id: UUID,
    org_id: UUID,
    app_id: UUID,
    payload: ApplicationUpdateRequest,
    tenant: Tenant = Depends(require_active_tenant_subscription),
    db: AsyncSession = Depends(get_db_session),
):
    return await update_application(db, tenant_id, org_id, app_id, payload)


# ── OPA Sidecar Orchestration ──────────────────────────────────────────────────

@router.post(
    "/{app_id}/sidecar/deploy",
    response_model=SidecarDeployResponse,
    status_code=status.HTTP_200_OK,
    summary="Deploy / Spawn kontainer OPA sidecar ke Docker Engine host",
)
async def deploy_sidecar_endpoint(
    tenant_id: UUID,
    org_id: UUID,
    app_id: UUID,
    tenant: Tenant = Depends(require_active_tenant_subscription),
    db: AsyncSession = Depends(get_db_session),
):
    return await deploy_application_sidecar(db, tenant_id, org_id, app_id)


@router.get(
    "/{app_id}/sidecar/health",
    response_model=SidecarHealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Cek status kontainer Docker dan OPA Engine /health",
)
async def get_sidecar_health_endpoint(
    tenant_id: UUID,
    org_id: UUID,
    app_id: UUID,
    tenant: Tenant = Depends(require_active_tenant_subscription),
    db: AsyncSession = Depends(get_db_session),
):
    app, org, tenant_obj = await get_application_context(db, tenant_id, org_id, app_id)
    return await get_opa_container_health(
        tenant_slug=tenant_obj.slug,
        org_slug=org.slug,
        app_slug=app.slug,
        assigned_port=app.sidecar_port,
    )


@router.post(
    "/{app_id}/sidecar/restart",
    status_code=status.HTTP_200_OK,
    summary="Restart kontainer OPA sidecar",
)
async def restart_sidecar_endpoint(
    tenant_id: UUID,
    org_id: UUID,
    app_id: UUID,
    tenant: Tenant = Depends(require_active_tenant_subscription),
    db: AsyncSession = Depends(get_db_session),
):
    app, org, tenant_obj = await get_application_context(db, tenant_id, org_id, app_id)
    result = await restart_opa_container(
        tenant_slug=tenant_obj.slug,
        org_slug=org.slug,
        app_slug=app.slug,
    )
    return {"status": "success", "data": result}


@router.get(
    "/{app_id}/sidecar/logs",
    summary="Stream log kontainer OPA secara realtime via Server-Sent Events (SSE)",
)
async def stream_sidecar_logs_endpoint(
    tenant_id: UUID,
    org_id: UUID,
    app_id: UUID,
    tail: int = Query(default=100, ge=1, le=1000, description="Jumlah baris log awal"),
    tenant: Tenant = Depends(require_active_tenant_subscription),
    db: AsyncSession = Depends(get_db_session),
):
    app, org, tenant_obj = await get_application_context(db, tenant_id, org_id, app_id)
    return StreamingResponse(
        stream_container_logs(
            tenant_slug=tenant_obj.slug,
            org_slug=org.slug,
            app_slug=app.slug,
            tail=tail,
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


# ── Service Tokens (Argon2id + Salt) ──────────────────────────────────────────

@router.post(
    "/{app_id}/tokens",
    response_model=ServiceTokenCreatedResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate Service Token baru untuk akses API/Sidecar",
)
async def issue_token_endpoint(
    tenant_id: UUID,
    org_id: UUID,
    app_id: UUID,
    payload: ServiceTokenCreateRequest,
    tenant: Tenant = Depends(require_active_tenant_subscription),
    db: AsyncSession = Depends(get_db_session),
):
    token_obj, raw_token = await create_service_token(db, tenant_id, org_id, app_id, payload)
    response_data = ServiceTokenCreatedResponse.model_validate(token_obj)
    response_data.raw_token = raw_token
    return response_data


@router.get(
    "/{app_id}/tokens",
    response_model=List[ServiceTokenResponse],
    status_code=status.HTTP_200_OK,
    summary="Daftar service token aktif",
)
async def list_tokens_endpoint(
    tenant_id: UUID,
    org_id: UUID,
    app_id: UUID,
    tenant: Tenant = Depends(require_active_tenant_subscription),
    db: AsyncSession = Depends(get_db_session),
):
    return await list_service_tokens(db, app_id)


@router.delete(
    "/{app_id}/tokens/{token_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Revoke service token",
)
async def revoke_token_endpoint(
    tenant_id: UUID,
    org_id: UUID,
    app_id: UUID,
    token_id: UUID,
    tenant: Tenant = Depends(require_active_tenant_subscription),
    db: AsyncSession = Depends(get_db_session),
):
    await revoke_service_token(db, app_id, token_id)