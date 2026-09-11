#!/usr/bin/env bash
# Выполняется НА app-server, от пользователя с sudo, ПОСЛЕ setup_app_server.sh
# и после того, как /etc/duma/duma.env отредактирован под реальный DATABASE_URL.
set -euo pipefail

APP_DIR="/opt/duma-project"

echo "== 1. Применяем миграции БД (от имени пользователя duma) =="
sudo -u duma bash -c "cd $APP_DIR && set -a && source /etc/duma/duma.env && set +a && .venv/bin/python -m alembic upgrade head"

echo "== 2. Устанавливаем unit-файл =="
sudo cp "$APP_DIR/deploy/duma.service" /etc/systemd/system/duma.service
sudo systemctl daemon-reload

echo "== 3. Включаем автозапуск при старте системы и запускаем сейчас =="
sudo systemctl enable duma.service
sudo systemctl restart duma.service

echo "== 4. Статус =="
sudo systemctl status duma.service --no-pager
echo
echo "Полезные команды для защиты:"
echo "  sudo systemctl status duma      — состояние службы"
echo "  sudo systemctl stop duma        — остановка"
echo "  sudo systemctl start duma       — запуск"
echo "  sudo systemctl restart duma     — перезапуск"
echo "  journalctl -u duma -f           — журнал в реальном времени"
echo "  sudo ss -tlnp | grep 8000       — кто слушает порт"
