from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, Literal
from datetime import datetime

ThemeMode = Literal["dark", "light", "system"]
AccentColor = Literal["zinc", "blue", "violet", "emerald", "rose"]

class UserPreferenceBase(BaseModel):
    theme_mode: ThemeMode = "system"
    locale: str = Field(default="id", max_length=10)
    accent_color: AccentColor = "zinc"
    custom_settings: Dict[str, Any] = Field(default_factory=dict)

class UserPreferenceUpdate(BaseModel):
    theme_mode: Optional[ThemeMode] = None
    locale: Optional[str] = None
    accent_color: Optional[AccentColor] = None
    custom_settings: Optional[Dict[str, Any]] = None

class UserPreferenceResponse(UserPreferenceBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True