import os

os.environ["DATABASE_URL"] = "sqlite:///./test_duma.db"

import pytest
from fastapi.testclient import TestClient

from app.database import Base, engine


@pytest.fixture(autouse=True)
def _clean_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    from app.main import app

    return TestClient(app)
