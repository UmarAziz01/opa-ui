import io
import logging
from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import EntityNotFoundException
from app.core.storage import get_presigned_download_url, upload_bundle_stream
from app.modules.bundles.models import PolicyBundle
from app.modules.bundles.schemas import BundleCompileTriggerRequest, BundleRollbackRequest
from app.modules.organizations.models import Organization
from app.modules.tenants.models import Tenant
from app.workers.bundle_compiler import compile_and_upload_bundle, create_in_memory_bundle_tar_gz

logger = logging.getLogger(__name__)


async def list_bundles(
    db: AsyncSession,
    tenant_id: UUID,
    org_id: UUID,
    environment: Optional[str] = None,
) -> List[PolicyBundle]:
    query = (
        select(PolicyBundle)
        .where(
            PolicyBundle.tenant_id == tenant_id,
            PolicyBundle.organization_id == org_id,
        )
        .order_by(desc(PolicyBundle.version))
    )
    if environment:
        query = query.where(PolicyBundle.environment == environment)

    res = await db.execute(query)
    return list(res.scalars().all())


async def get_bundle_by_id(
    db: AsyncSession,
    tenant_id: UUID,
    org_id: UUID,
    bundle_id: UUID,
) -> tuple[PolicyBundle, Optional[str]]:
    query = select(PolicyBundle).where(
        PolicyBundle.id == bundle_id,
        PolicyBundle.tenant_id == tenant_id,
        PolicyBundle.organization_id == org_id,
    )
    res = await db.execute(query)
    bundle = res.scalar_one_or_none()
    if not bundle:
        raise EntityNotFoundException("PolicyBundle", str(bundle_id))

    download_url = None
    if bundle.s3_object_key and bundle.status == "ACTIVE":
        try:
            download_url = await get_presigned_download_url(bundle.s3_object_key)
        except Exception as exc:
            logger.warning("Gagal membuat presigned download URL untuk %s: %s", bundle.s3_object_key, exc)

    return bundle, download_url


async def trigger_manual_compile(
    db: AsyncSession,
    tenant_id: UUID,
    org_id: UUID,
    user_id: UUID,
    payload: BundleCompileTriggerRequest,
) -> PolicyBundle:
    bundle = await compile_and_upload_bundle(
        db=db,
        tenant_id=tenant_id,
        organization_id=org_id,
        user_id=user_id,
        environment=payload.environment,
    )
    if payload.change_summary:
        bundle.change_summary = payload.change_summary
        await db.commit()
        await db.refresh(bundle)
    return bundle


async def rollback_bundle_to_version(
    db: AsyncSession,
    tenant_id: UUID,
    org_id: UUID,
    user_id: UUID,
    payload: BundleRollbackRequest,
) -> PolicyBundle:
    """
    Rollback:
    1. Ambil snapshot data RBAC dari target_bundle_id.
    2. Buat record PolicyBundle baru dengan version increment.
    3. Re-bundle snapshot tersebut ke format tar.gz dan timpa current.tar.gz di MinIO.
    """
    # 1. Ambil target bundle
    target_res = await db.execute(
        select(PolicyBundle).where(
            PolicyBundle.id == payload.target_bundle_id,
            PolicyBundle.tenant_id == tenant_id,
            PolicyBundle.organization_id == org_id,
        )
    )
    target_bundle = target_res.scalar_one_or_none()
    if not target_bundle or not target_bundle.snapshot_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Target bundle untuk rollback tidak ditemukan atau tidak memiliki snapshot RBAC.",
        )

    # 2. Ambil metadata Tenant & Organization
    tenant_res = await db.execute(select(Tenant).where(Tenant.id == tenant_id))
    tenant = tenant_res.scalar_one()

    org_res = await db.execute(select(Organization).where(Organization.id == org_id))
    org = org_res.scalar_one()

    # 3. Hitung nomor versi incremental berikutnya
    ver_stmt = select(func.coalesce(func.max(PolicyBundle.version), 0)).where(
        PolicyBundle.organization_id == org_id,
        PolicyBundle.environment == target_bundle.environment,
    )
    max_ver = (await db.execute(ver_stmt)).scalar_one()
    next_ver = max_ver + 1

    # 4. Re-bundle tar.gz dari data snapshot target
    tar_stream, checksum, size_bytes = create_in_memory_bundle_tar_gz(
        tenant_slug=tenant.slug,
        org_slug=org.slug,
        version=next_ver,
        rbac_data=target_bundle.snapshot_data,
    )

    # 5. Upload bundle versi baru & timpa current.tar.gz di MinIO
    object_key = f"bundles/tenants/{tenant.slug}/orgs/{org.slug}/{target_bundle.environment}/bundle-v{next_ver}.tar.gz"
    current_key = f"bundles/tenants/{tenant.slug}/orgs/{org.slug}/{target_bundle.environment}/current.tar.gz"

    await upload_bundle_stream(object_key=object_key, data=tar_stream, length=size_bytes)
    
    current_stream = io.BytesIO(tar_stream.getvalue())
    await upload_bundle_stream(object_key=current_key, data=current_stream, length=size_bytes)

    # 6. Simpan record bundle baru ke database
    rollback_bundle = PolicyBundle(
        tenant_id=tenant_id,
        organization_id=org_id,
        version=next_ver,
        environment=target_bundle.environment,
        status="ACTIVE",
        bundle_size_bytes=size_bytes,
        checksum_sha256=checksum,
        s3_object_key=object_key,
        snapshot_data=target_bundle.snapshot_data,
        parent_bundle_id=target_bundle.id,
        change_summary=f"Rollback ke versi v{target_bundle.version}",
        compiled_by=user_id,
    )
    db.add(rollback_bundle)
    await db.commit()
    await db.refresh(rollback_bundle)

    logger.info(
        "Rollback berhasil: Bundle baru v%d dibuat dari snapshot v%d dan dipush ke %s",
        rollback_bundle.version,
        target_bundle.version,
        current_key,
    )
    return rollback_bundle