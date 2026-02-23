"""Авторизация через Telegram Login Widget."""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import create_access_token, create_refresh_token, decode_token
from app.core.telegram_auth import extract_telegram_user
from app.services.user_service import UserService
from app.services.settings_service import SettingsService

router = APIRouter()


class TelegramAuthData(BaseModel):
    id: int
    first_name: str
    last_name: str = ""
    username: str = ""
    photo_url: str = ""
    auth_date: int
    hash: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: dict


@router.post("/telegram", response_model=TokenResponse)
async def telegram_login(
    data: TelegramAuthData,
    db: AsyncSession = Depends(get_db),
):
    """
    Вход через Telegram Login Widget.
    Виджет передаёт подписанные данные — проверяем HMAC и выдаём JWT.
    """
    raw = data.model_dump()
    tg_user = extract_telegram_user(raw)
    if not tg_user:
        raise HTTPException(status_code=401, detail="Невалидные данные Telegram")

    user_service = UserService(db)
    settings_service = SettingsService(db)

    # Проверяем, существует ли уже пользователь
    user = await user_service.get_by_telegram_id(tg_user["telegram_id"])

    if user is None:
        # Новый пользователь — проверяем, разрешена ли регистрация
        registration_open = await settings_service.get("registration_open", default="true")
        if registration_open.lower() != "true":
            raise HTTPException(
                status_code=403,
                detail="Регистрация новых пользователей закрыта администратором",
            )
        user = await user_service.create_from_telegram(tg_user)

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Аккаунт заблокирован")

    # Обновляем last_login
    await user_service.update_last_login(user.id)

    access = create_access_token(subject=user.telegram_id, role=user.role.value)
    refresh = create_refresh_token(subject=user.telegram_id)

    return TokenResponse(
        access_token=access,
        refresh_token=refresh,
        user={
            "id": user.id,
            "telegram_id": user.telegram_id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "username": user.username,
            "role": user.role.value,
        },
    )


class RefreshRequest(BaseModel):
    refresh_token: str


@router.post("/refresh", response_model=dict)
async def refresh_token(
    body: RefreshRequest,
    db: AsyncSession = Depends(get_db),
):
    payload = decode_token(body.refresh_token)
    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Неверный тип токена")

    user_service = UserService(db)
    user = await user_service.get_by_telegram_id(payload["sub"])
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="Пользователь не найден")

    access = create_access_token(subject=user.telegram_id, role=user.role.value)
    return {"access_token": access, "token_type": "bearer"}
