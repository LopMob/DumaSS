# Разбор проекта «Городская Дума» для защиты

Три раздела: (1) что делает каждый коммит, (2) что делает каждый файл,
по возможности построчно, (3) как запустить и что должно появиться.

---

# ЧАСТЬ 1. Коммиты — что и зачем в каждом

Смотреть командой: `git log --oneline --graph --all`

```
*   11ddea2 merge: feature/meetings-status-filter into main (PR #1)
|\
| * d204e41 docs(api): document status query parameter for GET /meetings
| * 6cda96f test(meetings): cover status filter and invalid status value
| * 0f5f1bb feat(meetings): add status filter to GET /meetings
* | 6a33057 docs(api): clarify meetings listing wording and note default sort order
|/
* 3d53080 docs: add task description for meetings status filter (issue #1)
* 21db64d docs: TZ, API description, data model, contribution rules
* 5deefef chore: alembic migrations, Makefile commands, Docker scaffolding
* 1fe49be test: cover CRUD, validation errors and business rules
* f459f20 feat(api): CRUD endpoints and business rules (single chair, quorum)
* ddac424 feat(domain): entities deputies, commissions, memberships, meetings, attendance
* 5e7eb27 chore: project scaffolding, env config and DB session setup
```

Читать снизу вверх — это порядок, в котором коммиты реально создавались.

### 1. `5e7eb27` — chore: project scaffolding, env config and DB session setup
**Файлы:** `.gitignore`, `.env.example`, `requirements.txt`, `pyproject.toml`, `app/config.py`, `app/database.py`, `app/__init__.py`
**Смысл:** самый первый коммит — "скелет" без единой сущности и без единого эндпоинта. Настроено то, от чего зависит вообще всё остальное: как читать `.env`, как подключаться к БД, какие библиотеки нужны, что не пускать в Git.
**Почему отдельным коммитом:** если что-то не так с конфигурацией — сразу видно, в каком коммите искать, не перерывая логику бизнес-правил.

### 2. `ddac424` — feat(domain): entities deputies, commissions, memberships, meetings, attendance
**Файлы:** `app/models.py`, `app/schemas.py`
**Смысл:** описаны 5 таблиц БД (ORM-модели) и Pydantic-схемы для валидации HTTP-запросов/ответов. Ещё нет ни одного эндпоинта — просто "форма" данных.
**Почему отдельно:** модель данных — это фундамент, её проще всего проверять/показывать отдельно от логики поверх неё.

### 3. `f459f20` — feat(api): CRUD endpoints and business rules (single chair, quorum)
**Файлы:** `app/crud.py`, `app/routers/*.py`, `app/main.py`
**Смысл:** вот тут появляется реально работающее приложение — вся бизнес-логика (`crud.py`), HTTP-обёртка (`routers/`), сборка приложения и обработка ошибок (`main.py`). Именно в этом коммите реализованы оба содержательных правила: один председатель на комиссию и правило кворума.
**Это — самый важный коммит для защиты**, если спросят "где твоё бизнес-правило" — ответ: здесь, в `crud.py`.

### 4. `1fe49be` — test: cover CRUD, validation errors and business rules
**Файлы:** `tests/*.py` (кроме `test_meetings_filter.py` — он появится позже)
**Смысл:** автотесты на всё, что было в предыдущих двух коммитах. Тесты сделаны **после** кода намеренно разделены отдельным коммитом — это не значит "тесты не важны", это значит "тесты — самостоятельная проверяемая единица работы".

### 5. `5deefef` — chore: alembic migrations, Makefile commands, Docker scaffolding
**Файлы:** `alembic.ini`, `alembic/`, `Makefile`, `Dockerfile`, `docker-compose.yml`
**Смысл:** инфраструктурный слой — как разворачивать БД (миграции), как единообразно запускать команды (`make ...`), заготовка на будущее для контейнеров (используется не в этой лабораторной, а в следующих).

### 6. `21db64d` — docs: TZ, API description, data model, contribution rules
**Файлы:** `README.md`, `CONTRIBUTING.md`, `docs/TZ.md`, `docs/API.md`, `docs/DATA_MODEL.md`
**Смысл:** вся обязательная по заданию документация. Идёт последним коммитом в базовой истории, потому что документирует уже готовый к этому моменту код — писать доки на несуществующий код бессмысленно.

