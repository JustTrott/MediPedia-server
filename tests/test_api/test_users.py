import pytest
from fastapi.testclient import TestClient

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
    error_detail = response.json()["detail"][0]
    assert error_detail["loc"] == ["body", "email"]
    assert "Invalid email format" in error_detail["msg"]

def test_create_user_duplicate_email(client, test_user):
    response = client.post(
        "/api/v1/users/",
        json={"email": "test@example.com"}
    )
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]

def test_get_user(client, test_user):
    response = client.get(f"/api/v1/users/{test_user.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == test_user.email
    assert data["id"] == test_user.id

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