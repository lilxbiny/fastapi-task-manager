# Task Management API

RESTful API для управления задачами пользователей на FastAPI + PostgreSQL с JWT-аутентификацией.

## Технологический стек

- Python 3.11+, FastAPI, SQLAlchemy 2.0, Alembic
- PostgreSQL 16
- JWT (python-jose) + bcrypt (passlib)
- Pydantic v2
- Docker / Docker Compose
- pytest + httpx

## Структура проекта

```
fastapi-task-manager/
├── app/
│   ├── main.py            # точка входа FastAPI
│   ├── config.py          # настройки из переменных окружения
│   ├── database.py        # SQLAlchemy engine/session
│   ├── models/             # ORM-модели (User, Task)
│   ├── schemas/            # Pydantic-схемы
│   ├── api/                 # роутеры (auth, tasks)
│   ├── core/                # security (JWT, хеширование), GUID-тип
│   └── services/            # бизнес-логика
├── alembic/                 # миграции БД
├── tests/                   # pytest-тесты (auth, tasks)
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
└── README.md
```

## Быстрый запуск (Docker)

1. Скопируйте файл окружения и при желании отредактируйте значения:

   ```bash
   cp .env.example .env
   ```

2. Поднимите проект одной командой:

   ```bash
   docker-compose up --build
   ```

   API дождётся готовности PostgreSQL (retry-логика в `app/main.py`) и создаст таблицы автоматически при первом запуске.

3. API будет доступен на `http://localhost:8000`, интерактивная документация — на `http://localhost:8000/docs`.

Для остановки: `docker-compose down` (данные PostgreSQL сохраняются в volume `postgres_data`; чтобы стереть их — `docker-compose down -v`).

## Применение миграций Alembic (опционально)

В `app/main.py` для удобства разработки таблицы создаются автоматически через `Base.metadata.create_all()`. Для продакшн-развёртывания рекомендуется использовать явные миграции:

```bash
docker-compose exec api alembic upgrade head
```

Создать новую миграцию после изменения моделей:

```bash
docker-compose exec api alembic revision --autogenerate -m "описание изменений"
```

## Локальный запуск без Docker

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env             # укажите локальный DATABASE_URL, если PostgreSQL не в докере
uvicorn app.main:app --reload
```

## Тесты

Тесты используют in-memory SQLite и не требуют поднятой PostgreSQL:

```bash
pip install -r requirements.txt
pytest -v
```

Покрытие:
- регистрация пользователя (включая дубликат email)
- логин (успешный и с неверным паролем)
- создание задачи
- получение списка задач (пагинация, фильтр по статусу)
- полное (`PUT`) и частичное (`PATCH`) обновление задачи
- удаление задачи
- попытка доступа к чужой задаче → `404`
- доступ к `/tasks` без токена → `401`

## Примеры запросов

### Регистрация

```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "supersecret1"}'
```

### Логин (OAuth2 Password Flow → JWT)

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@example.com&password=supersecret1"
```

Ответ:

```json
{ "access_token": "eyJhbGciOi...", "token_type": "bearer" }
```

Сохраните токен в переменную для удобства:

```bash
export TOKEN="eyJhbGciOi..."
```

### Создание задачи

```bash
curl -X POST http://localhost:8000/tasks/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Написать API", "description": "Реализовать CRUD", "status": "todo", "priority": "high"}'
```

### Список задач (пагинация + фильтр)

```bash
curl "http://localhost:8000/tasks/?skip=0&limit=10&status=todo" \
  -H "Authorization: Bearer $TOKEN"
```

### Получить задачу по ID

```bash
curl http://localhost:8000/tasks/<task_id> \
  -H "Authorization: Bearer $TOKEN"
```

### Полное обновление (PUT)

```bash
curl -X PUT http://localhost:8000/tasks/<task_id> \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Новое название", "description": null, "status": "in_progress", "priority": "medium"}'
```

### Частичное обновление (PATCH)

```bash
curl -X PATCH http://localhost:8000/tasks/<task_id> \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status": "done"}'
```

### Удаление задачи

```bash
curl -X DELETE http://localhost:8000/tasks/<task_id> \
  -H "Authorization: Bearer $TOKEN"
```

## Безопасность

- Все эндпоинты `/tasks/*` защищены Bearer-токеном (OAuth2 Password Flow + JWT).
- Пароли хранятся только в виде bcrypt-хеша.
- При обращении к задаче по ID всегда проверяется `task.owner_id == current_user.id`; чужая задача возвращает `404` (чтобы не раскрывать факт её существования).
- Секретный ключ и параметры БД читаются из переменных окружения (`.env`), файл `.env` не должен попадать в репозиторий (см. `.gitignore`).
- Время жизни access-токена — 30 минут по умолчанию, настраивается через `ACCESS_TOKEN_EXPIRE_MINUTES`.

## Дальнейшие возможные улучшения (вне текущего scope)

- Refresh-токены
- Роли пользователей (admin / user)
- Прикрепление файлов к задачам
- Уведомления
- Полнотекстовый поиск
- Rate limiting
