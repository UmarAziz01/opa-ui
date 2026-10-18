from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.dependencies import get_current_user, get_db_session
from app.modules.auth.models import User
from app.modules.bundles.models import PolicyBundle
from app.modules.policies.schemas import (
    PermissionCreateRequest,
    PermissionResponse,
    PolicySimulationInput,
    PolicySimulationResponse,
    RoleCreateRequest,
    RoleResponse,
    RoleUpdateRequest,
    SubjectRoleAssignRequest,
    SubjectRoleMappingResponse,
)
from app.modules.policies.service import (
    assign_subject_role,
    compile_organization_bundle,
    create_permission,
    create_role,
    list_permissions,
    list_roles,
    list_subject_mappings,
    simulate_policy_decision,
    update_role,
)
from app.modules.tenants.dependencies import require_active_tenant_subscription
from app.modules.tenants.models import Tenant

router = APIRouter(
    prefix="/tenants/{tenant_id}/orgs/{org_id}/policies",
    tags=["Policies & RBAC Matrix"],
)


# ── Permissions ───────────────────────────────────────────────────────────────

@router.post(
    "/permissions",
    response_model=PermissionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Daftarkan permission baru (resource:action)",
)
async def create_perm_endpoint(
    tenant_id: UUID,
    org_id: UUID,
    payload: PermissionCreateRequest,
    tenant: Tenant = Depends(require_active_tenant_subscription),
    db: AsyncSession = Depends(get_db_session),
):
    return await create_permission(db, org_id, payload)


@router.get(
    "/permissions",
    response_model=List[PermissionResponse],
    status_code=status.HTTP_200_OK,
    summary="Daftar semua permission yang terdaftar di organisasi",
)
async def list_perms_endpoint(
    tenant_id: UUID,
    org_id: UUID,
    tenant: Tenant = Depends(require_active_tenant_subscription),
    db: AsyncSession = Depends(get_db_session),
):
    return await list_permissions(db, org_id)


# ── Roles ─────────────────────────────────────────────────────────────────────

@router.post(
    "/roles",
    response_model=RoleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Buat role baru beserta mapping permission awal",
)
async def create_role_endpoint(
    tenant_id: UUID,
    org_id: UUID,
    payload: RoleCreateRequest,
    tenant: Tenant = Depends(require_active_tenant_subscription),
    db: AsyncSession = Depends(get_db_session),
):
    return await create_role(db, org_id, payload)


@router.get(
    "/roles",
    response_model=List[RoleResponse],
    status_code=status.HTTP_200_OK,
    summary="Daftar role beserta matrix permission-nya",
)
async def list_roles_endpoint(
    tenant_id: UUID,
    org_id: UUID,
    tenant: Tenant = Depends(require_active_tenant_subscription),
    db: AsyncSession = Depends(get_db_session),
):
    return await list_roles(db, org_id)


@router.patch(
    "/roles/{role_id}",
    response_model=RoleResponse,
    status_code=status.HTTP_200_OK,
    summary="Update role atau ubah daftar permission yang dipasangkan",
)
async def update_role_endpoint(
    tenant_id: UUID,
    org_id: UUID,
    role_id: UUID,
    payload: RoleUpdateRequest,
    tenant: Tenant = Depends(require_active_tenant_subscription),
    db: AsyncSession = Depends(get_db_session),
):
    return await update_role(db, org_id, role_id, payload)


# ── Subject Mappings ──────────────────────────────────────────────────────────

@router.post(
    "/subjects/assign",
    response_model=SubjectRoleMappingResponse,
    status_code=status.HTTP_200_OK,
    summary="Tugaskan role ke subjek pengguna/aplikasi target",
)
async def assign_role_endpoint(
    tenant_id: UUID,
    org_id: UUID,
    payload: SubjectRoleAssignRequest,
    tenant: Tenant = Depends(require_active_tenant_subscription),
    db: AsyncSession = Depends(get_db_session),
):
    return await assign_subject_role(db, org_id, payload)


@router.get(
    "/subjects",
    response_model=List[SubjectRoleMappingResponse],
    status_code=status.HTTP_200_OK,
    summary="Daftar seluruh mapping subjek ke role",
)
async def list_mappings_endpoint(
    tenant_id: UUID,
    org_id: UUID,
    tenant: Tenant = Depends(require_active_tenant_subscription),
    db: AsyncSession = Depends(get_db_session),
):
    return await list_subject_mappings(db, org_id)


# ── Simulation & Publish ──────────────────────────────────────────────────────

@router.post(
    "/simulate",
    response_model=PolicySimulationResponse,
    status_code=status.HTTP_200_OK,
    summary="Dry-run simulasi evaluasi izin menggunakan binary OPA CLI lokal",
)
async def simulate_endpoint(
    tenant_id: UUID,
    org_id: UUID,
    payload: PolicySimulationInput,
    tenant: Tenant = Depends(require_active_tenant_subscription),
    db: AsyncSession = Depends(get_db_session),
):
    return await simulate_policy_decision(db, org_id, payload)


@router.post(
    "/publish-bundle",
    status_code=status.HTTP_200_OK,
    summary="Kompilasi RBAC saat ini menjadi bundle .tar.gz OPA dan upload ke MinIO",
)
async def publish_bundle_endpoint(
    tenant_id: UUID,
    org_id: UUID,
    environment: str = Query(default="production", regex="^(staging|production)$"),
    current_user: User = Depends(get_current_user),
    tenant: Tenant = Depends(require_active_tenant_subscription),
    db: AsyncSession = Depends(get_db_session),
):
    bundle = await compile_organization_bundle(
        db=db,
        tenant_id=tenant_id,
        organization_id=org_id,
        user_id=current_user.id,
        environment=environment,
    )
    return {
        "status": "success",
        "message": f"Policy bundle v{bundle.version} berhasil dikompilasi dan dipublish ke MinIO.",
        "bundle_id": str(bundle.id),
        "version": bundle.version,
        "s3_key": bundle.s3_object_key,
        "checksum_sha256": bundle.checksum_sha256,
    }