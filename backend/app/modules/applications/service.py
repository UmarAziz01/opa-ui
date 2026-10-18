from datetime import datetime, timedelta, timezone
import logging
import secrets
from typing import List, Tuple
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import ConflictException, EntityNotFoundException
from app.common.utils import generate_salt, hash_secret_argon2
from app.modules.applications.docker_runner import (
    get_opa_container_health,
    restart_opa_container,
    spawn_opa_sidecar,
    stop_opa_sidecar,
)
from app.modules.applications.models import Application, ServiceToken
from app.modules.applications.port_manager import allocate_sidecar_port
from app.modules.applications.schemas import (
    ApplicationCreateRequest,
    ApplicationUpdateRequest,
    ServiceTokenCreateRequest,
)
from app.modules.auth.models import User
from app.modules.organizations.models import Organization
from app.modules.tenants.models import Tenant

logger = logging.getLogger(__name__)


async def get_application_context(
    db: AsyncSession,
    tenant_id: UUID,
    org_id: UUID,
    app_id: UUID,
) -> Tuple[Application, Organization, Tenant]:
    query = (
        select(Application, Organization, Tenant)
        .join(Organization, Application.organization_id == Organization.id)
        .join(Tenant, Organization.tenant_id == Tenant.id)
        .where(
            Application.id == app_id,
            Organization.id == org_id,
            Tenant.id == tenant_id,
            Application.deleted_at.is_(None),
        )
    )
    result = await db.execute(query)
    record = result.first()
    if not record:
        raise EntityNotFoundException("Application", str(app_id))
    return record.Application, record.Organization, record.Tenant


async def create_application(
    db: AsyncSession,
    tenant_id: UUID,
    org_id: UUID,
    payload: ApplicationCreateRequest,
    current_user: User,
) -> Application:
    # 1. Validasi Organisasi
    org_query = select(Organization).where(
        Organization.id == org_id,
        Organization.tenant_id == tenant_id,
        Organization.deleted_at.is_(None),
    )
    res_org = await db.execute(org_query)
    if not res_org.scalar_one_or_none():
        raise EntityNotFoundException("Organization", str(org_id))

    # 2. Cek Keunikan Slug
    res_slug = await db.execute(
        select(Application.id).where(
            Application.organization_id == org_id,
            Application.slug == payload.slug,
            Application.deleted_at.is_(None),
        )
    )
    if res_slug.scalar_one_or_none():
        raise ConflictException(f"Aplikasi dengan slug '{payload.slug}' sudah ada di organisasi ini.")

    # 3. Alokasi Port Dinamis (Otomatis atau Validasi User Input)
    assigned_port = await allocate_sidecar_port(
        db=db,
        requested_port=payload.sidecar_port,
    )

    new_app = Application(
        organization_id=org_id,
        slug=payload.slug,
        display_name=payload.display_name,
        description=payload.description,
        sidecar_port=assigned_port,
        created_by=current_user.id,
    )
    db.add(new_app)
    await db.commit()
    await db.refresh(new_app)

    logger.info("Aplikasi '%s' berhasil didaftarkan dengan port %d", new_app.slug, assigned_port)
    return new_app


async def list_applications(db: AsyncSession, org_id: UUID) -> List[Application]:
    query = (
        select(Application)
        .where(Application.organization_id == org_id, Application.deleted_at.is_(None))
        .order_by(Application.created_at.desc())
    )
    res = await db.execute(query)
    return list(res.scalars().all())


async def update_application(
    db: AsyncSession,
    tenant_id: UUID,
    org_id: UUID,
    app_id: UUID,
    payload: ApplicationUpdateRequest,
) -> Application:
    app, _, _ = await get_application_context(db, tenant_id, org_id, app_id)
    if payload.display_name is not None:
        app.display_name = payload.display_name
    if payload.description is not None:
        app.description = payload.description

    await db.commit()
    await db.refresh(app)
    return app


async def deploy_application_sidecar(
    db: AsyncSession,
    tenant_id: UUID,
    org_id: UUID,
    app_id: UUID,
) -> dict:
    app, org, tenant = await get_application_context(db, tenant_id, org_id, app_id)

    # Buat internal service token untuk container OPA polling bundle MinIO
    raw_token = f"opa_sidecar_{secrets.token_urlsafe(32)}"
    salt = generate_salt(16)
    hashed_token = hash_secret_argon2(raw_token, custom_salt=salt)

    token_record = ServiceToken(
        tenant_id=tenant.id,
        organization_id=org.id,
        application_id=app.id,
        name=f"Automated Sidecar Token - {app.slug}",
        token_prefix=raw_token[:12],
        token_hash=f"{salt}${hashed_token}",
    )
    db.add(token_record)
    await db.commit()

    # Jalankan container sidecar via Docker SDK
    container_info = await spawn_opa_sidecar(
        tenant_slug=tenant.slug,
        org_slug=org.slug,
        app_slug=app.slug,
        assigned_port=app.sidecar_port,
        service_token=raw_token,
        environment="production",
    )

    return {
        "application_id": app.id,
        "container_name": container_info["container_name"],
        "status": container_info["status"],
        "host_port": container_info["host_port"],
        "network": container_info["network"],
        "message": "Kontainer OPA sidecar berhasil di-deploy dan terhubung ke MinIO bundle.",
    }


async def create_service_token(
    db: AsyncSession,
    tenant_id: UUID,
    org_id: UUID,
    app_id: UUID,
    payload: ServiceTokenCreateRequest,
) -> Tuple[ServiceToken, str]:
    app, org, tenant = await get_application_context(db, tenant_id, org_id, app_id)

    raw_token = f"opa_st_{secrets.token_urlsafe(32)}"
    token_prefix = raw_token[:12]

    # Enkripsi Argon2id dengan Dynamic Salt
    salt = generate_salt(16)
    hashed = hash_secret_argon2(raw_token, custom_salt=salt)
    stored_hash = f"{salt}${hashed}"

    now_utc = datetime.now(timezone.utc)
    expires_at = now_utc + timedelta(days=payload.expires_in_days) if payload.expires_in_days else None

    token_obj = ServiceToken(
        tenant_id=tenant.id,
        organization_id=org.id,
        application_id=app.id,
        name=payload.name,
        token_prefix=token_prefix,
        token_hash=stored_hash,
        expires_at=expires_at,
    )
    db.add(token_obj)
    await db.commit()
    await db.refresh(token_obj)

    return token_obj, raw_token


async def list_service_tokens(db: AsyncSession, app_id: UUID) -> List[ServiceToken]:
    query = (
        select(ServiceToken)
        .where(ServiceToken.application_id == app_id, ServiceToken.revoked_at.is_(None))
        .order_by(ServiceToken.created_at.desc())
    )
    res = await db.execute(query)
    return list(res.scalars().all())


async def revoke_service_token(db: AsyncSession, app_id: UUID, token_id: UUID) -> None:
    query = select(ServiceToken).where(
        ServiceToken.id == token_id,
        ServiceToken.application_id == app_id,
        ServiceToken.revoked_at.is_(None),
    )
    res = await db.execute(query)
    token = res.scalar_one_or_none()
    if not token:
        raise EntityNotFoundException("ServiceToken", str(token_id))

    token.revoked_at = datetime.now(timezone.utc)
    await db.commit()