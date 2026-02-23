#!/usr/bin/env bash
# scripts/deploy.sh
# Деплой / обновление TaxReport Pro
# Использование:
#   ./scripts/deploy.sh              — обычное обновление
#   ./scripts/deploy.sh --first-run  — первый запуск (SSL + миграции)

set -euo pipefail

FIRST_RUN=false
for arg in "$@"; do
  [[ "$arg" == "--first-run" ]] && FIRST_RUN=true
done

if [[ ! -f ".env" ]]; then
  echo "❌ Файл .env не найден. Скопируйте .env.example и заполните."
  exit 1
fi

source .env

echo "=== TaxReport Pro: деплой ==="
echo "Домен: ${APP_DOMAIN}"

# Собираем образы
echo "→ Сборка Docker образов..."
docker compose build --pull

if [[ "$FIRST_RUN" == "true" ]]; then
  echo "→ Первый запуск: получение SSL сертификата..."
  # Запускаем только nginx для ACME challenge
  docker compose up -d nginx

  docker compose run --rm certbot \
    certbot certonly \
    --webroot -w /var/www/certbot \
    --email "${CERTBOT_EMAIL}" \
    --agree-tos --no-eff-email \
    -d "${APP_DOMAIN}"

  docker compose down
fi

# Запускаем все сервисы
echo "→ Запуск сервисов..."
docker compose up -d

# Ждём готовности БД
echo "→ Ожидание готовности PostgreSQL..."
until docker compose exec -T db pg_isready -U "${POSTGRES_USER}" -d "${POSTGRES_DB}" &>/dev/null; do
  sleep 2
done

# Применяем миграции
echo "→ Применение миграций Alembic..."
docker compose exec -T api alembic upgrade head

if [[ "$FIRST_RUN" == "true" ]]; then
  echo "→ Bootstrap: создание первого администратора..."
  docker compose exec -T api python -c "
import asyncio
from app.core.database import AsyncSessionLocal
from app.services.user_service import UserService
from app.services.settings_service import SettingsService
import os

async def bootstrap():
    async with AsyncSessionLocal() as db:
        ss = SettingsService(db)
        await ss.set('registration_open', 'true')
        await db.commit()
        print('Настройки по умолчанию установлены')

asyncio.run(bootstrap())
"
fi

echo ""
echo "✅ Деплой завершён!"
echo "Сайт доступен по адресу: https://${APP_DOMAIN}"
echo ""
echo "Логи: docker compose logs -f api"
