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
    )
    return review

def test_create_review(client: TestClient, test_user: Any, test_medicine: Any, test_db: SqliteDatabase, review_data: dict):
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
    assert data["user"] == test_user.id
    assert data["medicine"] == test_medicine.id

def test_create_review_invalid_rating(client: TestClient, test_user: Any, test_medicine: Any, test_db: SqliteDatabase):
    response = client.post(
        "/api/v1/reviews/",
        params={"user_id": test_user.id, "medicine_id": test_medicine.id},
        json={"rating": 6, "comment": "Test review", "sentiment_score": 0.5}
    )
    assert response.status_code == 422

def test_create_review_empty_comment(client: TestClient, test_user: Any, test_medicine: Any, test_db: SqliteDatabase):
    response = client.post(
        "/api/v1/reviews/",
        params={"user_id": test_user.id, "medicine_id": test_medicine.id},
        json={"rating": 4, "comment": "", "sentiment_score": 0.5}
    )
    assert response.status_code == 422

def test_create_duplicate_review(client: TestClient, test_review: Any, test_db: SqliteDatabase):
    response = client.post(
        "/api/v1/reviews/",
        params={"user_id": test_review.user.id, "medicine_id": test_review.medicine.id},
        json={"rating": 4, "comment": "Another review", "sentiment_score": 0.5}
    )
    assert response.status_code == 400
    assert "already reviewed" in response.json()["detail"]

def test_get_reviews(client: TestClient, test_review: Any, test_db: SqliteDatabase):
    response = client.get("/api/v1/reviews/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    review = data[0]
    assert review["rating"] == test_review.rating
    assert review["comment"] == test_review.comment
    assert review["user"] == test_review.user.id
    assert review["medicine"] == test_review.medicine.id

def test_get_review_by_id(client: TestClient, test_review: Any):
    response = client.get(f"/api/v1/reviews/{test_review.id}")
    assert response.status_code == 200
    data = response.json()
    print(data)
    assert data["rating"] == test_review.rating
    assert data["comment"] == test_review.comment
    assert data["user"] == test_review.user.id
    assert data["medicine"] == test_review.medicine.id

def test_get_review_not_found(client: TestClient, test_db: SqliteDatabase):
    response = client.get("/api/v1/reviews/999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]

def test_get_reviews_by_medicine(client: TestClient, test_review: Any, test_db: SqliteDatabase):
    response = client.get(f"/api/v1/reviews/medicine/{test_review.medicine.id}")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    review = data[0]
    assert review["rating"] == test_review.rating
    assert review["medicine"] == test_review.medicine.id

def test_get_reviews_by_user(client: TestClient, test_review: Any, test_db: SqliteDatabase):
    response = client.get(f"/api/v1/reviews/user/{test_review.user.id}")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    review = data[0]
    assert review["rating"] == test_review.rating
    assert review["user"] == test_review.user.id

def test_get_reviews_by_medicine_empty(client: TestClient, test_db: SqliteDatabase):
    response = client.get("/api/v1/reviews/medicine/999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]

def test_get_reviews_by_user_empty(client: TestClient, test_db: SqliteDatabase):
    response = client.get("/api/v1/reviews/user/999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]