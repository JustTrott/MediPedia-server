from app.services.openfda_service import OpenFDAService
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
import requests

def test_find_medicine_by_label_success(test_db):
    with patch('requests.get') as mock_get:
        mock_get.return_value.json.return_value = {
            "meta": {
                "total": 1
            },
            "results": [
                {
                    "generic_name": "ibuprofen",
                    "description": "Pain reliever and fever reducer"
                }
            ]
        }
        mock_get.return_value.status_code = 200

        medicine = OpenFDAService().find_medicine_by_label("ibuprofen")
        assert medicine["generic_name"] == "ibuprofen"
        assert medicine["description"] == "Pain reliever and fever reducer"

def test_find_medicine_by_label_not_found(test_db):
    with patch('requests.get') as mock_get:
        mock_get.return_value.json.return_value = {
            "meta": {
                "total": 0
            },
            "results": []
        }
        mock_get.return_value.status_code = 200

        medicine = OpenFDAService().find_medicine_by_label("paracetamol")
        assert medicine is None

def test_find_medicine_by_label_api_error(test_db):
    with patch('requests.get') as mock_get:
        mock_get.side_effect = requests.exceptions.RequestException("API error")

        medicine = OpenFDAService().find_medicine_by_label("ibuprofen")
        assert medicine is None