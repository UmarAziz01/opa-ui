import hashlib
import io
import json
import logging
import tarfile
import time
from typing import Any, Dict, Optional
from uuid import UUID

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import AsyncSessionLocal
from app.core.storage import build_bundle_key, upload_bundle_stream
from app.modules.bundles.models import PolicyBundle
from app.modules.organizations.models import Organization
from app.modules.policies.models import Permission, Role, TargetUserRoleMapping
from app.modules.tenants.models import Tenant

logger = logging.getLogger(__name__)

# Template evaluasi OPA RBAC seragam
DEFAULT_AUTHZ_REGO = """package policies.authz
import rego.v1

default allow := false

# Evaluasi kecocokan permission berdasarkan user_roles dan target resource:action
allow if {
    org_data := data.tenants[input.tenant].orgs[input.org]
    some role_name in org_data.user_roles[input.user_id]
    some permission in org_data.roles[role_name].permissions
    target_permission := concat(":", [input.resource, input.action])
    permission == target_permission
}

# Superadmin bypass rule
allow if {
    input.context.is_superadmin == true
}
"""


async def fetch_org_rbac_snapshot(session: AsyncSession, org_id: UUID) -> Dict[str, Any]:
    """Menarik seluruh snapshot role, permission, dan mapping subject dari DB."""
    # 1. Ambil roles beserta permissions (eager load)
    roles_stmt = (
        select(Role)
        .options(selectinload(Role.permissions))
        .where(Role.organization_id == org_id)
    )
    roles_res = await session.execute(roles_stmt)
    roles = roles_res.scalars().all()

    roles_dict = {}
    for r in roles:
        roles_dict[r.name] = {
            "permissions": [f"{p.resource}:{p.action}" for p in r.permissions]
        }

    # 2. Ambil mapping subjek -> role
    mapping_stmt = (
        select(TargetUserRoleMapping, Role.name)
        .join(Role, TargetUserRoleMapping.role_id == Role.id)
        .where(TargetUserRoleMapping.organization_id == org_id)
    )
    mapping_res = await session.execute(mapping_stmt)
    
    user_roles_dict = {}
    for mapping, role_name in mapping_res.all():
        subj = mapping.subject_identifier
        if subj not in user_roles_dict:
            user_roles_dict[subj] = []
        if role_name not in user_roles_dict[subj]:
            user_roles_dict[subj].append(role_name)

    return {
        "roles": roles_dict,
        "user_roles": user_roles_dict,
    }


def create_in_memory_bundle_tar_gz(
    tenant_slug: str,
    org_slug: str,
    version: int,
    rbac_data: Dict[str, Any],
) -> tuple[io.BytesIO, str, int]:
    """Membungkus .manifest, data.json, dan policy rego ke archive tar.gz."""
    tar_buffer = io.BytesIO()

    # Struktur data JSON OPA bundle
    data_content = {
        "tenants": {
            tenant_slug: {
                "orgs": {
                    org_slug: rbac_data
                }
            }
        }
    }
    data_bytes = json.dumps(data_content, indent=2).encode("utf-8")

    # Manifest metadata OPA
    manifest_content = {
        "revision": f"v{version}",
        "roots": [
            f"tenants/{tenant_slug}/orgs/{org_slug}",
            "policies/authz",
        ],
    }
    manifest_bytes = json.dumps(manifest_content, indent=2).encode("utf-8")
    rego_bytes = DEFAULT_AUTHZ_REGO.encode("utf-8")
    now_epoch = int(time.time())

    with tarfile.open(fileobj=tar_buffer, mode="w:gz") as tar:
        # 1. Tambahkan .manifest
        m_info = tarfile.TarInfo(name=".manifest")
        m_info.size = len(manifest_bytes)
        m_info.mtime = now_epoch
        tar.addfile(m_info, io.BytesIO(manifest_bytes))

        # 2. Tambahkan policy rego
        p_info = tarfile.TarInfo(name="policies/authz/policy.rego")
        p_info.size = len(rego_bytes)
        p_info.mtime = now_epoch
        tar.addfile(p_info, io.BytesIO(rego_bytes))

        # 3. Tambahkan data.json (di root bundle agar matching dengan data.tenants.*)
        d_info = tarfile.TarInfo(name="data.json")
        d_info.size = len(data_bytes)
        d_info.mtime = now_epoch
        tar.addfile(d_info, io.BytesIO(data_bytes))

    tar_buffer.seek(0)
    bundle_bytes = tar_buffer.getvalue()
    checksum = hashlib.sha256(bundle_bytes).hexdigest()
    tar_buffer.seek(0)

    return tar_buffer, checksum, len(bundle_bytes)


