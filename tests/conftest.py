import os
import sys
import pytest
from fastapi.testclient import TestClient

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from app.main import app
from app.database import db
from app.models.user import User
from app.models.profile import PersonalProfile, MedicalData
from app.models.medicine import Medicine
from app.models.review import Review

@pytest.fixture(scope="function")
def client():
    return TestClient(app)

@pytest.fixture(scope="function")
def test_db():
    # Use in-memory SQLite for tests
    db.connect()
    db.create_tables([
        User,
        PersonalProfile,
        MedicalData,
        Medicine,
        Review
    ])
    yield db
    db.drop_tables([
        User,
        PersonalProfile,
        MedicalData,
        Medicine,
        Review
    ])
    db.close()

@pytest.fixture
def test_user(test_db):
    user = User.create(email="test@example.com")
    return user

@pytest.fixture
def test_profile(test_user):
    profile = PersonalProfile.create(
        user=test_user,
        first_name="Test",
        last_name="User",
        age=30,
        gender="Male",
        phone="+1234567890",
        address="123 Test St"
    )
    MedicalData.create(profile=profile)
    return profile 

@pytest.fixture
def test_medicine(test_db):
    medicine = Medicine.create(
        name="Test Medicine",
        description="Test description",
        fda_id="TEST123"
    )
    return medicine