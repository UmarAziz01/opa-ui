import logging
from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.utils import current_epoch
from app.modules.audit.models import AuditLog
from app.modules.audit.schemas import AuditLogFilter

logger = logging.getLogger(__name__)


async def record_audit_event(
    db: AsyncSession,
    action: str,
    resource_type: str,
    resource_id: Optional[str] = None,
    tenant_id: Optional[UUID] = None,
    organization_id: Optional[UUID] = None,
    actor_id: Optional[UUID] = None,
    changes: Optional[Dict[str, Any]] = None,
    status: str = "SUCCESS",
    request: Optional[Request] = None,
) -> AuditLog:
    """Helper terpusat untuk merekam jejak aktivitas sistem ke audit_logs."""
    ip_addr = None
    user_agent = None

    if request:
        ip_addr = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent", "")[:255]

    log_entry = AuditLog(
        tenant_id=tenant_id,
        organization_id=organization_id,
        actor_id=actor_id,
        action=action,
        resource_type=resource_type,
        resource_id=str(resource_id) if resource_id else None,
        ip_address=ip_addr,
        user_agent=user_agent,
        changes=changes or {},
        status=status,
        timestamp=current_epoch(),
    )
    db.add(log_entry)
    await db.commit()
    await db.refresh(log_entry)
    return log_entry


async def query_audit_logs(
    db: AsyncSession,
    tenant_id: UUID,
    org_id: Optional[UUID] = None,
    filters: Optional[AuditLogFilter] = None,
    limit: int = 50,
    offset: int = 0,
) -> List[AuditLog]:
    stmt = select(AuditLog).where(AuditLog.tenant_id == tenant_id)

    if org_id:
        stmt = stmt.where(AuditLog.organization_id == org_id)

    if filters:
        if filters.action:
            stmt = stmt.where(AuditLog.action == filters.action)
        if filters.resource_type:
            stmt = stmt.where(AuditLog.resource_type == filters.resource_type)
        if filters.actor_id:
            stmt = stmt.where(AuditLog.actor_id == filters.actor_id)
        if filters.start_timestamp:
            stmt = stmt.where(AuditLog.timestamp >= filters.start_timestamp)
        if filters.end_timestamp:
            stmt = stmt.where(AuditLog.timestamp <= filters.end_timestamp)

    stmt = stmt.order_by(AuditLog.timestamp.desc()).limit(min(limit, 100)).offset(offset)
    res = await db.execute(stmt)
    return list(res.scalars().all())