async def compile_and_upload_bundle(
    db: Optional[AsyncSession] = None,
    tenant_id: Optional[UUID] = None,
    organization_id: Optional[UUID] = None,
    user_id: Optional[UUID] = None,
    environment: str = "production",
    bundle_id: Optional[UUID] = None,
) -> PolicyBundle:
    """
    Kompilasi bundle yang mendukung dua mode:
    1. Dipanggil via router: Membuat record PolicyBundle baru (increment version) lalu compile & upload.
    2. Dipanggil via background task dengan bundle_id yang sudah ada.
    """
    if db is not None and bundle_id is None:
        # Mode 1: Buat record bundle baru dan upload langsung
        # Ambil metadata Tenant & Organization
        tenant_res = await db.execute(select(Tenant).where(Tenant.id == tenant_id))
        tenant = tenant_res.scalar_one()

        org_res = await db.execute(select(Organization).where(Organization.id == organization_id))
        org = org_res.scalar_one()

        # Hitung nomor versi incremental berikutnya
        ver_stmt = select(func.coalesce(func.max(PolicyBundle.version), 0)).where(
            PolicyBundle.organization_id == organization_id,
            PolicyBundle.environment == environment,
        )
        max_ver = (await db.execute(ver_stmt)).scalar_one()
        next_ver = max_ver + 1

        bundle = PolicyBundle(
            tenant_id=tenant_id,
            organization_id=organization_id,
            environment=environment,
            version=next_ver,
            status="BUILDING",
            compiled_by=user_id,
        )
        db.add(bundle)
        await db.commit()
        await db.refresh(bundle)

        target_bundle_id = bundle.id
    else:
        target_bundle_id = bundle_id

    # Proses assembly tar.gz & upload
    async with AsyncSessionLocal() as session:
        try:
            query = (
                select(PolicyBundle, Organization, Tenant)
                .join(Organization, PolicyBundle.organization_id == Organization.id)
                .join(Tenant, PolicyBundle.tenant_id == Tenant.id)
                .where(PolicyBundle.id == target_bundle_id)
            )
            res = await session.execute(query)
            record = res.first()
            if not record:
                raise ValueError(f"Bundle ID {target_bundle_id} tidak ditemukan.")

            bundle, org, tenant = record.PolicyBundle, record.Organization, record.Tenant

            # 1. Snapshot RBAC
            rbac_snapshot = await fetch_org_rbac_snapshot(session, org.id)

            # 2. Build tar.gz
            tar_stream, checksum, size_bytes = create_in_memory_bundle_tar_gz(
                tenant_slug=tenant.slug,
                org_slug=org.slug,
                version=bundle.version,
                rbac_data=rbac_snapshot,
            )

            # 3. Upload versi spesifik (misal: .../bundle-v1.tar.gz)
            object_key = build_bundle_key(
                tenant_slug=tenant.slug,
                org_slug=org.slug,
                environment=bundle.environment,
                version=bundle.version,
            )
            await upload_bundle_stream(
                object_key=object_key,
                data=tar_stream,
                length=size_bytes,
            )

            # 4. Upload salinan sebagai current.tar.gz agar sidecar OPA otomatis sinkron
            current_stream = io.BytesIO(tar_stream.getvalue())
            current_key = f"bundles/tenants/{tenant.slug}/orgs/{org.slug}/{bundle.environment}/current.tar.gz"
            await upload_bundle_stream(
                object_key=current_key,
                data=current_stream,
                length=size_bytes,
            )

            # 5. Update status ke ACTIVE
            bundle.s3_object_key = object_key
            bundle.checksum_sha256 = checksum
            bundle.bundle_size_bytes = size_bytes
            bundle.snapshot_data = rbac_snapshot
            bundle.status = "ACTIVE"
            await session.commit()
            await session.refresh(bundle)

            logger.info(
                "Bundle %s (v%d) dipublish ke %s dan %s",
                bundle.id,
                bundle.version,
                object_key,
                current_key,
            )
            return bundle

        except Exception as exc:
            await session.rollback()
            logger.error("Gagal compile bundle %s: %s", target_bundle_id, exc)
            await session.execute(
                update(PolicyBundle)
                .where(PolicyBundle.id == target_bundle_id)
                .values(status="REVOKED")
            )
            await session.commit()
            raise exc