import pytest
from unittest.mock import patch

@pytest.fixture
def medicine_data():
    return {
        "name": "Aspirin",
        "description": "Pain reliever and fever reducer",
        "fda_id": "N012345"
    }

def test_create_medicine(client, test_db, medicine_data):
    response = client.post("/api/v1/medicines/", json=medicine_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == medicine_data["name"]
    assert data["description"] == medicine_data["description"]
    assert data["fda_id"] == medicine_data["fda_id"]

def test_get_medicine(client, test_medicine):
    response = client.get(f"/api/v1/medicines/{test_medicine.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == test_medicine.name
    assert data["description"] == test_medicine.description

def test_get_medicine_not_found(client, test_db):
    response = client.get("/api/v1/medicines/999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]

def test_get_medicines_list(client, test_medicine):
    response = client.get("/api/v1/medicines/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]["name"] == test_medicine.name

def test_display_list_success(client, test_user, test_profile, mock_openfda_response, test_db):
    with patch('app.services.cohere_service.CohereService.extract_label') as mock_extract, \
         patch('app.services.cohere_service.CohereService.filter_by_profile') as mock_filter, \
         patch('app.services.openfda_service.OpenFDAService.find_medicine_by_label') as mock_find:
        
        mock_extract.return_value = "acetaminophen"
        mock_find.return_value = mock_openfda_response
        mock_filter.return_value = {"can_take": True, "warning": None}

        response = client.post(f"/api/v1/medicines/{test_user.id}/search/Tylenol")
        
        assert response.status_code == 200
        data = response.json()
        assert "medicine" in data
        assert "safety" in data
        assert data["medicine"]["generic_name"] == "acetaminophen"
        assert data["safety"]["can_take"] is True

def test_display_list_user_not_found(client, test_db):
    response = client.post("/api/v1/medicines/999/search/Tylenol")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]

def test_display_list_medicine_not_found(client, test_user, test_profile):
    with patch('app.services.cohere_service.CohereService.extract_label') as mock_extract, \
         patch('app.services.openfda_service.OpenFDAService.find_medicine_by_label') as mock_find:
        
        mock_extract.return_value = "unknown_medicine"
        mock_find.return_value = None

        response = client.post(f"/api/v1/medicines/{test_user.id}/search/UnknownMedicine")
        
        assert response.status_code == 404
        assert "Medicine not found" in response.json()["detail"]

def test_display_list_unsafe_medicine(client, test_user, test_profile, mock_openfda_response):
    with patch('app.services.cohere_service.CohereService.extract_label') as mock_extract, \
         patch('app.services.cohere_service.CohereService.filter_by_profile') as mock_filter, \
         patch('app.services.openfda_service.OpenFDAService.find_medicine_by_label') as mock_find:
        
        mock_extract.return_value = "aspirin"
        mock_find.return_value = mock_openfda_response
        mock_filter.return_value = {"can_take": False, "warning": "Patient has allergies"}

        response = client.post(f"/api/v1/medicines/{test_user.id}/search/Aspirin")
        
        assert response.status_code == 200
        data = response.json()
        assert data["safety"]["can_take"] is False
        assert "Patient has allergies" in data["safety"]["warning"]

def test_display_list_invalid_cohere_response(client, test_user, test_profile):
    with patch('app.services.cohere_service.CohereService.extract_label') as mock_extract:
        mock_extract.return_value = ""

        response = client.post(f"/api/v1/medicines/{test_user.id}/search/Tylenol")
        
        assert response.status_code == 400
        assert "Could not extract medicine name" in response.json()["detail"]