import logging
from datetime import datetime, timedelta, timezone
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import ConflictException, EntityNotFoundException, PermissionDeniedException
from app.modules.auth.models import User
from app.modules.tenants.models import Tenant, TenantMember
from app.modules.tenants.schemas import TenantCreateRequest, TenantMemberAddRequest, TenantUpdateRequest

logger = logging.getLogger(__name__)


async def create_tenant_self_service(
    db: AsyncSession,
    payload: TenantCreateRequest,
    current_user: User,
) -> Tenant:
    """
    Onboarding tenant baru secara mandiri:
    1. Cek duplikasi slug.
    2. Atur masa trial 30 hari dari waktu sekarang (UTC).
    3. Simpan tenant dan daftarkan pembuat sebagai TENANT_ADMIN.
    """
    # 1. Cek slug
    existing = await db.execute(select(Tenant.id).where(Tenant.slug == payload.slug))
    if existing.scalar_one_or_none():
        raise ConflictException(f"Tenant dengan slug '{payload.slug}' sudah terdaftar.")

    now_utc = datetime.now(timezone.utc)
    trial_ends = now_utc + timedelta(days=30)

    # 2. Buat entitas tenant
    new_tenant = Tenant(
        name=payload.name,
        slug=payload.slug,
        owner_user_id=current_user.id,
        subscription_tier="FREE_TRIAL",
        subscription_status="TRIALING",
        trial_starts_at=now_utc,
        trial_ends_at=trial_ends,
        max_organizations=3,
        max_developers=5,
    )
    db.add(new_tenant)
    await db.flush()

    # 3. Otomatis jadikan current_user sebagai TENANT_ADMIN
    membership = TenantMember(
        tenant_id=new_tenant.id,
        user_id=current_user.id,
        tenant_role="TENANT_ADMIN",
    )
    db.add(membership)
    await db.commit()
    await db.refresh(new_tenant)

    logger.info(
        "Tenant baru berhasil dibuat: %s (%s) oleh user %s. Trial aktif hingga %s.",
        new_tenant.name,
        new_tenant.slug,
        current_user.username,
        trial_ends.isoformat(),
    )
    return new_tenant


async def get_tenant_detail(db: AsyncSession, tenant_id: UUID) -> Tenant:
    query = select(Tenant).where(Tenant.id == tenant_id, Tenant.deleted_at.is_(None))
    result = await db.execute(query)
    tenant = result.scalar_one_or_none()
    if not tenant:
        raise EntityNotFoundException("Tenant", str(tenant_id))
    return tenant


async def update_tenant_settings(
    db: AsyncSession,
    tenant_id: UUID,
    payload: TenantUpdateRequest,
    current_user: User,
) -> Tenant:
    tenant = await get_tenant_detail(db, tenant_id)

    # Hanya owner yang berhak mengubah kuota/pengaturan tenant
    if tenant.owner_user_id != current_user.id:
        raise PermissionDeniedException("Hanya owner tenant yang dapat mengubah konfigurasi ini.")

    if payload.name is not None:
        tenant.name = payload.name
    if payload.max_organizations is not None:
        tenant.max_organizations = payload.max_organizations
    if payload.max_developers is not None:
        tenant.max_developers = payload.max_developers

    await db.commit()
    await db.refresh(tenant)
    return tenant


async def add_member_to_tenant(
    db: AsyncSession,
    tenant_id: UUID,
    payload: TenantMemberAddRequest,
    current_user: User,
) -> TenantMember:
    """Menambahkan user ke keanggotaan tenant dengan mematuhi kuota max_developers."""
    tenant = await get_tenant_detail(db, tenant_id)

    # Validasi kuota developer/anggota
    count_query = select(func.count(TenantMember.id)).where(TenantMember.tenant_id == tenant_id)
    member_count_res = await db.execute(count_query)
    current_members = member_count_res.scalar_one() or 0

    if current_members >= tenant.max_developers:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Batas kuota anggota tenant tercapai ({current_members}/{tenant.max_developers}). "
                "Upgrade langganan untuk menambah kuota anggota."
            ),
        )

    # Validasi user target
    target_user_res = await db.execute(select(User).where(User.id == payload.user_id, User.deleted_at.is_(None)))
    if not target_user_res.scalar_one_or_none():
        raise EntityNotFoundException("User", str(payload.user_id))

    # Cek apakah user sudah terdaftar di tenant
    existing_member = await db.execute(
        select(TenantMember.id).where(
            TenantMember.tenant_id == tenant_id,
            TenantMember.user_id == payload.user_id,
        )
    )
    if existing_member.scalar_one_or_none():
        raise ConflictException("Pengguna sudah menjadi anggota di tenant ini.")

    new_member = TenantMember(
        tenant_id=tenant_id,
        user_id=payload.user_id,
        tenant_role=payload.tenant_role,
    )
    db.add(new_member)
    await db.commit()
    await db.refresh(new_member)
    return new_member


async def get_tenant_members(db: AsyncSession, tenant_id: UUID) -> List[TenantMember]:
    query = select(TenantMember).where(TenantMember.tenant_id == tenant_id)
    result = await db.execute(query)
    return list(result.scalars().all())