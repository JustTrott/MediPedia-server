import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import db
from app.models.user import User
from app.models.medicine import Medicine
from app.models.review import Review

@pytest.fixture(scope="function")
def client():
    return TestClient(app)

@pytest.fixture(scope="function")
def test_db():
    db.connect()
    db.create_tables([User, Medicine, Review])
    yield db
    db.drop_tables([User, Medicine, Review])
    db.close() 