import os
import sys
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import io
from PIL import Image

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from app.main import app
from app.database import test_db as db
from app.models.user import User
from app.models.profile import PersonalProfile, MedicalData
from app.models.medicine import Medicine
from app.models.review import Review
from app.models.favorites import Favorite
from app.services.gemini_service import GeminiService

@pytest.fixture
def mock_gemini_model():
    with patch('google.generativeai.GenerativeModel') as mock_model:
        mock_instance = MagicMock()
        mock_model.return_value = mock_instance
        mock_instance.generate_content = MagicMock()
        yield mock_instance

@pytest.fixture
def gemini_service(mock_gemini_model):
    return GeminiService()

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
    db.bind([User, PersonalProfile, MedicalData, Medicine, Review, Favorite], bind_refs=False, bind_backrefs=False)
    db.connect()
    db.create_tables([User, PersonalProfile, MedicalData, Medicine, Review, Favorite])
    yield db
    db.drop_tables([User, PersonalProfile, MedicalData, Medicine, Review, Favorite])
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
        name="ibuprofen",
        description="For temporary relief of minor aches and pains",
        fda_id="123456"
    )
    return medicine

@pytest.fixture
def test_review(test_user, test_medicine):
    review = Review.create(
        user=test_user,
        medicine=test_medicine,
        rating=5,
        comment="Great medicine!",
        sentiment_score=0.9
    )
    return review

@pytest.fixture
def mock_openfda_full_response():
    return {
        "meta": {
            "results": {
                "total": 1
            }
        },
        "results": [{
            "spl_product_data_elements": ["test data"],
            "active_ingredient": ["ibuprofen 200mg"],
            "purpose": ["Pain reliever"],
            "indications_and_usage": ["For temporary relief of minor aches and pains"],
            "warnings": ["Do not use if allergic"],
            "do_not_use": ["If you have ever had an allergic reaction"],
            "ask_doctor": ["Before use if pregnant"],
            "ask_doctor_or_pharmacist": ["About interactions"],
            "stop_use": ["If pain persists"],
            "pregnancy_or_breast_feeding": ["Ask health professional"],
            "keep_out_of_reach_of_children": ["Store in safe place"],
            "dosage_and_administration": ["Take 1 tablet every 4-6 hours"],
            "storage_and_handling": ["Store at room temperature"],
            "inactive_ingredient": ["starch, cellulose"],
            "questions": ["Call 1-800-xxx-xxxx"],
            "package_label_principal_display_panel": ["Front panel image"],
            "set_id": "abc123",
            "id": "123456",
            "effective_time": "20230101",
            "version": "1",
            "openfda": {
                "application_number": ["ANDA123456"],
                "brand_name": ["Advil"],
                "generic_name": ["ibuprofen"],
                "manufacturer_name": ["Pfizer"],
                "product_ndc": ["12345-678-90"],
                "product_type": ["HUMAN OTC DRUG"],
                "route": ["ORAL"],
                "substance_name": ["IBUPROFEN"],
                "rxcui": ["123456"],
                "spl_id": ["abc123"],
                "spl_set_id": ["def456"],
                "package_ndc": ["12345-678-90"],
                "is_original_packager": [True],
                "upc": ["123456789012"],
                "unii": ["WK2XYI10QM"]
            }
        }]
    }

@pytest.fixture
def mock_openfda_empty_response():
    return {
        "meta": {
            "results": {
                "total": 0
            }
        },
        "results": []
    }

@pytest.fixture
def mock_openfda_malformed_response():
    return {
        "meta": {
            "results": {
                "total": 1
            }
        },
        "results": [{
            "id": "123456",
            "openfda": {
                "generic_name": ["ibuprofen"]
            }
        }]
    }

@pytest.fixture
def test_image():
    # Create a simple test image with some white text on black background
    img = Image.new('RGB', (100, 30), color='white')
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    return img_byte_arr