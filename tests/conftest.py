"""
Test configuration.

Tests run against an in-memory SQLite database instead of the real
PostgreSQL instance, so `pytest` can run standalone without docker-compose.
We swap out the UUID-as-native-postgres-type columns for SQLAlchemy's
generic type by relying on SQLite's loose typing (it stores the UUID's
string repr transparently via the postgres UUID type's Python-side
handling), which works fine for these tests since we never hit
Postgres-only SQL features.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app

SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture()
def client():
    # Skip the real startup event (which waits for Postgres); tests use
    # SQLite tables created directly by the setup_database fixture above.
    app.router.on_startup = []
    with TestClient(app) as c:
        yield c


@pytest.fixture()
def auth_headers(client):
    """Register + log in a user, return Authorization headers for it."""

    def _make(email: str = "user@example.com", password: str = "supersecret1"):
        client.post("/auth/register", json={"email": email, "password": password})
        resp = client.post(
            "/auth/login",
            data={"username": email, "password": password},
        )
        token = resp.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    return _make
