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
    """Tukar OIDC Authorization Code dengan Access Token Keycloak."""
    token_url = f"{settings.KEYCLOAK_SERVER_URL.rstrip('/')}/realms/{settings.KEYCLOAK_REALM}/protocol/openid-connect/token"
    data = {
        "grant_type": "authorization_code",
        "client_id": settings.KEYCLOAK_CLIENT_ID,
        "client_secret": settings.KEYCLOAK_CLIENT_SECRET,
        "code": code,
        "redirect_uri": redirect_uri,
    }

    async with httpx.AsyncClient(timeout=10.0, verify=False) as client:
        try:
            resp = await client.post(token_url, data=data)
            if resp.status_code != 200:
                logger.error("Gagal exchange authorization code [%s]: %s", resp.status_code, resp.text)
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Kode otorisasi tidak valid atau telah kedaluwarsa.",
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
            logger.error("Gagal terhubung ke Keycloak: %s", exc)
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Layanan autentikasi Keycloak sedang tidak dapat dijangkau.",
            )


async def sync_keycloak_user(db: AsyncSession, claims: Dict[str, Any]) -> User:
    keycloak_sub = claims.get("sub")
    if not keycloak_sub:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Klaim token tidak memiliki atribut 'sub'.",
        )

    stmt = select(User).where(User.keycloak_id == keycloak_sub)
    res = await db.execute(stmt)
    user = res.scalar_one_or_none()

    username = claims.get("preferred_username") or claims.get("username") or keycloak_sub
    email = claims.get("email") or f"{username}@no-email.internal"
    full_name = claims.get("name") or claims.get("given_name") or username

    if not user:
        user = User(
            keycloak_id=keycloak_sub,
            username=username,
            email=email,
            full_name=full_name,
            user_type="External",
            status="ACTIVE",
        )
        db.add(user)
    else:
        user.username = username
        user.email = email
        user.full_name = full_name

    await db.commit()
    await db.refresh(user)
    return user


async def get_user_tenants(db: AsyncSession, user_id: Any) -> List[Dict[str, Any]]:
    stmt = (
        select(
            Tenant.id,
            Tenant.name,
            Tenant.slug,
            Tenant.subscription_status,
            TenantMember.tenant_role,
        )
        .join(TenantMember, Tenant.id == TenantMember.tenant_id)
        .where(TenantMember.user_id == user_id, Tenant.deleted_at.is_(None))
    )
    res = await db.execute(stmt)
    rows = res.all()

    return [
        {
            "id": row.id,
            "name": row.name,
            "slug": row.slug,
            "subscription_status": row.subscription_status,
            "tenant_role": row.tenant_role,
        }
        for row in rows
    ]

async def refresh_access_token(refresh_token: str) -> TokenResponse:
    """Perbarui Access Token menggunakan Refresh Token ke Keycloak."""
    token_url = f"{settings.KEYCLOAK_SERVER_URL.rstrip('/')}/realms/{settings.KEYCLOAK_REALM}/protocol/openid-connect/token"
    data = {
        "grant_type": "refresh_token",
        "client_id": settings.KEYCLOAK_CLIENT_ID,
        "client_secret": settings.KEYCLOAK_CLIENT_SECRET,
        "refresh_token": refresh_token,
    }

    async with httpx.AsyncClient(timeout=10.0, verify=False) as client:
        try:
            resp = await client.post(token_url, data=data)
            if resp.status_code != 200:
                logger.error("Gagal refresh token Keycloak [%s]: %s", resp.status_code, resp.text)
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Refresh token kedaluwarsa atau tidak valid.",
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
            logger.error("Gagal terhubung ke Keycloak: %s", exc)
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Layanan autentikasi Keycloak sedang tidak dapat dijangkau.",
            )