# GitHub Actions CI/CD Demo (GHCR + Production Deploy)

> **Ultimate версия:** комбинация лучших практик от Claude, ChatGPT и Gemini

Демонстрационный проект для изучения CI/CD с GitHub Actions, GHCR и production деплоем на VPS.

## 🎯 Особенности

✅ **Modern Stack:**
- Flask REST API
- Docker + Docker Compose
- GitHub Container Registry (GHCR)
- GitHub Actions for CI/CD

✅ **Production-Ready:**
- Непривилегированный пользователь в контейнере
- Health check валидация после деплоя
- Строгий режим bash (`set -euo pipefail`)
- Автоматические теги (latest + sha)

✅ **Security:**
- Секреты через GitHub Secrets
- SSH key authentication
- No hardcoded credentials

## 🏗️ Архитектура

```
┌──────────────┐
│   Developer  │
│   git push   │
└──────┬───────┘
       │
       ↓
┌──────────────────────┐
│   GitHub Actions     │
│   ├─ Build & Test    │
│   ├─ Push to GHCR    │
│   └─ Deploy via SSH  │
└──────┬───────────────┘
       │
       ↓
┌──────────────────────┐
│   VPS Server         │
│   95.163.232.237     │
│   └─ Docker Container│
└──────────────────────┘
```

## 📋 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Информация о приложении |
| `/health` | GET | Health check для мониторинга |
| `/time` | GET | Текущее время сервера (UTC) |
| `/info` | GET | Системная информация |

## 🚀 Быстрый старт

### Локальный запуск без Docker

```bash
# Клонирование
git clone https://github.com/ergon73/test-github-actions.git
cd test-github-actions

# Создание виртуального окружения
python3 -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# Установка зависимостей
pip install -r requirements.txt

# Запуск приложения
python app.py

# Приложение доступно на http://localhost:5000
```

### Локальный запуск с Docker

```bash
# Сборка образа
docker build -t test-app .

# Запуск контейнера
docker run -d -p 5000:5000 --name test-app test-app

# Проверка
curl http://localhost:5000/health

# Остановка
docker stop test-app
docker rm test-app
```

### Локальный запуск с Docker Compose

```bash
# Запуск
docker compose up -d

# Проверка логов
docker compose logs -f

# Остановка
docker compose down
```

## 🔄 CI/CD Pipeline

### Workflow триггеры:
- `push` в `main` → Build + Deploy
- `pull_request` в `main` → Build only (без деплоя)

### Этапы pipeline:

#### Job 1: Build
1. ✓ Checkout кода
2. ✓ Setup Python 3.11
3. ✓ Установка зависимостей
4. ✓ Smoke test (проверка импорта)
5. ✓ Login в GHCR (через GITHUB_TOKEN)
6. ✓ Docker metadata (генерация тегов)
7. ✓ Build & Push образа в GHCR

#### Job 2: Deploy (только при push в main)
1. ✓ SSH подключение к VPS
2. ✓ (Опционально) Login в GHCR на сервере
3. ✓ Подготовка директории `/opt/test-github-actions`
4. ✓ Создание `docker-compose.yml`
5. ✓ Pull последнего образа
6. ✓ Остановка старого контейнера
7. ✓ Запуск нового контейнера
8. ✓ **Health check валидация** (критический шаг!)
9. ✓ Проверка статуса контейнера

## 📦 GitHub Secrets

Необходимо настроить следующие секреты в репозитории:

| Secret Name | Description | Required |
|-------------|-------------|----------|
| `SSH_HOST` | IP адрес VPS сервера | ✅ Yes |
| `SSH_USERNAME` | SSH пользователь (обычно root) | ✅ Yes |
| `SSH_PRIVATE_KEY` | Приватный SSH ключ (без passphrase) | ✅ Yes |
| `CR_PAT` | Personal Access Token для GHCR | ⭐ Optional* |

\* CR_PAT нужен только если пакет в GHCR приватный

### Важно для GitHub Actions:
- В репозитории: **Settings → Actions → General**
- **Workflow permissions** → Select **"Read and write permissions"**
- Сохрани изменения

## 🌳 GitFlow

Используем модель ветвления:

```
feature/xxx → develop → main
                        ↓
                   production
```

### Процесс разработки:

1. Создай feature ветку: `git checkout -b feature/new-feature`
2. Разработай и закоммить изменения
3. Создай PR: `feature/new-feature` → `develop`
4. После review смёржи в `develop`
5. Когда готов релиз: создай PR `develop` → `main`
6. После мерджа в `main` → автоматический деплой на production

## 🔧 Production сервер

### Требования:
- Ubuntu 20.04/22.04/24.04
- Docker 20.10+
- Docker Compose plugin (v2.x)
- Открыт порт 5000
- SSH доступ

### Установка Docker на сервере:

```bash
# Подключение к серверу
ssh root@95.163.232.237

# Установка Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Проверка
docker --version
docker compose version

# Добавление пользователя в группу docker (если не root)
sudo usermod -aG docker $USER
```

### Проверка на сервере:

```bash
# Проверка контейнеров
docker ps

# Логи приложения
docker logs test-github-actions

# Health check
curl http://localhost:5000/health
```

## 📊 Мониторинг

### Health check endpoint:
```bash
curl http://95.163.232.237:5000/health
```

### Проверка статуса:
```bash
# На сервере
docker ps | grep test-github-actions
docker logs -f test-github-actions
```

### GitHub Actions статус:
```
https://github.com/ergon73/test-github-actions/actions
```

## 🐛 Troubleshooting

### Workflow не запускается:
- Проверь путь: `.github/workflows/deploy.yml`
- Проверь **Workflow permissions** в настройках Actions

### Build failed:
```bash
# Проверь локально
docker build -t test-app .
python -c "from app import app"
```

### Deploy failed (SSH):
- Проверь что SSH ключ скопирован полностью
- Проверь что ключ без passphrase
- Тест: `ssh root@95.163.232.237`

### Health check failed:
```bash
# На сервере
docker logs test-github-actions
docker ps -a
curl http://localhost:5000/health
```

## 🎓 Технологии и best practices

- ✅ Flask REST API
- ✅ Gunicorn WSGI server
- ✅ Docker multi-stage (не используется для простоты)
- ✅ Непривилегированный пользователь в контейнере
- ✅ GHCR вместо Docker Hub (меньше настройки)
- ✅ docker/metadata-action для автоматических тегов
- ✅ Строгий режим bash (`set -euo pipefail`)
- ✅ Health check валидация после деплоя
- ✅ Подробное логирование в workflow
- ✅ GitFlow модель ветвления

## 📄 Лицензия

MIT

## 👤 Автор

GitHub: [@ergon73](https://github.com/ergon73)

---

**Made with ❤️ combining best practices from Claude, ChatGPT and Gemini**
