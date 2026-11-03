from datetime import date

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app


# Base de datos SQLite en memoria: las pruebas no tocan PostgreSQL
@pytest.fixture
def client():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    TestingSession = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

    def get_test_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = get_test_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def registrar(client: TestClient, email: str = "ana@test.com", password: str = "123456") -> dict:
    respuesta = client.post("/api/auth/register", json={"email": email, "password": password})
    assert respuesta.status_code == 201, respuesta.text
    return {"Authorization": f"Bearer {respuesta.json()['access_token']}"}


@pytest.fixture
def auth(client):
    return registrar(client)


@pytest.fixture
def hoy() -> date:
    return date.today()


def mes_de(fecha: date) -> str:
    return fecha.strftime("%Y-%m")
