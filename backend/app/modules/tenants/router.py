from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.dependencies import get_current_user, get_db_session, require_tenant_membership
from app.modules.auth.models import User
from app.modules.tenants.models import TenantMember
from app.modules.tenants.schemas import (
    TenantCreateRequest,
    TenantMemberAddRequest,
    TenantMemberResponse,
    TenantResponse,
    TenantUpdateRequest,
)
from app.modules.tenants.service import (
    add_member_to_tenant,
    create_tenant_self_service,
    get_tenant_detail,
    get_tenant_members,
    update_tenant_settings,
)

router = APIRouter(prefix="/tenants", tags=["Tenants & Subscriptions"])


@router.post(
    "",
    response_model=TenantResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Onboarding mandiri tenant baru (Free Trial 30 Hari)",
)
async def create_tenant(
    payload: TenantCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    tenant = await create_tenant_self_service(db, payload, current_user)
    return tenant


@router.get(
    "/{tenant_id}",
    response_model=TenantResponse,
    status_code=status.HTTP_200_OK,
    summary="Ambil detail informasi tenant & masa aktif trial",
)
async def get_tenant(
    tenant_id: UUID,
    membership: TenantMember = Depends(require_tenant_membership),
    db: AsyncSession = Depends(get_db_session),
):
    return await get_tenant_detail(db, tenant_id)


@router.patch(
    "/{tenant_id}",
    response_model=TenantResponse,
    status_code=status.HTTP_200_OK,
    summary="Perbarui konfigurasi nama / kuota tenant (Owner Only)",
)
async def update_tenant(
    tenant_id: UUID,
    payload: TenantUpdateRequest,
    current_user: User = Depends(get_current_user),
    membership: TenantMember = Depends(require_tenant_membership),
    db: AsyncSession = Depends(get_db_session),
):
    return await update_tenant_settings(db, tenant_id, payload, current_user)


@router.post(
    "/{tenant_id}/members",
    response_model=TenantMemberResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Undang/tambahkan anggota ke tenant sesuai kuota max_developers",
)
async def add_member(
    tenant_id: UUID,
    payload: TenantMemberAddRequest,
    current_user: User = Depends(get_current_user),
    membership: TenantMember = Depends(require_tenant_membership),
    db: AsyncSession = Depends(get_db_session),
):
    return await add_member_to_tenant(db, tenant_id, payload, current_user)


@router.get(
    "/{tenant_id}/members",
    response_model=List[TenantMemberResponse],
    status_code=status.HTTP_200_OK,
    summary="Daftar seluruh anggota di dalam tenant",
)
async def list_members(
    tenant_id: UUID,
    membership: TenantMember = Depends(require_tenant_membership),
    db: AsyncSession = Depends(get_db_session),
):
    return await get_tenant_members(db, tenant_id)