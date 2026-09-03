.PHONY: setup run test quality migrate backup restore verify up down container-check

VENV := .venv
PY := $(VENV)/bin/python
PIP := $(VENV)/bin/pip

setup: ## Первоначальная настройка: venv, зависимости, .env
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	[ -f .env ] || cp .env.example .env
	@echo "Готово. Активируйте окружение: source $(VENV)/bin/activate"

run: ## Локальный запуск приложения
	$(PY) -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test: ## Автоматические тесты
	$(PY) -m pytest -v

quality: ## Форматирование и статический анализ (ruff + black --check)
	$(PY) -m ruff check .
	$(PY) -m black --check .

migrate: ## Применение миграций Alembic
	$(PY) -m alembic upgrade head

backup: ## Резервная копия локальной БД (SQLite, ЛР1)
	mkdir -p backups
	@if [ -f duma.db ]; then \
		cp duma.db backups/duma_$$(date +%Y%m%d_%H%M%S).db && \
		echo "Резервная копия создана в backups/"; \
	else \
		echo "Файл duma.db не найден — нечего резервировать"; \
	fi

restore: ## Восстановление БД из последней резервной копии
	@LATEST=$$(ls -t backups/*.db 2>/dev/null | head -n1); \
	if [ -z "$$LATEST" ]; then \
		echo "Резервные копии не найдены"; exit 1; \
	else \
		cp $$LATEST duma.db && echo "Восстановлено из $$LATEST"; \
	fi

verify: quality test ## Полный набор локальных проверок (обязателен перед PR)
	@echo "Все локальные проверки пройдены."

up: ## Запуск контейнерного окружения (появится в следующих ЛР)
	docker compose up -d --build

down: ## Остановка контейнерного окружения
	docker compose down

container-check: ## Проверка состояния контейнеров/образа (появится в следующих ЛР)
	docker compose ps
