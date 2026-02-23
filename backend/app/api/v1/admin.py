"""Административная панель — настройки системы и управление пользователями."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.core.database import get_db
from app.core.security import require_admin
from app.services.settings_service import SettingsService
from app.services.user_service import UserService

router = APIRouter()


# ── Настройки системы ─────────────────────────────────────────────────────────

class SettingUpdate(BaseModel):
    value: str


ALLOWED_SETTINGS = {
    "registration_open": "Разрешить самостоятельную регистрацию новых пользователей (true/false)",
    "default_locale": "Язык интерфейса по умолчанию (ru/en)",
    "session_timeout_minutes": "Время сессии в минутах",
    "require_2fa": "Требовать двухфакторную аутентификацию (true/false)",
}


@router.get("/settings")
async def get_settings(
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_admin),
):
    """Возвращает все системные настройки."""
    svc = SettingsService(db)
    result = {}
    for key, description in ALLOWED_SETTINGS.items():
        value = await svc.get(key, default=None)
        result[key] = {"value": value, "description": description}
    return result


@router.put("/settings/{key}")
async def update_setting(
    key: str,
    body: SettingUpdate,
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_admin),
):
    """Обновляет системную настройку."""
    if key not in ALLOWED_SETTINGS:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail=f"Неизвестная настройка: {key}")
    svc = SettingsService(db)
    await svc.set(key, body.value, updated_by_id=admin.id)
    return {"key": key, "value": body.value}


# ── Управление пользователями ─────────────────────────────────────────────────

class UserRoleUpdate(BaseModel):
    role: str  # admin | manager | client


class UserStatusUpdate(BaseModel):
    is_active: bool


@router.get("/users")
async def list_users(
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_admin),
):
    svc = UserService(db)
    users = await svc.list_all()
    return [
        {
            "id": u.id,
            "telegram_id": u.telegram_id,
            "first_name": u.first_name,
            "last_name": u.last_name,
            "username": u.username,
            "role": u.role.value,
            "is_active": u.is_active,
            "created_at": u.created_at.isoformat(),
            "last_login": u.last_login.isoformat() if u.last_login else None,
        }
        for u in users
    ]


@router.patch("/users/{user_id}/role")
async def set_user_role(
    user_id: int,
    body: UserRoleUpdate,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_admin),
):
    svc = UserService(db)
    user = await svc.set_role(user_id, body.role)
    return {"id": user.id, "role": user.role.value}


@router.patch("/users/{user_id}/status")
async def set_user_status(
    user_id: int,
    body: UserStatusUpdate,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_admin),
):
    svc = UserService(db)
    user = await svc.set_active(user_id, body.is_active)
    return {"id": user.id, "is_active": user.is_active}
