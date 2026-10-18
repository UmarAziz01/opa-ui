from datetime import datetime, timezone
import logging
from fastapi import Depends, Header, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.dependencies import get_db_session
from app.common.utils import verify_secret_argon2
from app.modules.applications.models import ServiceToken
from app.modules.organizations.models import Organization
from app.modules.tenants.models import Tenant

logger = logging.getLogger(__name__)


async def authenticate_sidecar_token(
    tenant_slug: str,
    org_slug: str,
    authorization: str = Header(..., description="Bearer <service_token>"),
    db: AsyncSession = Depends(get_db_session),
) -> ServiceToken:
    """Memvalidasi kredensial Bearer Service Token OPA sidecar."""
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Header otentikasi harus berformat 'Bearer <token>'.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    raw_token = authorization.replace("Bearer ", "").strip()
    if len(raw_token) < 12:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token service tidak valid.",
        )

    token_prefix = raw_token[:12]

    # Ambil kandidat token aktif berdasarkan prefix, tenant_slug, dan org_slug
    query = (
        select(ServiceToken)
        .join(Tenant, ServiceToken.tenant_id == Tenant.id)
        .join(Organization, ServiceToken.organization_id == Organization.id)
        .where(
            Tenant.slug == tenant_slug,
            Organization.slug == org_slug,
            ServiceToken.token_prefix == token_prefix,
            ServiceToken.revoked_at.is_(None),
            Tenant.deleted_at.is_(None),
            Organization.deleted_at.is_(None),
        )
    )
    res = await db.execute(query)
    candidate_tokens = res.scalars().all()

    if not candidate_tokens:
        logger.warning("Token prefix '%s' tidak ditemukan untuk tenant=%s, org=%s", token_prefix, tenant_slug, org_slug)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token service tidak valid atau tidak memiliki akses ke resource ini.",
        )

    # Verifikasi hash Argon2id (format DB: salt$argon2hash)
    now_utc = datetime.now(timezone.utc)
    matched_token: ServiceToken | None = None

    for st in candidate_tokens:
        if st.expires_at and st.expires_at < now_utc:
            continue

        if "$" in st.token_hash:
            salt, argon_hash = st.token_hash.split("$", 1)
            if verify_secret_argon2(raw_token, argon_hash, custom_salt=salt):
                matched_token = st
                break

    if not matched_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Kredensial token salah atau token telah kedaluwarsa.",
        )

    return matched_token