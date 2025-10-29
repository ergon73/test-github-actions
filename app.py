"""
GitHub Actions CI/CD Demo Application
Flask REST API с основными эндпоинтами для демонстрации CI/CD
"""

from flask import Flask, jsonify
import datetime
import platform
import os

app = Flask(__name__)

@app.route('/')
def root():
    """
    Главная страница с информацией о приложении
    """
    return jsonify({
        "message": "GitHub Actions CI/CD Demo (GHCR + Production Deploy)",
        "status": "running",
        "repository": "ergon73/test-github-actions",
        "version": "1.0.0",
        "registry": "ghcr.io",
        "endpoints": [
            "/",
            "/health",
            "/time",
            "/info"
        ]
    })

@app.route('/health')
def health():
    """
    Health check endpoint для мониторинга и валидации
    Используется в docker healthcheck и post-deploy валидации
    """
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.datetime.utcnow().isoformat()
    })

@app.route('/time')
def time_now():
    """
    Возвращает текущее время сервера (UTC)
    Полезно для проверки работоспособности и timezone
    """
    now = datetime.datetime.utcnow()
    return jsonify({
        "server_time": now.isoformat(),
        "timezone": "UTC",
        "unix_timestamp": int(now.timestamp()),
        "formatted": now.strftime("%Y-%m-%d %H:%M:%S")
    })

@app.route('/info')
def system_info():
    """
    Системная информация о окружении
    Полезно для debug и проверки что запущен правильный контейнер
    """
    return jsonify({
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "hostname": os.environ.get("HOSTNAME", "unknown"),
        "dockerized": os.path.exists("/.dockerenv"),
        "working_directory": os.getcwd(),
        "environment": os.environ.get("FLASK_ENV", "development"),
        # Добавляем метку коммита из CI/CD для верификации версии
        "commit_sha": os.environ.get("COMMIT_SHA", "unknown")
    })

if __name__ == "__main__":
    # Получаем порт из переменной окружения (по умолчанию 5000)
    port = int(os.environ.get("PORT", 5000))
    
    # Запускаем приложение
    # В production используется gunicorn (см. Dockerfile CMD)
    # Этот блок только для локального dev-запуска
    app.run(host="0.0.0.0", port=port, debug=False)
