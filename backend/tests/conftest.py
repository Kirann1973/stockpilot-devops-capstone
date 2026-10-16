import os

# Point the app at an isolated SQLite file before it is imported, so tests never
# touch the real PostgreSQL database.
os.environ["DATABASE_URL"] = "sqlite:///./test_stockpilot.db"

import pytest
from fastapi.testclient import TestClient

from app.db import Base, engine
from app.main import app


@pytest.fixture(autouse=True)
def fresh_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture
def product(client):
    payload = {
        "name": "Wireless Mouse",
        "sku": "TEST-001",
        "category": "Electronics",
        "supplier": "TechSource",
        "quantity": 50,
        "reorder_level": 10,
        "unit_price": "499.00",
    }
    response = client.post("/api/products", json=payload)
    assert response.status_code == 201
    return response.json()
