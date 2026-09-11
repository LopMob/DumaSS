#!/usr/bin/env bash
# Выполняется НА app-server, от пользователя с sudo (не от root напрямую).
# Идемпотентен: повторный запуск не ломает уже настроенное.
set -euo pipefail

APP_USER="duma"
APP_DIR="/opt/duma-project"
CONFIG_DIR="/etc/duma"

echo "== 1. Системные пакеты =="
sudo apt-get update -y
sudo apt-get install -y python3 python3-venv python3-pip git ufw

echo "== 2. Пользователь для запуска приложения (без sudo, без интерактивного входа) =="
if ! id "$APP_USER" &>/dev/null; then
    sudo useradd --system --home "$APP_DIR" --shell /usr/sbin/nologin "$APP_USER"
    echo "Создан системный пользователь $APP_USER (login shell отключён — только для systemd)."
else
    echo "Пользователь $APP_USER уже существует."
fi

echo "== 3. Каталог приложения =="
sudo mkdir -p "$APP_DIR"
if [ ! -d "$APP_DIR/.git" ]; then
    sudo git clone https://github.com/<ваш-логин>/duma-project.git "$APP_DIR"
else
    echo "Репозиторий уже склонирован, пропускаем git clone."
fi
sudo chown -R "$APP_USER":"$APP_USER" "$APP_DIR"
sudo chmod 750 "$APP_DIR"

echo "== 4. Виртуальное окружение и зависимости =="
sudo -u "$APP_USER" python3 -m venv "$APP_DIR/.venv"
sudo -u "$APP_USER" "$APP_DIR/.venv/bin/pip" install --upgrade pip
sudo -u "$APP_USER" "$APP_DIR/.venv/bin/pip" install -r "$APP_DIR/requirements.txt"

echo "== 5. Каталог конфигурации, отдельно от кода =="
sudo mkdir -p "$CONFIG_DIR"
if [ ! -f "$CONFIG_DIR/duma.env" ]; then
    sudo cp "$APP_DIR/.env.example" "$CONFIG_DIR/duma.env"
    echo "!! Отредактируйте $CONFIG_DIR/duma.env вручную (DATABASE_URL на адрес db-server) !!"
fi
sudo chown "$APP_USER":"$APP_USER" "$CONFIG_DIR/duma.env"
sudo chmod 600 "$CONFIG_DIR/duma.env"   # читает только владелец (пользователь duma)

echo "Готово. Дальше: отредактируйте $CONFIG_DIR/duma.env и запустите install_service.sh"
