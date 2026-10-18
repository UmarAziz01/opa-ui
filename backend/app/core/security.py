import logging
from typing import Any, Dict, Optional
import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from app.core.config import settings

logger = logging.getLogger(__name__)
security_scheme = HTTPBearer(auto_error=True)

# Cache JWKS keycloak di memori
_jwks_cache: Optional[Dict[str, Any]] = None


async def get_keycloak_jwks() -> Dict[str, Any]:
    global _jwks_cache
    if _jwks_cache is not None:
        return _jwks_cache

    jwks_url = f"{settings.KEYCLOAK_SERVER_URL.rstrip('/')}/realms/{settings.KEYCLOAK_REALM}/protocol/openid-connect/certs"
    async with httpx.AsyncClient(timeout=10.0) as client:
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
    """Validasi signature token Keycloak via public certs dan verifikasi claims."""
    token = credentials.credentials
    jwks = await get_keycloak_jwks()

    try:
        # Baca header tanpa verifikasi terlebih dahulu untuk menemukan key id (kid)
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
            audience="account",  # default audience token Keycloak
            options={"verify_aud": False},  # Fleksibel jika multiple audience
        )
        return payload

    except JWTError as exc:
        logger.warning("Verifikasi JWT gagal: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token tidak valid atau telah kedaluwarsa",
            headers={"WWW-Authenticate": "Bearer"},
        )