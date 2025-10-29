# Эксплуатация на VPS (операции, диагностика, откаты)

## Путь и параметры
- Путь деплоя: `/opt/test-github-actions`
- Контейнер: `test-github-actions`
- Образ: `ghcr.io/ergon73/test-github-actions:latest`
- Порт: `5000/tcp`

## Операции
```bash
cd /opt/test-github-actions
# Статус
docker compose ps
# Логи (200 строк)
docker compose logs --no-color | tail -n 200
# Health вручную
curl -sf http://localhost:5000/health
# Перезапуск
docker compose restart
# Обновление latest
docker compose pull
docker compose up -d
# Остановка
docker compose down
```

## Сеть/фаервол
```bash
ss -lntp | grep :5000 || netstat -tulpn | grep :5000
ufw status
```

## Трассировка версий
- В контейнер передаётся `COMMIT_SHA` из `${{ github.sha }}`
- Проверка: `curl http://<ip>:5000/info | jq` → поле `commit_sha`

## Быстрый откат (rollback)
```bash
cd /opt/test-github-actions
# укажите нужный sha вместо <sha>
sed -i "s#:latest#:sha-<sha>#" docker-compose.yml
docker compose pull
docker compose up -d
```

## Примечания
- Непривилегированный пользователь в контейнере
- Секреты только через GitHub Secrets
- Post‑deploy health‑валидация обязательна
- В slim‑образе нет curl → healthcheck через python
