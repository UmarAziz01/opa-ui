from typing import AsyncGenerator, Dict, Any
from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import verify_jwt_token
from app.common.exceptions import EntityNotFoundException
from app.modules.auth.models import User
from app.modules.tenants.models import TenantMember


# Re-export get_db agar seluruh modul cukup mengimpor dari app.common.dependencies
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async for session in get_db():
        yield session


async def get_current_user(
    token_claims: Dict[str, Any] = Depends(verify_jwt_token),
    db: AsyncSession = Depends(get_db_session),
) -> User:
    """
    Resolusi user dari Keycloak JWT token ke record User internal di database.
    """
    keycloak_sub = token_claims.get("sub")
    if not keycloak_sub:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Klaim 'sub' tidak ditemukan di dalam token identitas.",
        )

    query = select(User).where(User.keycloak_id == keycloak_sub, User.deleted_at.is_(None))
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        raise EntityNotFoundException("User", keycloak_sub)

    if user.status != "ACTIVE":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Akun pengguna sedang non-aktif atau ditangguhkan.",
        )

    return user


async def require_tenant_membership(
    tenant_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> TenantMember:
    """
    Memvalidasi bahwa current_user adalah anggota aktif dari tenant terkait.
    """
    query = select(TenantMember).where(
        TenantMember.tenant_id == tenant_id,
        TenantMember.user_id == current_user.id,
    )
    result = await db.execute(query)
    membership = result.scalar_one_or_none()

    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Anda bukan anggota dari tenant ini.",
        )

    return membership