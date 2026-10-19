from datetime import datetime
from typing import Any, List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_serializer, field_validator
from app.common.utils import datetime_to_epoch


class OrganizationCreateRequest(BaseModel):
    name: str = Field(..., min_length=3, max_length=150, example="Engineering Division")
    slug: str = Field(..., min_length=2, max_length=100, example="engineering")
    description: Optional[str] = Field(None, max_length=500)

    @field_validator("slug")
    @classmethod
    def validate_slug(cls, v: str) -> str:
        clean_slug = v.strip().lower()
        if not clean_slug.replace("-", "").isalnum():
            raise ValueError("Slug organisasi hanya boleh berisi alfanumerik huruf kecil dan tanda hubung (-).")
        return clean_slug


class OrganizationUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=150)
    description: Optional[str] = Field(None, max_length=500)


class OrganizationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    name: str
    slug: str
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    @field_serializer("created_at", "updated_at", mode="plain")
    def serialize_epoch(self, dt: Any) -> Optional[int]:
        if isinstance(dt, datetime):
            return datetime_to_epoch(dt)
        return dt


class OrganizationMemberAssignRequest(BaseModel):
    user_id: UUID = Field(..., description="ID user yang akan ditambahkan ke organisasi")
    org_role: str = Field(
        default="DEVELOPER",
        description="Role organisasi: ORG_ADMIN, DEVELOPER, atau VIEWER",
        example="DEVELOPER",
    )

    @field_validator("org_role")
    @classmethod
    def validate_role(cls, v: str) -> str:
        allowed = {"ORG_ADMIN", "DEVELOPER", "VIEWER"}
        if v not in allowed:
            raise ValueError(f"Role harus salah satu dari: {', '.join(allowed)}")
        return v


class OrganizationMemberResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    organization_id: UUID
    user_id: UUID
    assigned_by: UUID
    org_role: str
    created_at: datetime
    updated_at: datetime

    @field_serializer("created_at", "updated_at", mode="plain")
    def serialize_epoch(self, dt: Any) -> Optional[int]:
        if isinstance(dt, datetime):
            return datetime_to_epoch(dt)
        return dt