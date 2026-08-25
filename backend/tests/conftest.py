from _collections_abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

import app.models # noqa: F401
from app.config import settings
from app.database import Base, get_db
from app.main import app

from scripts.seed_songs import seed_songs

if settings.test_database_url is None:
    raise RuntimeError("TEST_DATABASE_URL não foi configurada.")

test_engine = create_engine(
    settings.test_database_url,
)

TestingSessionLocal = sessionmaker(
    bind=test_engine,
    autoflush=False,
    expire_on_commit=False,
)

def override_get_db() -> Generator[Session, None, None]:
    with TestingSessionLocal() as session:
        yield session

@pytest.fixture(autouse=True)
def reset_database() -> Generator[None, None, None]:
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)

    with TestingSessionLocal() as session:
        seed_songs(session)

    yield

    Base.metadata.drop_all(bind=test_engine)

@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    with TestingSessionLocal() as session:
        yield session

@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.pop(get_db, None)

@pytest.fixture 
def db_session() -> Generator[
    Session,
    None,
    None,
]:
    with TestingSessionLocal() as session: 
        yield session