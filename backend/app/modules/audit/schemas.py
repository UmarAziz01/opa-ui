from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field, field_serializer
from app.common.utils import datetime_to_epoch


class AuditLogEntry(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: Optional[UUID] = None
    organization_id: Optional[UUID] = None
    actor_id: Optional[UUID] = None
    action: str
    resource_type: str
    resource_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    changes: Optional[Dict[str, Any]] = None
    status: str
    timestamp: int
    created_at: datetime

    @field_serializer("created_at", mode="plain")
    def serialize_epoch(self, dt: Any) -> Optional[int]:
        if isinstance(dt, datetime):
            return datetime_to_epoch(dt)
        return dt


class AuditLogFilter(BaseModel):
    action: Optional[str] = None
    resource_type: Optional[str] = None
    actor_id: Optional[UUID] = None
    start_timestamp: Optional[int] = Field(None, description="Awal rentang waktu (epoch detik)")
    end_timestamp: Optional[int] = Field(None, description="Akhir rentang waktu (epoch detik)")