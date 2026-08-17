Markdown

# Task Management API

A robust, scalable RESTful API for managing user tasks built with FastAPI, PostgreSQL, and JWT Authentication.

---

## Tech Stack

* **Language:** Python 3.11+
* **Framework:** FastAPI
* **ORM:** SQLAlchemy 2.0+
* **Database Migrations:** Alembic
* **Database:** PostgreSQL 16
* **Authentication:** JWT (`python-jose`) + `passlib` (bcrypt)
* **Data Validation:** Pydantic v2
* **ASGI Server:** Uvicorn
* **Containerization:** Docker & Docker Compose
* **Testing:** `pytest` + `httpx`

---

## Project Structure

```text
fastapi-task-manager/
├── app/
│   ├── main.py            # FastAPI entrypoint
│   ├── config.py          # Environment settings
│   ├── database.py        # SQLAlchemy engine and session setup
│   ├── models/            # ORM models (User, Task)
│   ├── schemas/           # Pydantic schemas
│   ├── api/               # API routers (auth, tasks)
│   ├── core/              # Security (JWT, hashing), custom types
│   └── services/          # Business logic
├── alembic/               # Database migrations
├── tests/                 # pytest test suite
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
└── README.md

Quick Start (Docker)

    Copy the environment configuration file:
    Bash

    cp .env.example .env

    Run the application using Docker Compose:
    Bash

    docker compose up --build

The API includes retry logic to wait for PostgreSQL to become healthy before starting. Tables are created automatically on the first launch.

    API Base URL: http://localhost:8000

    Interactive API Docs (Swagger UI): http://localhost:8000/docs

To stop the services:
Bash

docker compose down

(To completely remove stored database data, run docker compose down -v)
Database Migrations (Alembic)

By default, database tables are auto-created on application startup for development convenience. For production environments, apply migrations manually:
Bash

docker compose exec api alembic upgrade head

To generate a new migration after modifying models:
Bash

docker compose exec api alembic revision --autogenerate -m "migration description"

Local Development (Without Docker)

    Create and activate a virtual environment:
    Bash

    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate

    Install dependencies:
    Bash

    pip install -r requirements.txt

    Configure environment variables:
    Bash

    cp .env.example .env

    (Ensure your local PostgreSQL credentials in .env are correctly set)

    Start the application:
    Bash

    uvicorn app.main:app --reload

Testing

The test suite uses an in-memory SQLite database and does not require a running PostgreSQL instance.
Bash

pytest -v

Test Coverage Includes:

    User registration (including duplicate email validation)

    User login (valid credentials and invalid password checks)

    Task creation

    Task listing (pagination and status filtering)

    Full (PUT) and partial (PATCH) task updates

    Task deletion

    Isolation checks (accessing another user's task returns 404)

    Unauthorized requests check (401)

API Examples
1. User Registration
Bash

curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "supersecret1"}'

2. User Login (Obtain JWT Token)
Bash

curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@example.com&password=supersecret1"

Response:
JSON

{
  "access_token": "eyJhbGciOi...",
  "token_type": "bearer"
}

Save your token to an environment variable for convenience:
Bash

export TOKEN="eyJhbGciOi..."

3. Create a Task
Bash

curl -X POST http://localhost:8000/tasks/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Build API", "description": "Implement CRUD", "status": "todo", "priority": "high"}'

4. Get Task List (With Pagination & Status Filter)
Bash

curl "http://localhost:8000/tasks/?skip=0&limit=10&status=todo" \
  -H "Authorization: Bearer $TOKEN"

5. Get Task by ID
Bash

curl http://localhost:8000/tasks/<task_id> \
  -H "Authorization: Bearer $TOKEN"

6. Full Task Update (PUT)
Bash

curl -X PUT http://localhost:8000/tasks/<task_id> \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Updated Title", "description": null, "status": "in_progress", "priority": "medium"}'

7. Partial Task Update (PATCH)
Bash

curl -X PATCH http://localhost:8000/tasks/<task_id> \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status": "done"}'

8. Delete Task
Bash

curl -X DELETE http://localhost:8000/tasks/<task_id> \
  -H "Authorization: Bearer $TOKEN"

Security Features

    Protected Endpoints: All /tasks/* routes require a valid Bearer token (OAuth2 Password Flow + JWT).

    Password Hashing: Passwords are stored securely using bcrypt.

    Resource Isolation: Access control checks ensure task.owner_id == current_user.id. Accessing a non-owned task returns a 404 Not Found status to avoid leaking existence of private resources.

    Environment Variables: Secret keys and database configurations are managed via .env (excluded from git tracking).

    Token Expiration: Access tokens expire after 30 minutes by default (configurable via ACCESS_TOKEN_EXPIRE_MINUTES).

Future Improvements

    Refresh token support

    User roles & authorization tiers (e.g., admin, user)

    File attachments for tasks

    Email or push notifications

    Full-text search

    Rate limiting