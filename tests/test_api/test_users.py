import pytest
from fastapi.testclient import TestClient
from app.models.user import User
from app.models.profile import PersonalProfile, MedicalData

def test_create_user(client, test_db):
    response = client.post(
        "/api/v1/users/",
        json={"email": "new@example.com"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "new@example.com"
    assert "id" in data

def test_create_user_invalid_email(client, test_db):
    response = client.post(
        "/api/v1/users/",
        json={"email": "invalid-email"}
    )
    assert response.status_code == 422

def test_create_user_duplicate_email(client, test_user):
    response = client.post(
        "/api/v1/users/",
        json={"email": "test@example.com"}
    )
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]

def test_get_user(client, test_user, test_profile):
    # Verify test data exists
    user = User.get_by_id(test_user.id)
    profile = PersonalProfile.get(PersonalProfile.user == user)
    medical = MedicalData.get(MedicalData.profile == profile)
    
    assert user
    assert profile
    assert medical
    
    response = client.get(f"/api/v1/users/{test_user.id}")
    assert response.status_code == 200
    data = response.json()
    
    # Check user data
    assert data["email"] == test_user.email
    assert data["id"] == test_user.id
    
    # Check profile data
    assert data["profile"] is not None
    assert data["profile"]["first_name"] == test_profile.first_name
    assert data["profile"]["last_name"] == test_profile.last_name
    
    # Check medical data
    assert data["medical_data"] is not None
    assert "allergies" in data["medical_data"]
    assert "conditions" in data["medical_data"]

def test_get_user_by_email(client, test_user):
    response = client.get(f"/api/v1/users/email/{test_user.email}")
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == test_user.email
    assert data["id"] == test_user.id

def test_get_user_by_email_not_found(client, test_db):
    response = client.get("/api/v1/users/email/nonexistent@example.com")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]

def test_get_user_not_found(client, test_db):
    response = client.get("/api/v1/users/999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]

def test_get_users(client, test_user):
    response = client.get("/api/v1/users/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["email"] == test_user.email

def test_get_user_without_profile(client, test_db):
    # Create a user without profile
    response = client.post(
        "/api/v1/users/",
        json={"email": "noprofile@example.com"}
    )
    user_id = response.json()["id"]
    
    # Get user details
    response = client.get(f"/api/v1/users/{user_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "noprofile@example.com"
    assert data["profile"] is None
    assert data["medical_data"] is None