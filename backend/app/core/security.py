import logging
from typing import Any, Dict, Optional
import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.modules.auth.models import User

logger = logging.getLogger(__name__)
security_scheme = HTTPBearer(auto_error=True)

_jwks_cache: Optional[Dict[str, Any]] = None


async def get_keycloak_jwks() -> Dict[str, Any]:
    global _jwks_cache
    if _jwks_cache is not None:
        return _jwks_cache

    jwks_url = f"{settings.KEYCLOAK_SERVER_URL.rstrip('/')}/realms/{settings.KEYCLOAK_REALM}/protocol/openid-connect/certs"
    async with httpx.AsyncClient(timeout=10.0, verify=False) as client:
        try:
            response = await client.get(jwks_url)
            response.raise_for_status()
            _jwks_cache = response.json()
            return _jwks_cache
        except Exception as exc:
            logger.error("Gagal mengambil JWKS dari Keycloak (%s): %s", jwks_url, exc)
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Layanan autentikasi Keycloak sedang tidak dapat dijangkau",
            )


async def verify_jwt_token(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
) -> Dict[str, Any]:
    token = credentials.credentials
    jwks = await get_keycloak_jwks()

    try:
        unverified_header = jwt.get_unverified_header(token)
        rsa_key = {}
        for key in jwks.get("keys", []):
            if key["kid"] == unverified_header.get("kid"):
                rsa_key = {
                    "kty": key["kty"],
                    "kid": key["kid"],
                    "use": key.get("use"),
                    "n": key["n"],
                    "e": key["e"],
                }
                break

        if not rsa_key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Kunci publik (kid) token tidak ditemukan di Keycloak",
            )

        payload = jwt.decode(
            token,
            rsa_key,
            algorithms=["RS256"],
            options={"verify_aud": False},
        )
        return payload

    except JWTError as exc:
        logger.warning("Verifikasi JWT gagal: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token tidak valid atau telah kedaluwarsa",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    claims = await verify_jwt_token(credentials)
    keycloak_sub = claims.get("sub")

    if not keycloak_sub:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token tidak memiliki atribut 'sub'.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    stmt = select(User).where(User.keycloak_id == keycloak_sub)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        username = claims.get("preferred_username") or claims.get("username") or keycloak_sub
        email = claims.get("email") or f"{username}@no-email.internal"
        full_name = claims.get("name") or claims.get("given_name") or username

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

    if user.status != "ACTIVE":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Akun pengguna dinonaktifkan.",
        )

    return user