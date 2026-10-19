from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_serializer
from app.common.utils import datetime_to_epoch


class PolicyBundleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    organization_id: Optional[UUID] = None
    application_id: Optional[UUID] = None
    version: int
    environment: str
    status: str
    bundle_size_bytes: int
    checksum_sha256: Optional[str] = None
    s3_object_key: Optional[str] = None
    git_commit: Optional[str] = None
    change_summary: Optional[str] = None
    compiled_by: Optional[UUID] = None
    created_at: datetime

    @field_serializer("created_at", mode="plain")
    def serialize_epoch(self, dt: Any) -> Optional[int]:
        if isinstance(dt, datetime):
            return datetime_to_epoch(dt)
        return dt


class PolicyBundleDetailResponse(PolicyBundleResponse):
    snapshot_data: Optional[Dict[str, Any]] = None
    file_diff: Optional[str] = None
    download_url: Optional[str] = None


class BundleCompileTriggerRequest(BaseModel):
    environment: str = Field(default="production", pattern="^(staging|production)$")
    change_summary: Optional[str] = Field(None, max_length=255, example="Update RBAC admin permissions")


class BundleRollbackRequest(BaseModel):
    target_bundle_id: UUID = Field(..., description="ID PolicyBundle versi sebelumnya yang akan dijadikan aktif")