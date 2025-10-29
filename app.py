"""
GitHub Actions CI/CD Demo Application
Flask REST API с основными эндпоинтами для демонстрации CI/CD
"""

from flask import Flask, jsonify, request, g
import datetime
import platform
import os
import time

app = Flask(__name__)

# Метка старта процесса приложения (UTC)
PROCESS_STARTED_AT_UTC = datetime.datetime.utcnow()

# Примитивные in-memory метрики по эндпоинтам
ENDPOINT_STATS = {}


@app.before_request
def _start_timer():
    g._request_started_at = time.perf_counter()


@app.after_request
def _collect_metrics(response):
    try:
        started = getattr(g, "_request_started_at", None)
        if started is not None:
            elapsed_ms = (time.perf_counter() - started) * 1000.0
            endpoint = request.endpoint or "unknown"
            stats = ENDPOINT_STATS.setdefault(endpoint, {"count": 0, "total_ms": 0.0})
            stats["count"] += 1
            stats["total_ms"] += float(elapsed_ms)
    finally:
        return response

@app.route('/')
def root():
    """
    Главная страница с информацией о приложении
    """
    return jsonify({
        "message": "GitHub Actions CI/CD Demo (GHCR + Production Deploy)",
        "status": "running",
        "repository": "ergon73/test-github-actions",
        "version": "1.0.1",
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

@app.route('/uptime')
def uptime():
    """
    Возвращает аптайм процесса приложения и системы (если доступно)
    """
    now = datetime.datetime.utcnow()
    process_uptime = (now - PROCESS_STARTED_AT_UTC).total_seconds()

    system_uptime = None
    try:
        # На Linux доступен файл /proc/uptime: "<seconds> <idle_seconds>"
        if os.path.exists('/proc/uptime'):
            with open('/proc/uptime', 'r') as f:
                first = f.read().strip().split()[0]
                system_uptime = float(first)
    except Exception:
        # Не критично, просто не заполним поле
        system_uptime = None

    return jsonify({
        "now_utc": now.isoformat(),
        "process_started_at_utc": PROCESS_STARTED_AT_UTC.isoformat(),
        "process_uptime_sec": int(process_uptime),
        "system_uptime_sec": int(system_uptime) if isinstance(system_uptime, float) else None
    })


@app.route('/metrics')
def metrics():
    """
    Возвращает базовые метрики приложения:
    - аптайм
    - суммарное число запросов
    - по каждому эндпоинту: count и avg_latency_ms
    """
    now = datetime.datetime.utcnow()
    uptime_sec = int((now - PROCESS_STARTED_AT_UTC).total_seconds())

    per_endpoint = {}
    total_requests = 0
    for endpoint, s in ENDPOINT_STATS.items():
        count = int(s.get("count", 0))
        total_ms = float(s.get("total_ms", 0.0))
        avg_ms = (total_ms / count) if count > 0 else 0.0
        per_endpoint[endpoint] = {
            "count": count,
            "avg_latency_ms": round(avg_ms, 2)
        }
        total_requests += count

    return jsonify({
        "now_utc": now.isoformat(),
        "uptime_sec": uptime_sec,
        "total_requests": total_requests,
        "endpoints": per_endpoint
    })

if __name__ == "__main__":
    # Получаем порт из переменной окружения (по умолчанию 5000)
    port = int(os.environ.get("PORT", 5000))
    
    # Запускаем приложение
    # В production используется gunicorn (см. Dockerfile CMD)
    # Этот блок только для локального dev-запуска
    app.run(host="0.0.0.0", port=port, debug=False)
