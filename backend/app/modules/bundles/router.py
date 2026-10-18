from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status, Header, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.dependencies import get_current_user, get_db_session
from app.modules.auth.models import User
from app.modules.bundles.schemas import (
    BundleCompileTriggerRequest,
    BundleRollbackRequest,
    PolicyBundleDetailResponse,
    PolicyBundleResponse,
)
from app.modules.bundles.service import (
    get_bundle_by_id,
    list_bundles,
    rollback_bundle_to_version,
    trigger_manual_compile,
)
from app.modules.tenants.dependencies import require_active_tenant_subscription
from app.modules.tenants.models import Tenant
from minio.error import S3Error

from app.core.storage import get_object_stream
from app.modules.bundles.dependencies import authenticate_sidecar_token
from app.modules.applications.models import ServiceToken

router = APIRouter(
    prefix="/tenants/{tenant_id}/orgs/{org_id}/bundles",
    tags=["Policy Bundles & GitOps Releases"],
)


@router.get(
    "",
    response_model=List[PolicyBundleResponse],
    status_code=status.HTTP_200_OK,
    summary="Daftar riwayat rilis bundle kebijakan OPA",
)
async def list_bundles_endpoint(
    tenant_id: UUID,
    org_id: UUID,
    environment: Optional[str] = Query(None, pattern="^(staging|production)$"),
    tenant: Tenant = Depends(require_active_tenant_subscription),
    db: AsyncSession = Depends(get_db_session),
):
    return await list_bundles(db, tenant_id, org_id, environment)


@router.get(
    "/{bundle_id}",
    response_model=PolicyBundleDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Detail bundle beserta presigned URL download MinIO/S3",
)
async def get_bundle_endpoint(
    tenant_id: UUID,
    org_id: UUID,
    bundle_id: UUID,
    tenant: Tenant = Depends(require_active_tenant_subscription),
    db: AsyncSession = Depends(get_db_session),
):
    bundle, download_url = await get_bundle_by_id(db, tenant_id, org_id, bundle_id)
    response_data = PolicyBundleDetailResponse.model_validate(bundle)
    response_data.download_url = download_url
    return response_data


@router.post(
    "/compile",
    response_model=PolicyBundleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Trigger kompilasi bundle baru secara manual dari RBAC aktif",
)
async def compile_bundle_endpoint(
    tenant_id: UUID,
    org_id: UUID,
    payload: BundleCompileTriggerRequest,
    current_user: User = Depends(get_current_user),
    tenant: Tenant = Depends(require_active_tenant_subscription),
    db: AsyncSession = Depends(get_db_session),
):
    return await trigger_manual_compile(db, tenant_id, org_id, current_user.id, payload)


@router.post(
    "/rollback",
    response_model=PolicyBundleResponse,
    status_code=status.HTTP_200_OK,
    summary="Rollback ke versi bundle sebelumnya",
)
async def rollback_bundle_endpoint(
    tenant_id: UUID,
    org_id: UUID,
    payload: BundleRollbackRequest,
    current_user: User = Depends(get_current_user),
    tenant: Tenant = Depends(require_active_tenant_subscription),
    db: AsyncSession = Depends(get_db_session),
):
    return await rollback_bundle_to_version(db, tenant_id, org_id, current_user.id, payload)


@router.get(
    "/tenants/{tenant_slug}/orgs/{org_slug}/{environment}/current.tar.gz",
    summary="Endpoint Polling Bundle OPA Sidecar (Bearer Authenticated)",
    responses={
        200: {
            "content": {"application/gzip": {}},
            "description": "File bundle tar.gz terbaru.",
        },
        304: {"description": "Bundle belum berubah (ETag sama)."},
        401: {"description": "Service Token tidak valid."},
        404: {"description": "Bundle belum pernah dipublish."},
    },
)
async def download_current_bundle(
    tenant_slug: str,
    org_slug: str,
    environment: str,
    if_none_match: str | None = Header(None, alias="If-None-Match"),
    token_auth: ServiceToken = Depends(authenticate_sidecar_token),
):
    """
    Endpoint yang dipanggil berkala (10-30 detik) oleh kontainer OPA sidecar.
    Mendukung conditional GET (ETag / If-None-Match) untuk menghemat transfer data.
    """
    object_key = f"bundles/tenants/{tenant_slug}/orgs/{org_slug}/{environment}/current.tar.gz"

    try:
        data_stream, content_length, etag = await get_object_stream(object_key)
    except S3Error as exc:
        if exc.code in ("NoSuchKey", "ResourceNotFound"):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Bundle untuk environment '{environment}' belum tersedia.",
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Terjadi kesalahan saat membaca storage: {str(exc)}",
        )

    # 1. Evaluasi Caching OPA: Jika ETag cocok, kembalikan 304 Not Modified
    if if_none_match and if_none_match.strip('"') == etag:
        data_stream.close()
        data_stream.release_conn()
        return Response(status_code=status.HTTP_304_NOT_MODIFIED)

    # 2. Generator async untuk Streaming response
    async def stream_bundle():
        try:
            for chunk in data_stream.stream(32 * 1024):  # Baca blok 32KB
                yield chunk
        finally:
            data_stream.close()
            data_stream.release_conn()

    headers = {
        "Content-Type": "application/gzip",
        "Content-Disposition": f'attachment; filename="current.tar.gz"',
        "Content-Length": str(content_length),
        "ETag": f'"{etag}"',
        "Cache-Control": "no-cache",
    }

    return StreamingResponse(
        stream_bundle(),
        status_code=status.HTTP_200_OK,
        headers=headers,
    )