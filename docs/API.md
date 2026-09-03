# API — «Городская Дума»

Полная интерактивная документация доступна после запуска приложения по
адресу `/docs` (Swagger UI) и `/openapi.json`. Ниже — сводка вручную.

Базовый URL (локально): `http://localhost:8000`

## Служебное
| Метод | Путь | Описание |
|---|---|---|
| GET | `/health` | Проверка работоспособности сервиса и подключения к БД |

## Депутаты
| Метод | Путь | Описание |
|---|---|---|
| POST | `/deputies` | Создать депутата |
| GET | `/deputies?active_only=false` | Список депутатов |
| GET | `/deputies/{id}` | Получить депутата |
| PATCH | `/deputies/{id}` | Частично обновить депутата |
| DELETE | `/deputies/{id}` | Удалить депутата (каскадно) |
| GET | `/deputies/{id}/attendance-stats` | Статистика посещаемости депутата |

## Комиссии и членство
| Метод | Путь | Описание |
|---|---|---|
| POST | `/commissions` | Создать комиссию |
| GET | `/commissions` | Список комиссий |
| GET | `/commissions/{id}` | Получить комиссию |
| POST | `/commissions/{id}/members` | Добавить депутата в комиссию (`is_chair` — назначить председателем) |
| GET | `/commissions/{id}/members` | Состав комиссии |

## Заседания и посещаемость
| Метод | Путь | Описание |
|---|---|---|
| POST | `/meetings` | Создать заседание |
| GET | `/meetings?commission_id=` | Список заседаний (опционально по комиссии) |
| GET | `/meetings/{id}` | Получить заседание |
| PATCH | `/meetings/{id}/status` | Сменить статус (`scheduled`\|`held`\|`cancelled`); перевод в `held` проверяет кворум |
| POST | `/meetings/{id}/attendance` | Отметить посещаемость депутата |
| GET | `/meetings/{id}/attendance` | Список отметок посещаемости по заседанию |

## Коды ошибок
- `404` — сущность не найдена.
- `409` — нарушение бизнес-правила (см. `docs/TZ.md`, раздел 4): второй
  председатель, повторное членство, повторная посещаемость, отсутствие
  кворума при закрытии заседания.
- `422` — некорректное тело запроса.

## Пример сценария (curl)
```bash
# Депутат
curl -X POST localhost:8000/deputies -H "Content-Type: application/json" \
  -d '{"full_name": "Иванов Иван Иванович"}'

# Комиссия
curl -X POST localhost:8000/commissions -H "Content-Type: application/json" \
  -d '{"name": "Бюджетная комиссия"}'

# Включить депутата в комиссию председателем
curl -X POST localhost:8000/commissions/1/members -H "Content-Type: application/json" \
  -d '{"deputy_id": 1, "is_chair": true}'

# Создать заседание
curl -X POST localhost:8000/meetings -H "Content-Type: application/json" \
  -d '{"commission_id": 1, "title": "Заседание №1", "scheduled_at": "2026-09-10T10:00:00"}'

# Отметить присутствие
curl -X POST localhost:8000/meetings/1/attendance -H "Content-Type: application/json" \
  -d '{"deputy_id": 1, "status": "present"}'

# Закрыть заседание (проверка кворума)
curl -X PATCH localhost:8000/meetings/1/status -H "Content-Type: application/json" \
  -d '{"status": "held"}'
```