**Коммиты 1–6 — это "база", `v0.1.0`-кандидат до демонстрации фичи.**

### 7. `3d53080` — docs: add task description for meetings status filter (issue #1)
**Файл:** `docs/tasks/ISSUE-1.md`
**Смысл:** это имитация завести задачу (issue) в трекере — описание, что нужно сделать и критерии приёмки, **до** того как писать код. Прямо после этого коммита была создана ветка `feature/meetings-status-filter`.

### 8. `0f5f1bb` — feat(meetings): add status filter to GET /meetings *(в ветке)*
**Файлы:** `app/crud.py`, `app/routers/meetings.py`
**Смысл:** сама реализация задачи №1 — в `GET /meetings` добавлен необязательный параметр `?status=`.

### 9. `6cda96f` — test(meetings): cover status filter and invalid status value *(в ветке)*
**Файлы:** `tests/test_meetings_filter.py`, `tests/test_deputies.py`
**Смысл:** тест на новую функцию — отдельным коммитом от самой реализации.

### 10. `d204e41` — docs(api): document status query parameter for GET /meetings *(в ветке)*
**Файл:** `docs/API.md`
**Смысл:** обновление документации API под новую функцию — тоже отдельный коммит.

### 11. `6a33057` — docs(api): clarify meetings listing wording and note default sort order *(в main, параллельно)*
**Файл:** `docs/API.md`
**Смысл:** это **имитация параллельной работы коллеги** — пока вы (в ветке) добавляли `status`, "кто-то ещё" (в моём случае — я, для демонстрации) поменял ту же строку в `main`. В реальной команде это происходит само собой, когда два человека одновременно правят один файл.

