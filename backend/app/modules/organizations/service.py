import logging
from typing import List
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import ConflictException, EntityNotFoundException, PermissionDeniedException
from app.modules.auth.models import User
from app.modules.organizations.models import Organization, OrganizationMember
from app.modules.organizations.schemas import (
    OrganizationCreateRequest,
    OrganizationMemberAssignRequest,
    OrganizationUpdateRequest,
)
from app.modules.tenants.models import Tenant, TenantMember

logger = logging.getLogger(__name__)


async def create_organization(
    db: AsyncSession,
    tenant_id: UUID,
    payload: OrganizationCreateRequest,
    current_user: User,
) -> Organization:
    # 1. Ambil data tenant untuk validasi kuota
    tenant_res = await db.execute(select(Tenant).where(Tenant.id == tenant_id, Tenant.deleted_at.is_(None)))
    tenant = tenant_res.scalar_one_or_none()
    if not tenant:
        raise EntityNotFoundException("Tenant", str(tenant_id))

    # 2. Cek batas kuota max_organizations
    count_res = await db.execute(
        select(func.count(Organization.id)).where(
            Organization.tenant_id == tenant_id,
            Organization.deleted_at.is_(None),
        )
    )
    current_org_count = count_res.scalar_one() or 0
    if current_org_count >= tenant.max_organizations:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Kuota organisasi tenant tercapai ({current_org_count}/{tenant.max_organizations}). "
                "Silakan upgrade paket subscription Anda."
            ),
        )

    # 3. Cek duplikasi slug dalam tenant yang sama
    existing_slug = await db.execute(
        select(Organization.id).where(
            Organization.tenant_id == tenant_id,
            Organization.slug == payload.slug,
            Organization.deleted_at.is_(None),
        )
    )
    if existing_slug.scalar_one_or_none():
        raise ConflictException(f"Organisasi dengan slug '{payload.slug}' sudah ada pada tenant ini.")

    # 4. Buat entitas organisasi
    new_org = Organization(
        tenant_id=tenant_id,
        name=payload.name,
        slug=payload.slug,
        description=payload.description,
    )
    db.add(new_org)
    await db.flush()

    # 5. Otomatis daftarkan pembuat organisasi sebagai ORG_ADMIN
    admin_member = OrganizationMember(
        organization_id=new_org.id,
        user_id=current_user.id,
        assigned_by=current_user.id,
        org_role="ORG_ADMIN",
    )
    db.add(admin_member)
    await db.commit()
    await db.refresh(new_org)

    logger.info("Organisasi '%s' (%s) dibuat pada tenant %s", new_org.name, new_org.slug, tenant_id)
    return new_org


async def get_organization(db: AsyncSession, tenant_id: UUID, org_id: UUID) -> Organization:
    query = select(Organization).where(
        Organization.id == org_id,
        Organization.tenant_id == tenant_id,
        Organization.deleted_at.is_(None),
    )
    res = await db.execute(query)
    org = res.scalar_one_or_none()
    if not org:
        raise EntityNotFoundException("Organization", str(org_id))
    return org


async def list_organizations(db: AsyncSession, tenant_id: UUID) -> List[Organization]:
    query = select(Organization).where(
        Organization.tenant_id == tenant_id,
        Organization.deleted_at.is_(None),
    ).order_by(Organization.created_at.desc())
    res = await db.execute(query)
    return list(res.scalars().all())


async def update_organization(
    db: AsyncSession,
    tenant_id: UUID,
    org_id: UUID,
    payload: OrganizationUpdateRequest,
) -> Organization:
    org = await get_organization(db, tenant_id, org_id)
    if payload.name is not None:
        org.name = payload.name
    if payload.description is not None:
        org.description = payload.description

    await db.commit()
    await db.refresh(org)
    return org


async def assign_organization_member(
    db: AsyncSession,
    tenant_id: UUID,
    org_id: UUID,
    payload: OrganizationMemberAssignRequest,
    current_user: User,
) -> OrganizationMember:
    # 1. Pastikan organisasi valid
    org = await get_organization(db, tenant_id, org_id)

    # 2. User target harus terdaftar terlebih dahulu di tenant parent
    member_check = await db.execute(
        select(TenantMember.id).where(
            TenantMember.tenant_id == tenant_id,
            TenantMember.user_id == payload.user_id,
        )
    )
    if not member_check.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User harus menjadi anggota tenant terlebih dahulu sebelum ditambahkan ke organisasi.",
        )

    # 3. Cek apakah sudah terdaftar di organisasi ini
    existing_org_member = await db.execute(
        select(OrganizationMember).where(
            OrganizationMember.organization_id == org_id,
            OrganizationMember.user_id == payload.user_id,
        )
    )
    member = existing_org_member.scalar_one_or_none()

    if member:
        # Jika sudah ada, update role-nya
        member.org_role = payload.org_role
        member.assigned_by = current_user.id
    else:
        member = OrganizationMember(
            organization_id=org_id,
            user_id=payload.user_id,
            assigned_by=current_user.id,
            org_role=payload.org_role,
        )
        db.add(member)

    await db.commit()
    await db.refresh(member)
    return member


async def list_organization_members(
    db: AsyncSession,
    tenant_id: UUID,
    org_id: UUID,
) -> List[OrganizationMember]:
    await get_organization(db, tenant_id, org_id)
    query = select(OrganizationMember).where(
        OrganizationMember.organization_id == org_id
    ).order_by(OrganizationMember.created_at.asc())
    res = await db.execute(query)
    return list(res.scalars().all())