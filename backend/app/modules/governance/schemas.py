from datetime import datetime
from typing import Any, Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field, field_serializer, field_validator
from app.common.utils import datetime_to_epoch


class ApprovalRequestCreate(BaseModel):
    bundle_id: UUID = Field(..., description="ID bundle yang ingin diajukan ke environment target")
    target_environment: str = Field(default="production", pattern="^(staging|production)$")
    test_suite_rego: Optional[str] = Field(
        None,
        description="Isi Rego unit test tambahan (_test.rego). Kosongkan untuk menjalankan test bawaan."
    )


class ReviewAction(BaseModel):
    action: str = Field(..., description="Pilihan tindakan: APPROVE atau REJECT")
    review_notes: Optional[str] = Field(None, max_length=1000)

    @field_validator("action")
    @classmethod
    def validate_action(cls, v: str) -> str:
        v_upper = v.strip().upper()
        if v_upper not in {"APPROVE", "REJECT"}:
            raise ValueError("Action harus bernilai 'APPROVE' atau 'REJECT'.")
        return v_upper


class ApprovalResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    organization_id: UUID
    bundle_id: UUID
    requester_id: UUID
    reviewer_id: Optional[UUID] = None
    target_environment: str
    status: str
    tests_passed: bool
    test_output: Optional[str] = None
    review_notes: Optional[str] = None
    reviewed_at: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    @field_serializer("reviewed_at", "created_at", "updated_at", mode="plain")
    def serialize_epoch(self, dt: Any) -> Optional[int]:
        if isinstance(dt, datetime):
            return datetime_to_epoch(dt)
        return dt