from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_serializer
from app.common.utils import datetime_to_epoch


# ── Permission Schemas ────────────────────────────────────────────────────────

class PermissionCreateRequest(BaseModel):
    resource: str = Field(..., min_length=2, max_length=100, example="documents")
    action: str = Field(..., min_length=2, max_length=50, example="read")
    description: Optional[str] = Field(None, max_length=255)


class PermissionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    organization_id: UUID
    resource: str
    action: str
    description: Optional[str] = None
    created_at: int

    @field_serializer("created_at", mode="plain")
    def serialize_epoch(self, dt: Any) -> Optional[int]:
        if isinstance(dt, datetime):
            return datetime_to_epoch(dt)
        return dt


# ── Role Schemas ──────────────────────────────────────────────────────────────

class RoleCreateRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, example="Document_Editor")
    description: Optional[str] = Field(None, max_length=255)
    permission_ids: List[UUID] = Field(default_factory=list, description="Daftar ID permission awal")


class RoleUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = Field(None, max_length=255)
    permission_ids: Optional[List[UUID]] = None


class RoleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    organization_id: UUID
    name: str
    description: Optional[str] = None
    permissions: List[PermissionResponse] = []
    created_at: int
    updated_at: int

    @field_serializer("created_at", "updated_at", mode="plain")
    def serialize_epoch(self, dt: Any) -> Optional[int]:
        if isinstance(dt, datetime):
            return datetime_to_epoch(dt)
        return dt


# ── Subject / Target User Role Mapping Schemas ────────────────────────────────

class SubjectRoleAssignRequest(BaseModel):
    subject_identifier: str = Field(..., min_length=2, max_length=150, example="user-123@domain.com")
    role_id: UUID = Field(...)


class SubjectRoleMappingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    organization_id: UUID
    role_id: UUID
    subject_identifier: str
    created_at: int

    @field_serializer("created_at", mode="plain")
    def serialize_epoch(self, dt: Any) -> Optional[int]:
        if isinstance(dt, datetime):
            return datetime_to_epoch(dt)
        return dt


# ── OPA Simulation & Dry-Run Schemas ──────────────────────────────────────────

class PolicySimulationInput(BaseModel):
    subject: str = Field(..., example="alice")
    resource: str = Field(..., example="documents")
    action: str = Field(..., example="read")
    context: Optional[Dict[str, Any]] = Field(default_factory=dict)


class PolicySimulationResponse(BaseModel):
    allow: bool
    evaluated_at: int
    execution_time_ms: float
    rego_package: str
    details: Dict[str, Any]