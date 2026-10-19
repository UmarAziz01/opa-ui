from datetime import datetime
from typing import Any, List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_serializer, field_validator
from app.common.utils import datetime_to_epoch


class ApplicationCreateRequest(BaseModel):
    display_name: str = Field(..., min_length=3, max_length=150, example="Payment Gateway API")
    slug: str = Field(..., min_length=2, max_length=100, example="payment-gateway")
    description: Optional[str] = Field(None, max_length=500)
    sidecar_port: Optional[int] = Field(
        None,
        description="Port kustom (18100-18999). Kosongkan untuk alokasi otomatis oleh sistem.",
    )

    @field_validator("slug")
    @classmethod
    def validate_slug(cls, v: str) -> str:
        clean = v.strip().lower()
        if not clean.replace("-", "").isalnum():
            raise ValueError("Slug hanya boleh berisi karakter alfanumerik huruf kecil dan strip (-).")
        return clean


class ApplicationUpdateRequest(BaseModel):
    display_name: Optional[str] = Field(None, min_length=3, max_length=150)
    description: Optional[str] = Field(None, max_length=500)


class ApplicationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    organization_id: UUID
    slug: str
    display_name: str
    description: Optional[str] = None
    sidecar_port: Optional[int] = None
    created_by: UUID
    created_at: datetime
    updated_at: datetime

    @field_serializer("created_at", "updated_at", mode="plain")
    def serialize_epoch(self, dt: Any) -> Optional[int]:
        if isinstance(dt, datetime):
            return datetime_to_epoch(dt)
        return dt


class ServiceTokenCreateRequest(BaseModel):
    name: str = Field(..., min_length=3, max_length=100, example="CI/CD Deploy Token")
    expires_in_days: Optional[int] = Field(None, ge=1, le=365, example=30)


class ServiceTokenResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    application_id: UUID
    name: str
    token_prefix: str
    created_at: datetime
    expires_at: Optional[int] = None
    revoked_at: Optional[int] = None

    @field_serializer("created_at", "expires_at", "revoked_at", mode="plain")
    def serialize_epoch(self, dt: Any) -> Optional[int]:
        if isinstance(dt, datetime):
            return datetime_to_epoch(dt)
        return dt


class ServiceTokenCreatedResponse(ServiceTokenResponse):
    raw_token: str = Field(..., description="Token rahasia lengkap. Hanya ditampilkan satu kali saat pembuatan.")


class SidecarDeployResponse(BaseModel):
    application_id: UUID
    container_name: str
    status: str
    host_port: int
    network: str
    message: str


class SidecarHealthResponse(BaseModel):
    container_name: str
    docker_status: str
    opa_engine_ready: bool
    port: Optional[int] = None
    message: str