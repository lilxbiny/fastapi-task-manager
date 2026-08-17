import logging
import time

from fastapi import FastAPI
from sqlalchemy import text
from sqlalchemy.exc import OperationalError

from app.api import auth, tasks
from app.config import settings
from app.database import Base, SessionLocal, engine
from app.models import task, user  # noqa: F401  (ensure models are registered)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("app")

app = FastAPI(title=settings.PROJECT_NAME)

app.include_router(auth.router)
app.include_router(tasks.router)


def wait_for_db(max_retries: int = 10, delay_seconds: float = 2.0) -> None:
    """
    Retry the DB connection a few times before giving up.

    Postgres (in docker-compose) may still be starting up when the API
    container boots, even with `depends_on`, so we poll instead of failing
    immediately.
    """
    for attempt in range(1, max_retries + 1):
        try:
            db = SessionLocal()
            db.execute(text("SELECT 1"))
            db.close()
            logger.info("Database is ready.")
            return
        except OperationalError:
            logger.warning(
                "Database not ready yet (attempt %s/%s), retrying in %ss...",
                attempt,
                max_retries,
                delay_seconds,
            )
            time.sleep(delay_seconds)
    raise RuntimeError("Could not connect to the database after multiple retries.")


@app.on_event("startup")
def on_startup() -> None:
    wait_for_db()
    # For local/dev convenience only. In a real deployment, prefer running
    # `alembic upgrade head` explicitly instead of create_all().
    Base.metadata.create_all(bind=engine)


@app.get("/health", tags=["health"])
def health_check():
    return {"status": "ok"}
