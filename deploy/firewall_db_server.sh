#!/usr/bin/env bash
# Выполняется НА db-server.
set -euo pipefail

ADMIN_SUBNET="192.168.56.0/24"
APP_SERVER_IP="192.168.56.10"    # только этому IP разрешено ходить на 5432

sudo ufw default deny incoming
sudo ufw default allow outgoing

sudo ufw allow from "$ADMIN_SUBNET" to any port 22 proto tcp comment 'SSH только из локальной сети'
sudo ufw allow from "$APP_SERVER_IP" to any port 5432 proto tcp comment 'PostgreSQL только с app-server'

sudo ufw --force enable
sudo ufw status verbose
