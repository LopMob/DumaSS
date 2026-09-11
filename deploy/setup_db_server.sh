#!/usr/bin/env bash
# Выполняется НА db-server, от пользователя с sudo.
set -euo pipefail

DB_NAME="duma"
DB_USER="duma_app"
APP_SERVER_IP="192.168.56.10"   # адрес app-server в host-only сети — поменяйте под свою схему

echo "== 1. Установка PostgreSQL =="
sudo apt-get update -y
sudo apt-get install -y postgresql postgresql-contrib

echo "== 2. Создание роли и базы данных (минимальные права — не суперпользователь) =="
sudo -u postgres psql <<SQL
DO \$\$
BEGIN
   IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = '${DB_USER}') THEN
      CREATE ROLE ${DB_USER} WITH LOGIN PASSWORD 'ЗАМЕНИТЕ_НА_СВОЙ_ПАРОЛЬ' NOSUPERUSER NOCREATEDB NOCREATEROLE;
   END IF;
END
\$\$;

SELECT 'CREATE DATABASE ${DB_NAME} OWNER ${DB_USER}'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '${DB_NAME}')\gexec
SQL
echo "!! Не забудьте заменить пароль в реальном запуске — здесь он для примера !!"

echo "== 3. Разрешаем подключения только с app-server (по IP), не отовсюду =="
PG_VERSION=$(psql -V | grep -oE '[0-9]+' | head -1)
PG_HBA="/etc/postgresql/${PG_VERSION}/main/pg_hba.conf"
PG_CONF="/etc/postgresql/${PG_VERSION}/main/postgresql.conf"

sudo cp "$PG_HBA" "${PG_HBA}.bak"
echo "host    ${DB_NAME}    ${DB_USER}    ${APP_SERVER_IP}/32    scram-sha-256" | sudo tee -a "$PG_HBA"

sudo sed -i "s/^#listen_addresses.*/listen_addresses = '192.168.56.11'/" "$PG_CONF"

sudo systemctl restart postgresql
echo "PostgreSQL перезапущен. Проверьте: sudo -u postgres psql -c '\\du' и '\\l'"
