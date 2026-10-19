from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import get_current_user
from app.modules.auth.models import User
from app.modules.preferences.schema import UserPreferenceResponse, UserPreferenceUpdate
from app.modules.preferences.service import UserPreferenceService

router = APIRouter(prefix="/users/me/preferences", tags=["User Preferences"])

@router.get("", response_model=UserPreferenceResponse)
async def get_my_preferences(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    pref = await UserPreferenceService.get_or_create(db, current_user.id)
    return UserPreferenceResponse(
        id=str(pref.id),
        user_id=str(pref.user_id),
        theme_mode=pref.theme_mode,
        locale=pref.locale,
        accent_color=pref.accent_color,
        custom_settings=pref.custom_settings,
        created_at=pref.created_at,
        updated_at=pref.updated_at
    )

@router.patch("", response_model=UserPreferenceResponse)
async def update_my_preferences(
    payload: UserPreferenceUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    pref = await UserPreferenceService.update(db, current_user.id, payload)
    return UserPreferenceResponse(
        id=str(pref.id),
        user_id=str(pref.user_id),
        theme_mode=pref.theme_mode,
        locale=pref.locale,
        accent_color=pref.accent_color,
        custom_settings=pref.custom_settings,
        created_at=int(pref.created_at.timestamp()),
        updated_at=int(pref.updated_at.timestamp()),
    )