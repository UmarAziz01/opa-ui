from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.dependencies import get_db_session
from app.modules.audit.schemas import AuditLogEntry, AuditLogFilter
from app.modules.audit.service import query_audit_logs
from app.modules.tenants.dependencies import require_active_tenant_subscription
from app.modules.tenants.models import Tenant

router = APIRouter(
    prefix="/tenants/{tenant_id}/audit-logs",
    tags=["Audit & Compliance"],
)


@router.get(
    "",
    response_model=List[AuditLogEntry],
    status_code=status.HTTP_200_OK,
    summary="Ambil riwayat audit log keamanan dengan filter JSONB dan timestamp epoch",
)
async def get_audit_trail(
    tenant_id: UUID,
    org_id: Optional[UUID] = Query(None, description="Filter berdasarkan organisasi"),
    action: Optional[str] = Query(None, description="Filter action, misal: POLICY_PUBLISHED"),
    resource_type: Optional[str] = Query(None, description="Filter resource type: ROLE, BUNDLE, dll"),
    actor_id: Optional[UUID] = Query(None, description="Filter user ID pelaksana event"),
    start_time: Optional[int] = Query(None, description="Epoch timestamp awal"),
    end_time: Optional[int] = Query(None, description="Epoch timestamp akhir"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    tenant: Tenant = Depends(require_active_tenant_subscription),
    db: AsyncSession = Depends(get_db_session),
):
    filters = AuditLogFilter(
        action=action,
        resource_type=resource_type,
        actor_id=actor_id,
        start_timestamp=start_time,
        end_timestamp=end_time,
    )
    return await query_audit_logs(
        db=db,
        tenant_id=tenant_id,
        org_id=org_id,
        filters=filters,
        limit=limit,
        offset=offset,
    )