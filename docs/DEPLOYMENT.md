# Развёртывание в Linux-среде (ЛР2)

Две виртуальные машины в VirtualBox (Ubuntu Server), без контейнеров:
`app-server` (192.168.56.11) — приложение, `db-server` (192.168.56.10) — PostgreSQL.

## 1–2. Машины, сеть, статическая адресация, SSH по ключам

На каждой VM — два сетевых адаптера: **NAT** (интернет для установки пакетов)
и **Host-only** (`vboxnet0`, `192.168.56.0/24`) — для связи машин друг с другом
и с хостом. Статический IP — см. [`netplan-example.yaml`](netplan-example.yaml),
применяется командой `sudo netplan apply` на самой VM.

**SSH-ключ** генерируется **на хосте** (не на VM):
```bash
ssh-keygen -t ed25519 -C "admin@duma-lab"
ssh-copy-id admin@192.168.56.11
ssh-copy-id admin@192.168.56.10
```
После этого проверьте вход без пароля: `ssh admin@192.168.56.11`.

## 3. Запрет root по SSH, отдельные пользователи

На **обеих** машинах, в `/etc/ssh/sshd_config`:
```
PermitRootLogin no
PasswordAuthentication no
```
Затем `sudo systemctl restart ssh`.

Пользователи:
- **`admin`** — обычный пользователь с `sudo`, вход по SSH-ключу, для администрирования.
- **`duma`** — системный пользователь **без** `sudo` и **без** интерактивного входа
  (`--shell /usr/sbin/nologin`), от его имени работает только systemd-служба.
  Создаётся автоматически скриптом [`setup_app_server.sh`](setup_app_server.sh).

## 4. Права на файлы и каталоги

| Путь | Владелец | Права | Почему |
|---|---|---|---|
| `/opt/duma-project` | `duma:duma` | `750` | Код читает/пишет только `duma`, остальные — нет доступа |
| `/etc/duma/duma.env` | `duma:duma` | `600` | Секреты видит только владелец, даже другие локальные пользователи — нет |

Выставляются автоматически в [`setup_app_server.sh`](setup_app_server.sh).

## 5–6. Среда выполнения и БД

**app-server**: `python3`, `venv`, зависимости из `requirements.txt` —
см. [`setup_app_server.sh`](setup_app_server.sh).

**db-server**: PostgreSQL, роль `duma_app` **без** прав суперпользователя,
создания БД или ролей (`NOSUPERUSER NOCREATEDB NOCREATEROLE`), владеет **только**
своей базой `duma` — см. [`setup_db_server.sh`](setup_db_server.sh).

## 7. Развёртывание приложения без контейнеров

```bash
sudo bash setup_app_server.sh      # клонирует репозиторий, venv, зависимости
# отредактировать /etc/duma/duma.env — указать реальный DATABASE_URL на db-server
sudo bash install_service.sh       # миграции + установка и запуск systemd-службы
```

## 8–9. systemd-служба: запуск/остановка/автостарт/автоперезапуск

Unit-файл — [`duma.service`](duma.service). Ключевые строки:
```ini
Restart=on-failure
RestartSec=5
[Install]
WantedBy=multi-user.target
```
`WantedBy=multi-user.target` + `systemctl enable duma` — автостарт при загрузке
системы. `Restart=on-failure` — автоматический перезапуск, если процесс упал
(не при штатной остановке через `systemctl stop`).

Управление:
```bash
sudo systemctl start duma
sudo systemctl stop duma
sudo systemctl restart duma
sudo systemctl status duma
sudo systemctl enable duma    # автостарт
sudo systemctl disable duma
```

## 10. Firewall

`app-server`: [`firewall_app_server.sh`](firewall_app_server.sh) — открыт `22`
(только из локальной подсети) и `8000` (клиентам).
`db-server`: [`firewall_db_server.sh`](firewall_db_server.sh) — открыт `22`
(только из подсети) и `5432` **только** с IP `app-server`, больше ни для кого.

Дополнительно на уровне самого PostgreSQL — `pg_hba.conf` разрешает подключение
к базе `duma` только с IP app-server (см. `setup_db_server.sh`), то есть защита
не только на firewall, но и в самой СУБД — два независимых рубежа.

## 11. Настройки отдельно от кода

Код — в `/opt/duma-project` (из Git). Настройки — в `/etc/duma/duma.env`,
**вне** репозитория, подключаются к службе через `EnvironmentFile=` в
`duma.service`. В Git попадает только шаблон
[`duma.env.production.example`](duma.env.production.example) без реальных
значений — та же логика, что и `.env.example` в корне проекта из ЛР1.

## 12. Скрипты повторяемого развёртывания

Всё, что выше — исполняемые скрипты в этой папке, не только описание:
`setup_app_server.sh` → `setup_db_server.sh` → `install_service.sh` →
`firewall_app_server.sh` / `firewall_db_server.sh`.

## 13. Требования безопасности — как проверить, что они выполнены

| Требование | Проверка |
|---|---|
| Приложение не от root | `systemctl show duma -p User` → должно быть `duma` |
| Лишние порты не открыты | `sudo ufw status` на обеих машинах — только 22 и (8000 или 5432) |
| Пароли не в репозитории | `git log -p -- deploy/ \| grep -i password` — не должно найти реальных значений; `.env`/`duma.env` — в `.gitignore` |

## Проверка на защите — что показать и какими командами

- **Перезагрузка + автозапуск**: `sudo reboot`, после — `systemctl status duma` (`active (running)`), `curl http://192.168.56.11:8000/health` с хоста.
- **Остановка БД, диагностика приложения**: на db-server `sudo systemctl stop postgresql`; на app-server `curl .../health` → `"database":"unavailable"`; `journalctl -u duma -n 50`.
- **Поиск процесса/порта/журналов**: `systemctl status duma`, `sudo ss -tlnp | grep 8000`, `journalctl -u duma -f`.
- **Изменение параметра и восстановление**: например, поменять `RestartSec` в `duma.service`, `sudo systemctl daemon-reload && systemctl restart duma`, показать эффект, затем вернуть исходное значение тем же путём.
- **Недоступность БД снаружи**: с хост-машины (не app-server) `telnet 192.168.56.10 5432` или `nc -zv 192.168.56.10 5432` — должно быть отказано/таймаут.
