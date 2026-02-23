"""Сервис системных настроек (key-value в таблице system_settings)."""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import SystemSettings

# Значения по умолчанию
DEFAULTS = {
    "registration_open": "true",
    "default_locale": "ru",
    "session_timeout_minutes": "60",
    "require_2fa": "false",
}


class SettingsService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get(self, key: str, default: Optional[str] = None) -> Optional[str]:
        result = await self.db.execute(
            select(SystemSettings).where(SystemSettings.key == key)
        )
        row = result.scalar_one_or_none()
        if row:
            return row.value
        return DEFAULTS.get(key, default)

    async def set(self, key: str, value: str, updated_by_id: Optional[int] = None):
        result = await self.db.execute(
            select(SystemSettings).where(SystemSettings.key == key)
        )
        row = result.scalar_one_or_none()
        if row:
            row.value = value
            row.updated_by_id = updated_by_id
        else:
            row = SystemSettings(key=key, value=value, updated_by_id=updated_by_id)
            self.db.add(row)
        await self.db.flush()
