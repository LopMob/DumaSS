# Схема данных

```mermaid
erDiagram
    DEPUTY ||--o{ COMMISSION_MEMBERSHIP : "состоит в"
    COMMISSION ||--o{ COMMISSION_MEMBERSHIP : "включает"
    COMMISSION ||--o{ MEETING : "проводит"
    MEETING ||--o{ ATTENDANCE : "фиксирует"
    DEPUTY ||--o{ ATTENDANCE : "отмечается на"

    DEPUTY {
        int id PK
        string full_name
        string party
        string election_district
        bool is_active
        datetime created_at
    }

    COMMISSION {
        int id PK
        string name UK
        string description
        datetime created_at
    }

    COMMISSION_MEMBERSHIP {
        int id PK
        int commission_id FK
        int deputy_id FK
        bool is_chair
        date joined_at
    }

    MEETING {
        int id PK
        int commission_id FK "nullable — пленарное заседание"
        string title
        datetime scheduled_at
        string status "scheduled|held|cancelled"
        text agenda
    }

    ATTENDANCE {
        int id PK
        int meeting_id FK
        int deputy_id FK
        string status "present|absent|excused"
        string note
    }
```

## Ключевые ограничения
- `COMMISSION.name` — уникально.
- `COMMISSION_MEMBERSHIP` — уникальная пара `(commission_id, deputy_id)`.
- `ATTENDANCE` — уникальная пара `(meeting_id, deputy_id)`.
- Председатель (`is_chair = true`) — не более одного на комиссию
  (проверяется на уровне приложения, см. `app/crud.py::add_membership`).
- Внешние ключи — `ON DELETE CASCADE`: удаление депутата/комиссии удаляет
  зависимые членства, заседания и посещаемость.

## Управление схемой
Схема версионируется миграциями Alembic (`alembic/versions/`). Первая
миграция создаёт все пять таблиц. Применение: `make migrate`.
