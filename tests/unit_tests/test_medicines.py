import pytest

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