### 12. `11ddea2` — merge: feature/meetings-status-filter into main (PR #1)
**Смысл:** попытка слияния ветки в `main` натолкнулась на конфликт — обе стороны поменяли одну и ту же строку в `docs/API.md`. Конфликт был разрешён **вручную и осознанно** — не "принять чью-то сторону", а объединить смысл обеих правок в одну строку. Это единственный коммит с двумя родителями (отсюда `|\` на графе).

### Тег `v0.1.0`
Стоит на коммите `11ddea2` — то есть версия зафиксирована **после** того, как функция прошла полный путь: задача → ветка → коммиты → конфликт → разрешение → слияние.

---

# ЧАСТЬ 2. Файлы проекта — построчный разбор

## `.gitignore`
```
.env                  # реальные секреты — никогда не в Git
*.db, *.sqlite3        # локальные файлы БД — у каждого свои данные
backups/               # резервные копии — тоже локальные
__pycache__/, .venv/   # то, что генерируется автоматически, не пишется руками
.pytest_cache/, .ruff_cache/  # кэши инструментов
.idea/, .vscode/       # настройки конкретной IDE конкретного человека
```
**Идея:** в Git должно попадать только то, что нужно **всем** разработчикам одинаково. Всё, что у каждого своё или генерируется — сюда.

## `.env.example`
Шаблон переменных окружения. Каждая строка — `ИМЯ=значение_по_умолчанию`:
- `APP_HOST`, `APP_PORT` — где слушает сервер.
- `DATABASE_URL=sqlite:///./duma.db` — строка подключения к БД; если поменять на `postgresql+psycopg2://...`, код не меняется вообще.
- `POSTGRES_*` — понадобятся, когда в следующей ЛР появится контейнер с PostgreSQL.

## `requirements.txt`
Каждая строка — одна зависимость с зафиксированной версией (`==`), чтобы у всех членов команды и на сервере ставилась ровно та же версия библиотеки, без сюрпризов от новых версий.
- `fastapi`, `uvicorn` — сам веб-фреймворк и сервер, который его запускает.
- `SQLAlchemy` — ORM (работа с БД через Python-объекты вместо голого SQL).
- `alembic` — миграции схемы БД.
- `pydantic`, `pydantic-settings` — валидация данных и чтение `.env`.
- `psycopg2-binary` — драйвер для PostgreSQL (для будущих лаб).
- `pytest`, `httpx`, `ruff`, `black` — тесты и проверка качества кода.

## `pyproject.toml`
Конфигурация инструментов проверки качества:
- `[tool.ruff]` — статический анализатор (ищет неиспользуемые импорты, опечатки, плохие паттерны). `line-length = 100` — максимальная длина строки.
- `[tool.ruff.lint] ignore = ["B008"]` — единственное исключение: правило B008 ругается на `Depends(...)` в аргументах функции, а это официальный рекомендованный паттерн FastAPI, а не ошибка.
- `[tool.black]` — автоформатирование кода (отступы, кавычки и т.д.) в одном стиле для всех.
- `[tool.pytest.ini_options]` — где искать тесты.

## `Makefile`
Каждая цель — это команда, которую можно набрать одним словом. Разбор по строкам:
```makefile
setup:      создаёт venv → ставит зависимости → копирует .env.example в .env
run:        запускает сервер (uvicorn) с автоперезагрузкой при изменении кода
test:       pytest -v — прогоняет все автотесты
quality:    ruff check + black --check — проверка стиля и ошибок, БЕЗ изменения файлов
migrate:    alembic upgrade head — накатывает все ещё не применённые миграции БД
backup:     копирует текущий duma.db в backups/ с меткой времени в имени
restore:    находит самую свежую резервную копию и возвращает её на место
verify:     quality + test одной командой — то, что ОБЯЗАТЕЛЬНО перед PR
up/down:    docker compose up/down — заготовка под контейнеры (не используется в ЛР1)
```

## `Dockerfile`
Инструкция сборки образа приложения (нужна начиная со следующей ЛР, не сейчас):
- `FROM python:3.12-slim` — базовый минимальный образ с Python.
- `COPY requirements.txt . / RUN pip install ...` — сначала зависимости отдельным слоем (Docker кэширует этот шаг, если requirements не менялся — пересборка быстрее).
- `COPY app ./app` и т.д. — копируем код приложения внутрь образа.
- `CMD [...]` — команда, которая выполнится при старте контейнера.

## `docker-compose.yml`
Описание **двух** сервисов, которые должны работать вместе (тоже заготовка на будущее):
- `app` — наш FastAPI-сервис, собирается из `Dockerfile`, порт `8000` пробрасывается наружу.
- `db` — готовый образ PostgreSQL с переменными для логина/пароля/имени базы из `.env`.
- `depends_on` — гарантирует, что `db` запустится раньше, чем `app` попытается к ней подключиться.

## `app/__init__.py` и `app/routers/__init__.py`
Пустые файлы. Их единственная задача — сказать Python "это не просто папка, а пакет", чтобы работал импорт вида `from app import crud`.

## `app/config.py`
```python
class Settings(BaseSettings):
    app_name: str = "Городская Дума API"     # значение по умолчанию,
    app_host: str = "0.0.0.0"                # переопределяется переменной
    app_port: int = 8000                     # окружения с тем же именем
    database_url: str = "sqlite:///./duma.db"
    environment: str = "development"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

@lru_cache
def get_settings() -> Settings:
    return Settings()
```
`BaseSettings` из `pydantic-settings` сам читает `.env` и переменные окружения ОС и подставляет их в поля класса. `@lru_cache` — чтобы объект настроек создавался один раз за всё время работы сервера, а не при каждом запросе.

## `app/database.py`
```python
connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
```
Специфика SQLite: по умолчанию он запрещает работу с одним соединением из разных потоков, а FastAPI как раз обрабатывает запросы в разных потоках — эта строка снимает запрет (для PostgreSQL строка не нужна, поэтому условие).
```python
engine = create_engine(...)          # "движок" — знает, как физически говорить с БД
SessionLocal = sessionmaker(...)     # фабрика сессий — одна сессия = одна транзакция
class Base(DeclarativeBase): pass    # базовый класс, от которого наследуются все модели
def get_db():
    db = SessionLocal()
    try:
        yield db                     # отдаём сессию эндпоинту
    finally:
        db.close()                   # и ГАРАНТИРОВАННО закрываем после, даже при ошибке
```

## `app/models.py`
Разбор по классам (каждый класс = таблица):
```python
class MeetingStatus(str, enum.Enum):
    scheduled = "scheduled"
    held = "held"
    cancelled = "cancelled"
```
Перечисление — статус заседания может быть только одним из этих трёх значений, БД сама это проверит.

```python
class Deputy(Base):
    __tablename__ = "deputies"
    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    ...
    memberships: Mapped[list["CommissionMembership"]] = relationship(...)
```
`mapped_column` — реальная колонка в таблице. `relationship` — не колонка, а удобный способ на Python-стороне получить связанные записи (`deputy.memberships` вернёт список членств этого депутата), сама связь физически задаётся внешним ключом в `CommissionMembership`.

```python
class CommissionMembership(Base):
    __table_args__ = (UniqueConstraint("commission_id", "deputy_id", name="uq_membership_pair"),)
    is_chair: Mapped[bool] = mapped_column(Boolean, default=False)
```
`UniqueConstraint` — база данных сама не даст добавить одного депутата в одну комиссию дважды (это защита на уровне БД, а не только в коде). `is_chair` — не отдельная таблица "председатели", а флаг в этой же таблице членства (обоснование: председатель — это роль депутата в конкретной комиссии, а не отдельная сущность).

```python
class Meeting(Base):
    commission_id: Mapped[int | None] = mapped_column(ForeignKey(...), nullable=True)
```
`nullable=True` — заседание **может** не принадлежать ни одной комиссии (пленарное заседание думы целиком).

```python
class Attendance(Base):
    __table_args__ = (UniqueConstraint("meeting_id", "deputy_id", name="uq_attendance_pair"),)
```
Аналогично — один депутат не может быть отмечен дважды на одном заседании.

## `app/schemas.py`
Каждый класс — это "форма" данных для конкретного HTTP-запроса или ответа, отдельно от ORM-модели:
```python
class DeputyCreate(BaseModel):
    full_name: str = Field(min_length=2, max_length=255)
```
Это то, что клиент **обязан** прислать при создании депутата. `min_length=2` — если пришло имя из 1 символа, FastAPI сам вернёт `422` ещё до того, как код вашего эндпоинта вообще запустится.
```python
class DeputyOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
```
`DeputyOut` — что мы **отдаём** клиенту в ответ. `from_attributes=True` разрешает строить эту схему прямо из ORM-объекта (`Deputy` из `models.py`), а не только из словаря.

Разделение `Create`/`Update`/`Out` — намеренное: например, в ответе (`Out`) никогда не будет случайно "утечки" поля, которого нет в схеме, даже если в модели БД оно есть.

## `app/crud.py` — самый важный файл, разбор ключевых мест

```python
class DomainError(Exception): pass
class NotFoundError(Exception): pass
class ConflictError(DomainError): pass
class QuorumError(DomainError): pass
```
Свои классы ошибок вместо `HTTPException` прямо здесь — специально, чтобы этот файл **не знал**, что такое HTTP вообще. Он мог бы использоваться и в консольной команде, и в другом интерфейсе — не только в вебе. Кто ловит эти ошибки и превращает в HTTP-коды — смотри `main.py`.

```python
def add_membership(db, commission_id, data):
    ...
    if data.is_chair:
        existing_chair = db.scalar(
            select(models.CommissionMembership).where(
                models.CommissionMembership.commission_id == commission.id,
                models.CommissionMembership.is_chair.is_(True),
            )
        )
        if existing_chair is not None:
            raise ConflictError("У комиссии уже есть действующий председатель ...")
```
**Правило №1 (один председатель).** Перед тем как добавить нового председателя — ищем в БД, нет ли уже действующего. Если есть — не добавляем, а бросаем понятную ошибку.

```python
def _ensure_quorum(db, meeting):
    if meeting.commission_id is None:
        return                                      # пленарные заседания не проверяем
    total_members = len(list(db.scalars(...)))        # сколько всего членов в комиссии
    present_count = len(list(db.scalars(...)))         # сколько отмечено "present"
    required = total_members // 2 + 1                  # больше половины
    if present_count < required:
        raise QuorumError(f"Нет кворума: присутствует {present_count} из {total_members} ...")
```
**Правило №2 (кворум).** `total_members // 2 + 1` — целочисленное деление, поэтому для 4 членов нужно 3 (не 2, не 2.5), для 5 — тоже 3. Вызывается из `set_meeting_status` только когда новый статус — `held`.

```python
def deputy_attendance_stats(db, deputy_id):
    ...
    return {
        "attendance_rate": round(present / total, 2) if total else None,
    }
```
`if total else None` — защита от деления на ноль: если у депутата вообще нет ни одной записи посещаемости, вместо ошибки вернём `None`, а не упадём.

## `app/routers/deputies.py`, `commissions.py`, `meetings.py`
Во всех трёх файлах один и тот же паттерн — эндпоинт **не содержит логики**, он просто:
```python
@router.post("", response_model=schemas.DeputyOut, status_code=201)
def create_deputy(data: schemas.DeputyCreate, db: Session = Depends(get_db)):
    return crud.create_deputy(db, data)
```
1. Объявляет HTTP-метод и путь (`@router.post("")`).
2. Говорит FastAPI, какую схему ждать на входе (`data: schemas.DeputyCreate`) — если формат не совпадёт, `422` вернётся автоматически.
3. Говорит, какую схему вернуть (`response_model=...`) — FastAPI сам проверит и отфильтрует поля ответа.
4. `Depends(get_db)` — получить сессию БД (см. `database.py`) на время этого одного запроса.
5. Вызывает соответствующую функцию из `crud.py` — вот и вся "логика" эндпоинта.

В `meetings.py` — единственное более сложное место:
```python
@router.patch("/{meeting_id}/status", response_model=schemas.MeetingOut)
def set_meeting_status(meeting_id: int, data: schemas.MeetingStatusUpdate, db=Depends(get_db)):
    return crud.set_meeting_status(db, meeting_id, data.status)
```
Именно этот эндпоинт при переводе в `held` внутри `crud.py` вызывает проверку кворума.

## `app/main.py`
```python
Base.metadata.create_all(bind=engine)
```
В ЛР1 таблицы создаются автоматически при старте сервера — это допустимо для минимального приложения; в следующих ЛР это заменится на обязательное `make migrate` (Alembic), потому что "просто пересоздать таблицы" на боевых данных недопустимо (данные потеряются).

```python
@app.exception_handler(crud.ConflictError)
def conflict_handler(request, exc):
    return JSONResponse(status_code=409, content={"detail": str(exc)})
```
Вот здесь и происходит превращение "внутренней" ошибки Python (`ConflictError` из `crud.py`) в правильный HTTP-код и JSON-тело ответа. По одному обработчику на каждый тип ошибки.

```python
@app.get("/health")
def health():
    try:
        with engine.connect():
            db_ok = True
    except Exception:
        db_ok = False
    return {"status": "ok" if db_ok else "degraded", ...}
```
Реальная попытка подключиться к БД, а не просто "сервер жив" — если БД недоступна, `/health` честно скажет `degraded`.

## `alembic.ini`, `alembic/env.py`, `alembic/script.py.mako`
- `alembic.ini` — где искать миграции (`script_location = alembic`), базовая строка подключения (реально переопределяется из `.env` в `env.py`).
- `alembic/env.py` — связывает Alembic с нашими моделями (`from app import models`), чтобы `alembic revision --autogenerate` мог сам увидеть все таблицы и сравнить их с текущим состоянием БД.
- `script.py.mako` — шаблон, по которому генерируется каждый новый файл миграции (не нужно трогать руками).
- `alembic/versions/a5064c40c64f_....py` — сама первая миграция: функции `upgrade()` (создать 5 таблиц) и `downgrade()` (откатить — удалить их).

## `tests/conftest.py`
```python
os.environ["DATABASE_URL"] = "sqlite:///./test_duma.db"
```
Тесты используют **отдельный** файл БД, не тот, что для обычной работы — чтобы тесты никогда не повредили ваши реальные данные.
```python
@pytest.fixture(autouse=True)
def _clean_db():
    Base.metadata.drop_all(bind=engine)   # удалить всё
    Base.metadata.create_all(bind=engine) # создать заново, пусто
    yield
    Base.metadata.drop_all(bind=engine)
```
`autouse=True` — выполняется перед **каждым** тестом автоматически. Каждый тест начинается с чистой БД, поэтому тесты не влияют друг на друга.

## `tests/test_health.py`, `test_deputies.py`, `test_business_rules.py`, `test_meetings_filter.py`
Все построены одинаково: вызвать эндпоинт через `client.post/get/patch(...)`, проверить `assert resp.status_code == ...` и `assert resp.json()[...] == ...`. Самые важные для защиты — `test_business_rules.py`: там дословно проверяется и правило председателя, и правило кворума (можно на защите открыть и показать: "вот тест, который доказывает, что правило реально работает").

## `docs/TZ.md`, `API.md`, `DATA_MODEL.md`, `tasks/ISSUE-1.md`, `CONTRIBUTING.md`, `README.md`
Это обязательные по заданию текстовые документы (не код) — их не нужно разбирать построчно, важно уметь коротко пересказать содержание каждого (см. предыдущие мои ответы в этом чате — там уже разобрано, что в каждом).

---

# ЧАСТЬ 3. Как запустить и что должно появиться

```bash
cd duma-project
make setup
```
**Что появится:** новая папка `.venv/`, в терминале — установка пакетов (много строк `Installing collected packages...`), в конце — сообщение про активацию окружения. Появится файл `.env` (скопированный из `.env.example`).

```bash
make migrate
```
**Что появится:** несколько строк лога Alembic (`INFO [alembic...] Running upgrade ...`), в папке проекта появится файл `duma.db` — это и есть ваша база данных (пустая, но со всеми таблицами).

```bash
make run
```
**Что появится в терминале:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```
Терминал "зависнет" в этом состоянии — это нормально, сервер работает и ждёт запросов. Останавливается `Ctrl+C`.

**Откройте в браузере:** `http://localhost:8000/docs`
**Что появится:** страница Swagger UI — список всех эндпоинтов, сгруппированных по тегам ("Депутаты", "Комиссии", "Заседания", "Служебное"). Можно нажать на любой, нажать "Try it out", ввести данные и нажать "Execute" — увидите реальный ответ сервера.

**Проверка health в другом терминале (пока `make run` работает в первом):**
```bash
curl http://localhost:8000/health
```
**Что появится:**
```json
{"status":"ok","environment":"development","database":"ok"}
```

**Демонстрация бизнес-правила** (можно через `/docs` или через curl):
```bash
curl -X POST localhost:8000/commissions -H "Content-Type: application/json" -d '{"name":"Тестовая комиссия"}'
# ответ: {"id":1,"name":"Тестовая комиссия","description":null}

curl -X POST localhost:8000/deputies -H "Content-Type: application/json" -d '{"full_name":"Иванов Иван"}'
# ответ: {"id":1,...}
curl -X POST localhost:8000/deputies -H "Content-Type: application/json" -d '{"full_name":"Петров Пётр"}'
# ответ: {"id":2,...}

curl -X POST localhost:8000/commissions/1/members -H "Content-Type: application/json" -d '{"deputy_id":1,"is_chair":true}'
# ответ 201: депутат 1 назначен председателем

curl -X POST localhost:8000/commissions/1/members -H "Content-Type: application/json" -d '{"deputy_id":2,"is_chair":true}'
# ответ 409: {"detail":"У комиссии уже есть действующий председатель ..."}  ← вот оно, правило сработало
```

```bash
make test
```
**Что появится:**
```
======================== 10 passed in 0.4Xs ========================
```
Если увидите `passed`, а не `failed` — всё в порядке.

```bash
make quality
```
**Что появится при отсутствии проблем:**
```
All checks passed!
```
(от ruff) и никакого вывода от black (значит, форматирование в порядке).

```bash
make verify
```
Просто выполняет `quality` и `test` одной командой — это то, что нужно гонять перед каждым PR.
