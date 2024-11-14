import os
import sys
import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch, MagicMock

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from app.main import app
from app.database import db
from app.models.user import User
from app.models.profile import PersonalProfile, MedicalData
from app.models.medicine import Medicine
from app.models.review import Review
from app.services.cohere_service import CohereService

@pytest.fixture
def mock_cohere_client():
    with patch('cohere.ClientV2') as mock_client:
        mock_instance = MagicMock()
        mock_client.return_value = mock_instance
        mock_instance.generate = AsyncMock()
        yield mock_instance

@pytest.fixture
def cohere_service(mock_cohere_client):
    return CohereService()

@pytest.fixture
def mock_openfda_service():
    with patch('app.services.openfda_service.OpenFDAService') as mock_service:
        mock_instance = MagicMock()
        mock_service.return_value = mock_instance
        mock_instance.find_medicine_by_label = MagicMock()
        yield mock_instance

@pytest.fixture
def mock_openfda_response():
    return {
        "generic_name": "acetaminophen",
        "description": "Pain reliever",
        "warnings": ["Liver warnings", "Alcohol warnings"]
    }

@pytest.fixture
def mock_cohere_safety_response():
    return {
        "can_take": True,
        "warning": None
    }

@pytest.fixture(scope="function")
def client():
    return TestClient(app)

@pytest.fixture(scope="function")
def test_db():
    db.connect()
    db.create_tables([User, PersonalProfile, MedicalData, Medicine, Review])
    yield db
    db.drop_tables([User, PersonalProfile, MedicalData, Medicine, Review])
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
    medical_data = MedicalData.create(
        profile=profile,
        allergies="none",
        conditions="none",
        preferred_medication_type="tablets"
    )
    return profile

@pytest.fixture
def test_medicine(test_db):
    medicine = Medicine.create(
        name="Test Medicine",
        description="Test description",
        fda_id="TEST123"
    )
    return medicine

@pytest.fixture
def test_review(test_user, test_medicine):
    review = Review.create(
        user=test_user,
        medicine=test_medicine,
        rating=5,
        comment="Great medicine!"
    )
    return review