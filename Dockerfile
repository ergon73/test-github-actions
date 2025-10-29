# ============================================================================
# Production-ready Dockerfile для Flask приложения
# Best practices:
# - Легковесный base image (python:3.11-slim)
# - Непривилегированный пользователь для безопасности
# - Multi-stage build не нужен (простое приложение)
# - Минимальный размер образа
# ============================================================================

# Используем официальный Python образ (slim версия)
FROM python:3.11-slim

# Метаданные образа
LABEL maintainer="ergon73"
LABEL description="GitHub Actions CI/CD Demo Application"
LABEL version="1.0.0"

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файл зависимостей
COPY requirements.txt .

# Устанавливаем зависимости
# --no-cache-dir: не кэшируем пакеты (меньше размер образа)
# --upgrade: обновляем pip до последней версии
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Копируем код приложения
COPY app.py .

# ============================================================================
# SECURITY: Создаём непривилегированного пользователя
# Best practice: никогда не запускай приложения от root в production
# ============================================================================
RUN useradd --create-home --shell /bin/bash appuser && \
    chown -R appuser:appuser /app

# Переключаемся на непривилегированного пользователя
USER appuser

# Открываем порт приложения
EXPOSE 5000

# Переменные окружения
ENV FLASK_APP=app.py \
    FLASK_ENV=production \
    PORT=5000 \
    PYTHONUNBUFFERED=1

# Healthcheck для Docker
# Проверяет что приложение отвечает каждые 30 секунд
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/health')"

# Запуск приложения через Gunicorn (production WSGI server)
# --bind: слушаем все интерфейсы на порту 5000
# --workers: 2 worker процесса (рекомендуется 2-4 × CPU cores)
# --timeout: таймаут для worker (60 секунд)
# --access-logfile: логи доступа в stdout
# --error-logfile: логи ошибок в stderr
CMD ["gunicorn", \
     "--bind", "0.0.0.0:5000", \
     "--workers", "2", \
     "--timeout", "60", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "app:app"]
