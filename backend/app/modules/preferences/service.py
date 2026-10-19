import uuid
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.modules.preferences.models import UserPreference
from app.modules.preferences.schema import UserPreferenceUpdate

class UserPreferenceService:
    @staticmethod
    async def get_or_create(db: AsyncSession, user_id: uuid.UUID) -> UserPreference:
        stmt = select(UserPreference).where(UserPreference.user_id == user_id)
        result = await db.execute(stmt)
        pref = result.scalar_one_or_none()

        if not pref:
            pref = UserPreference(user_id=user_id)
            db.add(pref)
            await db.commit()
            await db.refresh(pref)

        return pref

    @staticmethod
    async def update(
        db: AsyncSession, user_id: uuid.UUID, payload: UserPreferenceUpdate
    ) -> UserPreference:
        pref = await UserPreferenceService.get_or_create(db, user_id)
        
        update_data = payload.model_dump(exclude_unset=True)
        for field, val in update_data.items():
            setattr(pref, field, val)

        await db.commit()
        await db.refresh(pref)
        return pref