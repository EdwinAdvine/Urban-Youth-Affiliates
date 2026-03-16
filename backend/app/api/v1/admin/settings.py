from datetime import datetime, timezone
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.deps import require_admin
from app.models.user import User
from app.models.platform_setting import PlatformSetting

router = APIRouter()


@router.get("/admin/settings")
async def get_settings(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_admin),
):
    result = await db.execute(select(PlatformSetting))
    settings_list = result.scalars().all()
    return {s.key: s.value for s in settings_list}


@router.patch("/admin/settings/{key}")
async def update_setting(
    key: str,
    value: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_admin),
):
    result = await db.execute(select(PlatformSetting).where(PlatformSetting.key == key))
    setting = result.scalar_one_or_none()
    if setting:
        setting.value = value
        setting.updated_by = user.id
        setting.updated_at = datetime.now(timezone.utc)
    else:
        setting = PlatformSetting(key=key, value=value, updated_by=user.id)
        db.add(setting)
    await db.commit()
    return {"key": key, "value": value}
