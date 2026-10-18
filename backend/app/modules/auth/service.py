import logging
from typing import Any, Dict, List
import httpx
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.modules.auth.models import User
from app.modules.auth.schemas import TokenResponse
from app.modules.tenants.models import TenantMember, Tenant

logger = logging.getLogger(__name__)


async def exchange_code_for_token(code: str, redirect_uri: str) -> TokenResponse:
    """Tukar OIDC Authorization Code dengan Access Token ke Keycloak."""
    token_url = f"{settings.KEYCLOAK_SERVER_URL.rstrip('/')}/realms/{settings.KEYCLOAK_REALM}/protocol/openid-connect/token"
    data = {
        "grant_type": "authorization_code",
        "client_id": settings.KEYCLOAK_CLIENT_ID,
        "client_secret": settings.KEYCLOAK_CLIENT_SECRET,
        "code": code,
        "redirect_uri": redirect_uri,
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            resp = await client.post(token_url, data=data)
            if resp.status_code != 200:
                logger.error("Gagal exchange authorization code: %s", resp.text)
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Authorization code tidak valid atau telah kedaluwarsa.",
                )
            res_json = resp.json()
            return TokenResponse(
                access_token=res_json["access_token"],
                token_type=res_json.get("token_type", "Bearer"),
                expires_in=res_json.get("expires_in", 300),
                refresh_token=res_json.get("refresh_token"),
                refresh_expires_in=res_json.get("refresh_expires_in"),
                id_token=res_json.get("id_token"),
            )
        except httpx.RequestError as exc:
            logger.error("Koneksi ke Keycloak token endpoint gagal: %s", exc)
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Layanan Keycloak tidak dapat dihubungi.",
            )


async def sync_keycloak_user(db: AsyncSession, claims: Dict[str, Any]) -> User:
    """
    Sinkronisasi profil pengguna (Just-In-Time Provisioning).
    Jika pengguna belum terdaftar di DB internal, buat record baru.
    Jika sudah ada, perbarui nama/email jika terdapat perbedaan.
    """
    keycloak_sub = claims.get("sub")
    if not keycloak_sub:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token Keycloak tidak memiliki klaim 'sub'.",
        )

    username = claims.get("preferred_username") or claims.get("username") or keycloak_sub
    email = claims.get("email") or f"{username}@no-email.internal"
    full_name = claims.get("name") or claims.get("given_name") or username

    query = select(User).where(User.keycloak_id == keycloak_sub)
    res = await db.execute(query)
    user = res.scalar_one_or_none()

    if not user:
        # User baru pertama kali login
        user = User(
            keycloak_id=keycloak_sub,
            username=username,
            email=email,
            full_name=full_name,
            user_type="External",
            status="ACTIVE",
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        logger.info("Pengguna baru disinkronisasi dari Keycloak: %s (%s)", username, keycloak_sub)
    else:
        # Update atribut jika ada pembaruan di Keycloak
        updated = False
        if user.full_name != full_name:
            user.full_name = full_name
            updated = True
        if user.email != email:
            user.email = email
            updated = True
        if updated:
            await db.commit()
            await db.refresh(user)

    return user


async def get_user_tenants(db: AsyncSession, user_id: Any) -> List[Dict[str, Any]]:
    """Ambil daftar tenant di mana pengguna terdaftar sebagai anggota."""
    stmt = (
        select(Tenant.id, Tenant.name, Tenant.slug, Tenant.subscription_status, TenantMember.tenant_role)
        .join(TenantMember, Tenant.id == TenantMember.tenant_id)
        .where(TenantMember.user_id == user_id, Tenant.deleted_at.is_(None))
    )
    result = await db.execute(stmt)
    memberships = []
    for row in result.all():
        memberships.append({
            "tenant_id": str(row.id),
            "name": row.name,
            "slug": row.slug,
            "subscription_status": row.subscription_status,
            "role": row.tenant_role,
        })
    return memberships