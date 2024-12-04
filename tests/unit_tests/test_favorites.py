# tests/unit_tests/test_favorites.py

import pytest
from fastapi.testclient import TestClient
from app.models.favorites import Favorite

def test_add_favorite(client: TestClient, test_user, test_medicine):
    favorite_data = {"medicine_id": test_medicine.id}
    response = client.post(
        f"/api/v1/users/{test_user.id}/favorites",
        json=favorite_data
    )
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == test_user.id
    assert data["medicine"]["id"] == test_medicine.id

    # Verify favorite in database
    favorite = Favorite.get_or_none(
        (Favorite.user == test_user) & (Favorite.medicine == test_medicine)
    )
    assert favorite is not None

def test_get_user_favorites(client: TestClient, test_user, test_medicine):
    # Add a favorite
    Favorite.create(user=test_user, medicine=test_medicine)

    response = client.get(f"/api/v1/users/{test_user.id}/favorites")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    favorite = data[0]
    assert favorite["user_id"] == test_user.id
    assert favorite["medicine"]["id"] == test_medicine.id

def test_remove_favorite(client: TestClient, test_user, test_medicine):
    # Add a favorite
    Favorite.create(user=test_user, medicine=test_medicine)

    response = client.delete(
        f"/api/v1/users/{test_user.id}/favorites/{test_medicine.id}"
    )
    assert response.status_code == 200
    data = response.json()
    assert data["detail"] == "Favorite removed successfully"

    # Verify favorite is removed
    favorite = Favorite.get_or_none(
        (Favorite.user == test_user) & (Favorite.medicine == test_medicine)
    )
    assert favorite is None

def test_add_duplicate_favorite(client: TestClient, test_user, test_medicine):
    # Add a favorite
    Favorite.create(user=test_user, medicine=test_medicine)

    favorite_data = {"medicine_id": test_medicine.id}
    response = client.post(
        f"/api/v1/users/{test_user.id}/favorites",
        json=favorite_data
    )
    assert response.status_code == 400
    assert "already in favorites" in response.json()["detail"]

def test_get_user_favorites_empty(client: TestClient, test_user):
    response = client.get(f"/api/v1/users/{test_user.id}/favorites")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0

def test_remove_nonexistent_favorite(client: TestClient, test_user, test_medicine):
    response = client.delete(
        f"/api/v1/users/{test_user.id}/favorites/{test_medicine.id}"
    )
    assert response.status_code == 404
    assert "Favorite not found" in response.json()["detail"]

def test_add_favorite_user_not_found(client: TestClient, test_medicine):
    favorite_data = {"medicine_id": test_medicine.id}
    response = client.post(
        "/api/v1/users/999/favorites",
        json=favorite_data
    )
    assert response.status_code == 404
    assert "User not found" in response.json()["detail"]

def test_add_favorite_medicine_not_found(client: TestClient, test_user):
    favorite_data = {"medicine_id": 999}
    response = client.post(
        f"/api/v1/users/{test_user.id}/favorites",
        json=favorite_data
    )
    assert response.status_code == 404
    assert "Medicine not found" in response.json()["detail"]


def test_remove_favorite_user_not_found(client: TestClient, test_medicine):
    response = client.delete(
        f"/api/v1/users/999/favorites/{test_medicine.id}"
    )
    assert response.status_code == 404
    assert "User not found" in response.json()["detail"]