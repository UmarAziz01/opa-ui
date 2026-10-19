from typing import Any, Dict
from fastapi import APIRouter, Depends, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.dependencies import get_db_session, get_current_user
from app.core.security import verify_jwt_token
from app.modules.auth.models import User
from app.modules.auth.schemas import (
    KeycloakTokenExchangeRequest,
    TokenResponse,
    UserContextResponse,
    UserProfileResponse,
)
from app.modules.auth.service import (
    exchange_code_for_token,
    refresh_access_token,
    sync_keycloak_user,
    get_user_tenants,
)

router = APIRouter(prefix="/auth", tags=["Auth & Identity"])


class RefreshTokenRequest(BaseModel):
    refresh_token: str


@router.post(
    "/token",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Tukar authorization code dari Keycloak menjadi access token",
)
async def exchange_token(payload: KeycloakTokenExchangeRequest):
    return await exchange_code_for_token(
        code=payload.code,
        redirect_uri=payload.redirect_uri,
    )


@router.post(
    "/refresh",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Perbarui access token menggunakan refresh token",
)
async def refresh_session(payload: RefreshTokenRequest):
    return await refresh_access_token(payload.refresh_token)


@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    summary="Logout dan invalidated token",
)
async def logout():
    return {"status": "logged_out"}


@router.post(
    "/sync",
    response_model=UserProfileResponse,
    status_code=status.HTTP_200_OK,
    summary="Sinkronisasi akun lokal dengan token JWT Keycloak saat ini",
)
async def sync_profile(
    claims: Dict[str, Any] = Depends(verify_jwt_token),
    db: AsyncSession = Depends(get_db_session),
):
    user = await sync_keycloak_user(db, claims)
    return user


@router.get(
    "/me",
    response_model=UserContextResponse,
    status_code=status.HTTP_200_OK,
    summary="Ambil data profil pengguna, roles, dan tenant yang dimiliki",
)
async def get_my_context(
    current_user: User = Depends(get_current_user),
    claims: Dict[str, Any] = Depends(verify_jwt_token),
    db: AsyncSession = Depends(get_db_session),
):
    realm_access = claims.get("realm_access", {})
    roles = realm_access.get("roles", [])
    tenants = await get_user_tenants(db, current_user.id)

    return UserContextResponse(
        user=UserProfileResponse.model_validate(current_user),
        roles=roles,
        tenant_memberships=tenants,
    )