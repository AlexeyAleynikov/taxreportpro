FROM python:3.12-slim

# Системные зависимости (OCR, PDF)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc curl poppler-utils \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Зависимости Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Создаём директории для загруженных файлов
RUN mkdir -p /app/uploads /app/logs

# Непривилегированный пользователь
RUN adduser --disabled-password --gecos "" appuser \
    && chown -R appuser:appuser /app
USER appuser

CMD ["gunicorn", "app.main:app", \
     "-k", "uvicorn.workers.UvicornWorker", \
     "--workers", "4", \
     "--bind", "0.0.0.0:8000", \
     "--access-logfile", "-", \
     "--error-logfile", "-"]
