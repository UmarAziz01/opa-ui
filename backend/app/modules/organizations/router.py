from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.dependencies import get_current_user, get_db_session
from app.modules.auth.models import User
from app.modules.organizations.schemas import (
    OrganizationCreateRequest,
    OrganizationMemberAssignRequest,
    OrganizationMemberResponse,
    OrganizationResponse,
    OrganizationUpdateRequest,
)
from app.modules.organizations.service import (
    assign_organization_member,
    create_organization,
    get_organization,
    list_organization_members,
    list_organizations,
    update_organization,
)
from app.modules.tenants.dependencies import require_active_tenant_subscription
from app.modules.tenants.models import Tenant

router = APIRouter(prefix="/tenants/{tenant_id}/orgs", tags=["Organizations"])


@router.post(
    "",
    response_model=OrganizationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Buat organisasi baru di bawah tenant (memvalidasi max_organizations)",
)
async def create_new_org(
    tenant_id: UUID,
    payload: OrganizationCreateRequest,
    current_user: User = Depends(get_current_user),
    tenant: Tenant = Depends(require_active_tenant_subscription),
    db: AsyncSession = Depends(get_db_session),
):
    return await create_organization(db, tenant_id, payload, current_user)


@router.get(
    "",
    response_model=List[OrganizationResponse],
    status_code=status.HTTP_200_OK,
    summary="Daftar semua organisasi dalam tenant",
)
async def get_all_orgs(
    tenant_id: UUID,
    tenant: Tenant = Depends(require_active_tenant_subscription),
    db: AsyncSession = Depends(get_db_session),
):
    return await list_organizations(db, tenant_id)


@router.get(
    "/{org_id}",
    response_model=OrganizationResponse,
    status_code=status.HTTP_200_OK,
    summary="Ambil detail organisasi spesifik",
)
async def get_org_by_id(
    tenant_id: UUID,
    org_id: UUID,
    tenant: Tenant = Depends(require_active_tenant_subscription),
    db: AsyncSession = Depends(get_db_session),
):
    return await get_organization(db, tenant_id, org_id)


@router.patch(
    "/{org_id}",
    response_model=OrganizationResponse,
    status_code=status.HTTP_200_OK,
    summary="Update metadata organisasi",
)
async def update_org_by_id(
    tenant_id: UUID,
    org_id: UUID,
    payload: OrganizationUpdateRequest,
    tenant: Tenant = Depends(require_active_tenant_subscription),
    db: AsyncSession = Depends(get_db_session),
):
    return await update_organization(db, tenant_id, org_id, payload)


@router.post(
    "/{org_id}/members",
    response_model=OrganizationMemberResponse,
    status_code=status.HTTP_200_OK,
    summary="Tetapkan role anggota organisasi (ORG_ADMIN, DEVELOPER, VIEWER)",
)
async def assign_org_member(
    tenant_id: UUID,
    org_id: UUID,
    payload: OrganizationMemberAssignRequest,
    current_user: User = Depends(get_current_user),
    tenant: Tenant = Depends(require_active_tenant_subscription),
    db: AsyncSession = Depends(get_db_session),
):
    return await assign_organization_member(db, tenant_id, org_id, payload, current_user)


@router.get(
    "/{org_id}/members",
    response_model=List[OrganizationMemberResponse],
    status_code=status.HTTP_200_OK,
    summary="Daftar semua anggota dalam suatu organisasi",
)
async def get_org_members(
    tenant_id: UUID,
    org_id: UUID,
    tenant: Tenant = Depends(require_active_tenant_subscription),
    db: AsyncSession = Depends(get_db_session),
):
    return await list_organization_members(db, tenant_id, org_id)