# TaxReport Pro

Система сбора, хранения и анализа налоговых данных физических лиц (РФ и США).

## Стек

| Слой | Технология |
|------|-----------|
| Backend | Python 3.12, FastAPI, SQLAlchemy 2, Alembic |
| Frontend | React 18, Vite, TypeScript, TailwindCSS |
| БД | PostgreSQL 16 |
| Кэш / очереди | Redis 7, Celery |
| Авторизация | Telegram Login Widget + JWT |
| Веб-сервер | Nginx + Uvicorn (Gunicorn) |
| Контейнеризация | Docker + Docker Compose |

## Быстрый старт (продакшн, Ubuntu 24.04)

```bash
# 1. Клонируйте репозиторий
git clone https://github.com/YOUR_ORG/taxreportpro.git
cd taxreportpro

# 2. Скопируйте и заполните переменные окружения
cp .env.example .env
nano .env   # заполните секреты (см. .env.example)

# 3. Запустите
./scripts/deploy.sh
```

## Структура проекта

```
taxreportpro/
├── backend/          # FastAPI приложение
│   ├── app/
│   │   ├── api/      # Роутеры (v1)
│   │   ├── core/     # Настройки, безопасность, зависимости
│   │   ├── models/   # SQLAlchemy модели
│   │   ├── schemas/  # Pydantic схемы
│   │   └── services/ # Бизнес-логика
│   ├── migrations/   # Alembic
│   └── tests/
├── frontend/         # React/Vite SPA
│   └── src/
├── nginx/            # Nginx конфиги
├── scripts/          # Вспомогательные скрипты
├── docker-compose.yml
├── docker-compose.dev.yml
└── .env.example      # Шаблон переменных (без секретов)
```

## Авторизация через Telegram

1. Создайте бота через [@BotFather](https://t.me/botfather)
2. Получите `TELEGRAM_BOT_TOKEN` и `TELEGRAM_BOT_USERNAME`
3. Укажите в `.env`
4. Настройте домен бота: `/setdomain` → `taxrep.finitin.us`

## Роли пользователей

- **admin** — полные права, управление настройками системы
- **manager** — добавление/ведение клиентов, работа с профилями
- **client** — просмотр своих профилей (только через менеджера)

Администратор может **запретить самостоятельную регистрацию** новых пользователей в панели настроек (`/admin/settings` → «Разрешить регистрацию новых пользователей»).

## Переменные окружения

Все секреты хранятся в `.env` (не коммитится в git, см. `.gitignore`).  
Шаблон без значений — `.env.example` (коммитится).

## Деплой на новый сервер

```bash
# Установка зависимостей
./scripts/server_setup.sh

# Первый запуск + миграции БД
./scripts/deploy.sh --first-run
```
