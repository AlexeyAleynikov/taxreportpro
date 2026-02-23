"""Сервис работы с пользователями."""

from datetime import datetime, timezone
from typing import Optional, List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import User, UserRole


class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_telegram_id(self, telegram_id: str) -> Optional[User]:
        result = await self.db.execute(
            select(User).where(User.telegram_id == str(telegram_id))
        )
        return result.scalar_one_or_none()

    async def create_from_telegram(self, tg_data: dict) -> User:
        """Создаёт нового пользователя после первого входа через Telegram."""
        # Первый пользователь в системе автоматически становится администратором
        count_result = await self.db.execute(select(User))
        is_first = len(count_result.scalars().all()) == 0

        # Также проверяем FIRST_ADMIN_TELEGRAM_ID
        from app.core.config import settings
        is_forced_admin = (
            settings.FIRST_ADMIN_TELEGRAM_ID and
            str(tg_data["telegram_id"]) == str(settings.FIRST_ADMIN_TELEGRAM_ID)
        )

        user = User(
            telegram_id=tg_data["telegram_id"],
            first_name=tg_data.get("first_name", ""),
            last_name=tg_data.get("last_name", ""),
            username=tg_data.get("username"),
            photo_url=tg_data.get("photo_url"),
            role=UserRole.admin if (is_first or is_forced_admin) else UserRole.manager,
        )
        self.db.add(user)
        await self.db.flush()
        return user

    async def update_last_login(self, user_id: int):
        user = await self.db.get(User, user_id)
        if user:
            user.last_login = datetime.now(timezone.utc)
            await self.db.flush()

    async def list_all(self) -> List[User]:
        result = await self.db.execute(select(User).order_by(User.created_at))
        return result.scalars().all()

    async def set_role(self, user_id: int, role: str) -> User:
        from fastapi import HTTPException
        if role not in UserRole.__members__:
            raise HTTPException(status_code=400, detail="Неверная роль")
        user = await self.db.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Пользователь не найден")
        user.role = UserRole(role)
        await self.db.flush()
        return user

    async def set_active(self, user_id: int, is_active: bool) -> User:
        from fastapi import HTTPException
        user = await self.db.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Пользователь не найден")
        user.is_active = is_active
        await self.db.flush()
        return user
