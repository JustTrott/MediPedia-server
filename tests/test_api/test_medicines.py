import pytest
from fastapi.testclient import TestClient

@pytest.fixture
def medicine_data():
    return {
        "name": "Aspirin",
        "description": "Pain reliever and fever reducer",
        "fda_id": "N012345"
    }

def test_create_medicine(client, test_db, medicine_data):
    response = client.post(
        "/api/v1/medicines/",
        json=medicine_data
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == medicine_data["name"]
    assert data["description"] == medicine_data["description"]
    assert data["fda_id"] == medicine_data["fda_id"]

def test_create_medicine_minimal(client, test_db):
    minimal_data = {
        "name": "Ibuprofen"
    }
    response = client.post(
        "/api/v1/medicines/",
        json=minimal_data
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == minimal_data["name"]
    assert data["description"] is None
    assert data["fda_id"] is None

def test_create_medicine_missing_name(client, test_db):
    invalid_data = {
        "description": "Missing required name field"
    }
    response = client.post(
        "/api/v1/medicines/",
        json=invalid_data
    )
    assert response.status_code == 422
    error_detail = response.json()["detail"][0]
    assert error_detail["loc"] == ["body", "name"]
    assert "Field required" in error_detail["msg"]

def test_create_medicine_invalid_type(client, test_db):
    invalid_data = {
        "name": 123,  # Should be string
        "description": True  # Should be string
    }
    response = client.post(
        "/api/v1/medicines/",
        json=invalid_data
    )
    assert response.status_code == 422
    error_detail = response.json()["detail"][0]
    assert error_detail["loc"] == ["body", "name"]
    assert "Input should be a valid string" in error_detail["msg"]

def test_get_medicine(client, test_db, medicine_data):
    # First create a medicine
    create_response = client.post(
        "/api/v1/medicines/",
        json=medicine_data
    )
    medicine_id = create_response.json()["id"]
    
    # Then get it
    response = client.get(f"/api/v1/medicines/{medicine_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == medicine_data["name"]
    assert data["description"] == medicine_data["description"]

def test_get_medicine_not_found(client, test_db):
    response = client.get("/api/v1/medicines/999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]

def test_get_medicines_list(client, test_db, medicine_data):
    # Create a medicine first
    client.post("/api/v1/medicines/", json=medicine_data)
    
    # Get list of medicines
    response = client.get("/api/v1/medicines/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]["name"] == medicine_data["name"]

def test_create_medicine_database_error(client, test_db, medicine_data, monkeypatch):
    def mock_create(*args, **kwargs):
        raise Exception("Database error")
    
    from app.models.medicine import Medicine
    monkeypatch.setattr(Medicine, "create", mock_create)
    
    response = client.post(
        "/api/v1/medicines/",
        json=medicine_data
    )
    assert response.status_code == 500
    assert "Database error" in response.json()["detail"]