"""
Верификация Telegram Login Widget.

Telegram передаёт данные пользователя с HMAC-SHA256 подписью.
Ключ подписи = SHA256(TELEGRAM_BOT_TOKEN).
"""

import hashlib
import hmac
import time
from typing import Optional

from app.core.config import settings


MAX_AUTH_AGE_SECONDS = 86_400  # 24 часа


def verify_telegram_auth(data: dict) -> bool:
    """
    Проверяет подпись данных, полученных от Telegram Login Widget.

    :param data: словарь полей от виджета (включая 'hash' и 'auth_date')
    :returns: True если подпись корректна и данные свежие
    """
    received_hash = data.get("hash", "")
    auth_date = int(data.get("auth_date", 0))

    # Проверка свежести
    if time.time() - auth_date > MAX_AUTH_AGE_SECONDS:
        return False

    # Строим data-check-string
    fields = {k: v for k, v in data.items() if k != "hash"}
    data_check_string = "\n".join(
        f"{k}={v}" for k, v in sorted(fields.items())
    )

    # Ключ = SHA256(bot_token)
    secret_key = hashlib.sha256(settings.TELEGRAM_BOT_TOKEN.encode()).digest()

    # Вычисляем HMAC
    expected_hash = hmac.new(
        secret_key,
        data_check_string.encode(),
        hashlib.sha256,
    ).hexdigest()

    return hmac.compare_digest(expected_hash, received_hash)


def extract_telegram_user(data: dict) -> Optional[dict]:
    """Возвращает нормализованный профиль пользователя из данных виджета."""
    if not verify_telegram_auth(data):
        return None
    return {
        "telegram_id": str(data["id"]),
        "first_name": data.get("first_name", ""),
        "last_name": data.get("last_name", ""),
        "username": data.get("username", ""),
        "photo_url": data.get("photo_url", ""),
    }
