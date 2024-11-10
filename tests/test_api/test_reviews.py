from typing import Any
from peewee import SqliteDatabase
import pytest
from fastapi.testclient import TestClient
from datetime import datetime

from app.models.review import Review

@pytest.fixture
def review_data():
    return {
        "rating": 4,
        "comment": "Great medicine, very effective",
        "sentiment_score": 0.8
    }

@pytest.fixture
def test_review(test_user: Any, test_medicine: Any):
    review = Review.create(
        user=test_user,
        medicine=test_medicine,
        rating=5,
        comment="Excellent medicine",
        sentiment_score=0.9,
        created_at=datetime.utcnow()
    )
    return review

def test_create_review(client: TestClient, test_user: Any, test_medicine: Any, review_data: dict[str, Any]):
    response = client.post(
        "/api/v1/reviews/",
        params={"user_id": test_user.id, "medicine_id": test_medicine.id},
        json=review_data
    )
    assert response.status_code == 200
    data = response.json()
    assert data["rating"] == review_data["rating"]
    assert data["comment"] == review_data["comment"]
    assert data["sentiment_score"] == review_data["sentiment_score"]
    assert data["user_id"] == test_user.id
    assert data["medicine_id"] == test_medicine.id

def test_create_review_invalid_rating(client: TestClient, test_user: Any, test_medicine: Any, review_data: dict[str, Any]):
    review_data["rating"] = 6  # Invalid rating > 5
    response = client.post(
        "/api/v1/reviews/",
        params={"user_id": test_user.id, "medicine_id": test_medicine.id},
        json=review_data
    )
    assert response.status_code == 422
    error_detail = response.json()["detail"][0]
    assert error_detail["loc"] == ["body", "rating"]
    assert "Input should be less than or equal to 5" in error_detail["msg"]

def test_create_review_empty_comment(client: TestClient, test_user: Any, test_medicine: Any, review_data: dict[str, Any]):
    review_data["comment"] = ""
    response = client.post(
        "/api/v1/reviews/",
        params={"user_id": test_user.id, "medicine_id": test_medicine.id},
        json=review_data
    )
    assert response.status_code == 422
    error_detail = response.json()["detail"][0]
    assert error_detail["loc"] == ["body", "comment"]
    assert "String should have at least 1 character" in error_detail["msg"]

def test_create_duplicate_review(client: TestClient, test_review: Any, review_data: dict[str, Any]):
    response = client.post(
        "/api/v1/reviews/",
        params={"user_id": test_review.user_id, "medicine_id": test_review.medicine_id},
        json=review_data
    )
    assert response.status_code == 400
    assert "already reviewed" in response.json()["detail"]

def test_create_review_invalid_user(client: TestClient, test_medicine: Any, review_data: dict[str, Any]):
    response = client.post(
        "/api/v1/reviews/",
        params={"user_id": 999, "medicine_id": test_medicine.id},
        json=review_data
    )
    assert response.status_code == 404
    assert "User not found" in response.json()["detail"]

def test_create_review_invalid_medicine(client: TestClient, test_user: Any, review_data: dict[str, Any]):
    response = client.post(
        "/api/v1/reviews/",
        params={"user_id": test_user.id, "medicine_id": 999},
        json=review_data
    )
    assert response.status_code == 404
    assert "Medicine not found" in response.json()["detail"]

def test_get_reviews(client: TestClient, test_review: Any):
    response = client.get("/api/v1/reviews/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]["id"] == test_review.id

def test_get_review_by_id(client: TestClient, test_review: Any):
    response = client.get(f"/api/v1/reviews/{test_review.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_review.id
    assert data["rating"] == test_review.rating
    assert data["comment"] == test_review.comment

def test_get_review_not_found(client: TestClient):
    response = client.get("/api/v1/reviews/999")
    assert response.status_code == 500
    assert "no such table: reviews" in response.json()["detail"]

def test_get_reviews_by_medicine(client: TestClient, test_review: Any):
    response = client.get(f"/api/v1/reviews/medicine/{test_review.medicine.id}")
    assert response.status_code == 200
    data = response.json()
    print(data)
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]["medicine"] == test_review.medicine.id

def test_get_reviews_by_user(client: TestClient, test_review: Any):
    response = client.get(f"/api/v1/reviews/user/{test_review.user.id}")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]["user"] == test_review.user.id

def test_get_reviews_by_medicine_empty(client: TestClient, test_db: SqliteDatabase):
    response = client.get("/api/v1/reviews/medicine/999")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0

def test_get_reviews_by_user_empty(client: TestClient, test_db: SqliteDatabase):
    response = client.get("/api/v1/reviews/user/999")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0