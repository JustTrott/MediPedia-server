import pytest
from unittest.mock import patch
from app.models.medicine import Medicine
from app.models.review import Review
import io
from PIL import Image

def test_display_list_success(client, test_user, test_profile, mock_openfda_full_response):
    with patch('app.services.gemini_service.GeminiService.extract_label') as mock_extract, \
         patch('app.services.gemini_service.GeminiService.filter_by_profile') as mock_filter, \
         patch('app.services.openfda_service.OpenFDAService.find_medicine_by_label') as mock_find:
        
        mock_extract.return_value = "ibuprofen"
        mock_find.return_value = mock_openfda_full_response["results"][0]
        mock_filter.return_value = {"can_take": True, "warning": None}

        response = client.post(f"/api/v1/medicines/{test_user.id}/search/Advil")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check medicine data
        assert "medicine" in data
        assert data["medicine"]["name"] == "ibuprofen"
        assert "reviews" in data["medicine"]
        assert isinstance(data["medicine"]["reviews"], list)
        
        # Check safety data
        assert "safety" in data
        assert data["safety"]["can_take"] is True

def test_display_list_with_existing_medicine(client, test_user, test_profile, test_medicine, test_review, mock_openfda_full_response, test_db):
    with patch('app.services.gemini_service.GeminiService.extract_label') as mock_extract, \
         patch('app.services.gemini_service.GeminiService.filter_by_profile') as mock_filter, \
         patch('app.services.openfda_service.OpenFDAService.find_medicine_by_label') as mock_find:
        
        mock_extract.return_value = "ibuprofen"
        mock_find.return_value = mock_openfda_full_response["results"][0]
        mock_filter.return_value = {"can_take": True, "warning": None}

        # Ensure test_medicine exists before making the request
        assert Medicine.get_by_id(test_medicine.id)
        assert Review.get_by_id(test_review.id)
        
        response = client.post(f"/api/v1/medicines/{test_user.id}/search/Advil")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check medicine data
        assert data["medicine"]["name"] == "ibuprofen"
        assert data["medicine"]["fda_id"] == "123456"
        
        # Check reviews are included
        assert "reviews" in data["medicine"]
        assert len(data["medicine"]["reviews"]) > 0
        
        review = data["medicine"]["reviews"][0]
        assert review["rating"] == test_review.rating
        assert review["comment"] == test_review.comment
        assert review["user"] == test_user.id

def test_display_list_user_not_found(client, test_db):
    response = client.post("/api/v1/medicines/999/search/Tylenol")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]

def test_display_list_medicine_not_found(client, test_user, test_profile):
    with patch('app.services.gemini_service.GeminiService.extract_label') as mock_extract, \
         patch('app.services.openfda_service.OpenFDAService.find_medicine_by_label') as mock_find:
        
        mock_extract.return_value = "unknown_medicine"
        mock_find.return_value = None

        response = client.post(f"/api/v1/medicines/{test_user.id}/search/UnknownMedicine")
        
        assert response.status_code == 404
        assert "Medicine not found" in response.json()["detail"]

def test_display_list_unsafe_medicine(client, test_user, test_profile, mock_openfda_full_response):
    with patch('app.services.gemini_service.GeminiService.extract_label') as mock_extract, \
         patch('app.services.gemini_service.GeminiService.filter_by_profile') as mock_filter, \
         patch('app.services.openfda_service.OpenFDAService.find_medicine_by_label') as mock_find:
        
        mock_extract.return_value = "ibuprofen"
        mock_find.return_value = mock_openfda_full_response["results"][0]
        mock_filter.return_value = {"can_take": False, "warning": "Patient has allergies"}

        response = client.post(f"/api/v1/medicines/{test_user.id}/search/Advil")
        
        assert response.status_code == 200
        data = response.json()
        assert data["safety"]["can_take"] is False
        assert "Patient has allergies" in data["safety"]["warning"]

def test_display_list_invalid_gemini_response(client, test_user, test_profile):
    with patch('app.services.gemini_service.GeminiService.extract_label') as mock_extract:
        mock_extract.return_value = ""

        response = client.post(f"/api/v1/medicines/{test_user.id}/search/Tylenol")
        
        assert response.status_code == 400
        assert "Could not extract medicine name" in response.json()["detail"]

def test_display_list_medicine_creation_error(client, test_user, test_profile, mock_openfda_full_response):
    with patch('app.services.gemini_service.GeminiService.extract_label') as mock_extract, \
         patch('app.services.gemini_service.GeminiService.filter_by_profile') as mock_filter, \
         patch('app.services.openfda_service.OpenFDAService.find_medicine_by_label') as mock_find, \
         patch('app.models.medicine.Medicine.get_or_create') as mock_create:
        
        mock_extract.return_value = "ibuprofen"
        mock_find.return_value = mock_openfda_full_response["results"][0]
        mock_filter.return_value = {"can_take": True, "warning": None}
        mock_create.side_effect = Exception("Database error")

        response = client.post(f"/api/v1/medicines/{test_user.id}/search/Advil")
        
        assert response.status_code == 500
        assert "Error processing medicine data" in response.json()["detail"]

def test_search_by_image_success(client, test_user, test_profile, mock_openfda_full_response, test_image):
    with patch('app.services.gemini_service.GeminiService.extract_label_from_image') as mock_extract, \
         patch('app.services.gemini_service.GeminiService.filter_by_profile') as mock_filter, \
         patch('app.services.openfda_service.OpenFDAService.find_medicine_by_label') as mock_find:
        
        mock_extract.return_value = "ibuprofen"
        mock_find.return_value = mock_openfda_full_response["results"][0]
        mock_filter.return_value = {"can_take": True, "warning": None}

        response = client.post(
            f"/api/v1/medicines/{test_user.id}/search/image",
            files={"file": ("test.png", test_image, "image/png")}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["medicine"]["name"] == "ibuprofen"
        assert data["safety"]["can_take"] is True
        # Verify mock was called with bytes
        mock_extract.assert_called_once()
        assert isinstance(mock_extract.call_args[0][0], bytes)

def test_search_by_image_invalid_file(client, test_user, test_profile):
    response = client.post(
        f"/api/v1/medicines/{test_user.id}/search/image",
        files={"file": ("test.txt", b"not an image", "text/plain")}
    )
    
    assert response.status_code == 400
    assert "must be an image" in response.json()["detail"]

def test_search_by_image_extraction_failed(client, test_user, test_profile, test_image):
    with patch('app.services.gemini_service.GeminiService.extract_label_from_image') as mock_extract:
        mock_extract.return_value = ""

        response = client.post(
            f"/api/v1/medicines/{test_user.id}/search/image",
            files={"file": ("test.png", test_image, "image/png")}
        )
        
        assert response.status_code == 400
        assert "Could not extract medicine name from image" in response.json()["detail"]