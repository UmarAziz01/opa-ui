from uuid import UUID
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.dependencies import get_db_session, require_tenant_membership
from app.common.exceptions import TrialExpiredException
from app.modules.tenants.models import Tenant, TenantMember
from app.modules.tenants.service import get_tenant_detail


async def require_active_tenant_subscription(
    tenant_id: UUID,
    membership: TenantMember = Depends(require_tenant_membership),
    db: AsyncSession = Depends(get_db_session),
) -> Tenant:
    """
    Memastikan subscription tenant aktif (tidak EXPIRED)
    sebelum memproses request organisasi, aplikasi, dan policy.
    """
    tenant = await get_tenant_detail(db, tenant_id)

    if tenant.subscription_status == "EXPIRED":
        raise TrialExpiredException(tenant.slug)

    return tenant