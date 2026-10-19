from datetime import datetime
from typing import Any, List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_serializer, field_validator
from app.common.utils import datetime_to_epoch


class TenantCreateRequest(BaseModel):
    name: str = Field(..., min_length=3, max_length=150, example="Acme Corporation")
    slug: str = Field(..., min_length=3, max_length=100, example="acme-corp")

    @field_validator("slug")
    @classmethod
    def validate_slug(cls, v: str) -> str:
        clean_slug = v.strip().lower()
        if not clean_slug.replace("-", "").isalnum():
            raise ValueError("Slug hanya boleh berisi huruf kecil alfanumerik dan tanda hubung (-).")
        return clean_slug


class TenantUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=150)
    max_organizations: Optional[int] = Field(None, ge=1, le=50)
    max_developers: Optional[int] = Field(None, ge=1, le=100)


class TenantResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    slug: str
    owner_user_id: UUID
    subscription_tier: str
    subscription_status: str
    trial_starts_at: Optional[datetime] = None
    trial_ends_at: Optional[datetime] = None
    max_organizations: int
    max_developers: int
    created_at: datetime
    updated_at: datetime

    @field_serializer(
        "trial_starts_at",
        "trial_ends_at",
        "created_at",
        "updated_at",
        mode="plain",
    )
    def serialize_datetime_to_epoch(self, dt: Any) -> Optional[int]:
      if dt is None:
        return None
      if isinstance(dt, datetime):
        return datetime_to_epoch(dt)
      return dt


class TenantMemberAddRequest(BaseModel):
    user_id: UUID = Field(..., description="ID User internal yang akan ditambahkan")
    tenant_role: str = Field(default="TENANT_MEMBER", example="TENANT_MEMBER")  # 'TENANT_ADMIN' | 'TENANT_MEMBER'


class TenantMemberResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    user_id: UUID
    tenant_role: str
    created_at: datetime

    @field_serializer("created_at", mode="plain")
    def serialize_epoch(self, dt: Any) -> Optional[int]:
        if isinstance(dt, datetime):
            return datetime_to_epoch(dt)
        return dt