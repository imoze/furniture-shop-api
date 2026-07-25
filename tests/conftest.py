import os
from pathlib import Path
from unittest.mock import Mock
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

os.environ.setdefault("DATABASE_URL","postgresql://postgres:postgres@localhost:5433/test_db")

from app.main import app
from app.db import Base, get_db
from app.sender import get_sender

TEST_DB_URL = os.getenv('DATABASE_URL')
engine = create_engine(TEST_DB_URL)
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

@pytest.fixture()
def db_session():
    INIT_SQL = Path(__file__).resolve().parent.parent / "init-db" / "init.sql"
    query = INIT_SQL.read_text(encoding="utf-8")

    conn = engine.connect()
    conn.exec_driver_sql(query)
    conn.commit()
    conn.close()

    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def mock_sender():
    sender = Mock()
    app.dependency_overrides[get_sender] = lambda: sender
    yield sender
    app.dependency_overrides.pop(get_sender, None)


@pytest.fixture()
def client(db_session):
    def override_get_db():
        yield db_session
    app.dependency_overrides[get_db] = override_get_db

    yield TestClient(app)
    app.dependency_overrides.clear()