from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_serializer
from app.common.utils import datetime_to_epoch


class KeycloakTokenExchangeRequest(BaseModel):
    code: str = Field(..., description="Authorization code dari alur OIDC Keycloak callback")
    redirect_uri: str = Field(..., description="Redirect URI yang didaftarkan di Keycloak client")


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "Bearer"
    expires_in: int
    refresh_token: Optional[str] = None
    refresh_expires_in: Optional[int] = None
    id_token: Optional[str] = None


class UserProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    keycloak_id: str
    username: str
    email: EmailStr
    full_name: str
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
    user_type: str
    status: str
    # Izinkan input datetime dari SQLAlchemy saat validasi
    created_at: Union[datetime, int]
    updated_at: Union[datetime, int]

    @field_serializer("created_at", "updated_at", mode="plain")
    def serialize_datetime_to_epoch(self, dt: Any) -> Optional[int]:
        if isinstance(dt, datetime):
            return datetime_to_epoch(dt)
        return dt


class UserContextResponse(BaseModel):
    user: UserProfileResponse
    roles: List[str]
    tenant_memberships: List[Dict[str, Any]]