"""Celery приложение для фоновых задач."""
from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "taxreportpro",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)
celery_app.conf.timezone = "UTC"
