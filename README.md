# Events Aggregator

Асинхронный сервис-агрегатор мероприятий на FastAPI и PostgreSQL.

Приложение получает данные о мероприятиях из внешнего Events Provider, сохраняет их в PostgreSQL и предоставляет REST API для просмотра мероприятий, регистрации и отмены билетов, получения доступных мест и запуска синхронизации.

## Стек

* Python 3.12+
* FastAPI
* SQLAlchemy 2.0
* PostgreSQL 16
* asyncpg
* httpx
* Pydantic Settings
* uvicorn
* pytest
* pytest-asyncio
* Ruff
* Docker
* uv

## Возможности

* получение списка мероприятий с пагинацией;
* фильтрация мероприятий по дате;
* получение информации о конкретном мероприятии;
* получение доступных мест;
* регистрация билетов на мероприятие;
* отмена регистрации билета;
* ручной запуск синхронизации;
* автоматическая фоновая синхронизация;
* инкрементальная синхронизация по дате изменения данных;
* обработка пагинации внешнего API;
* кэширование доступных мест на 30 секунд;
* повторная попытка синхронизации после ошибки.

## Архитектура

Проект разделён на несколько основных слоёв:

```text
src/events_aggregator/
├── api/             # HTTP endpoints
├── clients/         # работа с внешним Events Provider
├── core/            # конфигурация и подключение к БД
├── models/          # SQLAlchemy models
├── repositories/    # работа с данными в БД
├── schemas/         # Pydantic schemas
├── services.py      # синхронизация мероприятий
├── services_seats.py
├── services_tickets.py
├── worker.py        # фоновая синхронизация
└── main.py          # создание FastAPI приложения
```

## API

### Мероприятия

Получить список мероприятий:

```http
GET /api/events
```

Параметры:

* `date_from` — дата, начиная с которой получать мероприятия;
* `page` — номер страницы;
* `page_size` — размер страницы от 1 до 100.

Пример:

```text
GET /api/events?date_from=2026-09-01&page=1&page_size=20
```

Получить мероприятие:

```http
GET /api/events/{event_id}
```

### Доступные места

Получить доступные места мероприятия:

```http
GET /api/events/{event_id}/seats
```

Результат кэшируется на 30 секунд.

### Билеты

Зарегистрировать билет:

```http
POST /api/tickets
```

Пример тела запроса:

```json
{
  "event_id": "00000000-0000-0000-0000-000000000000",
  "first_name": "Ivan",
  "last_name": "Ivanov",
  "email": "ivan@example.com",
  "seat": "A1"
}
```

Отменить регистрацию:

```http
DELETE /api/tickets/{ticket_id}
```

### Синхронизация

Запустить синхронизацию:

```http
POST /api/sync
```

Также доступен endpoint:

```http
POST /api/sync/trigger
```

Можно передать дату для синхронизации:

```text
POST /api/sync?date_from=2026-09-01
```

Ответ:

```json
{
  "synced": 10
}
```

## Синхронизация данных

При запуске приложения создаётся фоновая задача синхронизации.

Синхронизация:

* выполняется автоматически каждые 24 часа;
* использует пагинацию внешнего API;
* сохраняет дату последнего успешного изменения данных;
* при последующих запусках использует инкрементальную синхронизацию;
* при ошибке повторяет попытку через 60 секунд.

Для хранения состояния синхронизации используется таблица `sync_metadata`.

## Переменные окружения

Создайте файл `.env` в корне проекта.

Основные настройки:

```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/events_aggregator
EVENTS_PROVIDER_URL=https://events-provider.dev-2.python-labs.ru
EVENTS_PROVIDER_API_KEY=your_api_key
```

API key не должен добавляться в Git.

## Запуск локально

### Через uv

Установите зависимости:

```bash
uv sync
```

Запустите PostgreSQL:

```bash
docker compose up -d db
```

Запустите приложение:

```bash
uv run uvicorn events_aggregator.main:app --reload
```

После запуска API будет доступно по адресу:

```text
http://localhost:8000
```

Документация Swagger:

```text
http://localhost:8000/docs
```

## Docker

Собрать образ:

```bash
docker build -t events-aggregator .
```

Запустить PostgreSQL:

```bash
docker compose up -d db
```

## Тесты

Запустить тесты:

```bash
uv run pytest
```

Проверить код Ruff:

```bash
uv run ruff check .
```

Проверить форматирование:

```bash
uv run ruff format --check .
```

## CI/CD

GitHub Actions автоматически выполняет:

1. проверку Ruff;
2. проверку форматирования;
3. запуск тестов;
4. сборку Docker image;
5. деплой приложения.

## Статус проекта

Проект разработан как асинхронное REST API с использованием FastAPI, PostgreSQL и SQLAlchemy.

Текущая версия успешно проходит автоматические проверки проекта.
