import pytest
from fastapi.testclient import TestClient

@pytest.fixture
def profile_data():
    return {
        "first_name": "John",
        "last_name": "Doe",
        "age": 30,
        "gender": "Male",
        "phone": "+1234567890",
        "address": "123 Main St"
    }

def test_create_profile(client, test_user, profile_data):
    response = client.post(
        f"/api/v1/profiles/{test_user.id}",
        json=profile_data
    )
    assert response.status_code == 200
    data = response.json()
    assert data["first_name"] == profile_data["first_name"]
    assert data["last_name"] == profile_data["last_name"]
    assert data["user_id"] == test_user.id

def test_create_profile_invalid_age(client, test_user, profile_data):
    profile_data["age"] = 150
    response = client.post(
        f"/api/v1/profiles/{test_user.id}",
        json=profile_data
    )
    assert response.status_code == 422
    error_detail = response.json()["detail"][0]
    assert error_detail["loc"] == ["body", "age"]
    assert "Age must be between 0 and 120" in error_detail["msg"]

def test_create_profile_invalid_phone(client, test_user, profile_data):
    profile_data["phone"] = "invalid-phone"
    response = client.post(
        f"/api/v1/profiles/{test_user.id}",
        json=profile_data
    )
    assert response.status_code == 422
    error_detail = response.json()["detail"][0]
    assert error_detail["loc"] == ["body", "phone"]
    assert "Invalid phone number format" in error_detail["msg"]

def test_create_duplicate_profile(client, test_profile, profile_data):
    response = client.post(
        f"/api/v1/profiles/{test_profile.user_id}",
        json=profile_data
    )
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]

def test_update_profile(client, test_profile, profile_data):
    profile_data["first_name"] = "Updated"
    response = client.put(
        f"/api/v1/profiles/{test_profile.id}",
        json=profile_data
    )
    assert response.status_code == 200
    data = response.json()
    assert data["first_name"] == "Updated"
    assert data["id"] == test_profile.id

def test_update_profile_not_found(client, profile_data, test_db):
    response = client.put(
        "/api/v1/profiles/999",
        json=profile_data
    )
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]

def test_update_medical_data(client, test_profile):
    medical_data = {
        "allergies": "Peanuts",
        "conditions": "None",
        "preferred_medication_type": "Tablets"
    }
    response = client.put(
        f"/api/v1/profiles/{test_profile.id}/medical",
        json=medical_data
    )
    assert response.status_code == 200
    data = response.json()
    assert data["allergies"] == medical_data["allergies"]
    assert data["conditions"] == medical_data["conditions"]
    assert data["preferred_medication_type"] == medical_data["preferred_medication_type"]

def test_update_medical_data_not_found(client, test_db):
    response = client.put(
        "/api/v1/profiles/999/medical",
        json={"allergies": "Test"}
    )
    assert response.status_code == 404
    assert "not found" in response.json()["detail"] 