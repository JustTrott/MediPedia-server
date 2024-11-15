from app.services.openfda_service import OpenFDAService, MedicineResult, OpenFDAInfo
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
import requests

def test_find_medicine_by_label_success(test_db, mock_openfda_full_response):
    with patch('requests.get') as mock_get:
        mock_get.return_value.json.return_value = mock_openfda_full_response
        mock_get.return_value.status_code = 200

        medicine = OpenFDAService().find_medicine_by_label("ibuprofen")
        
        # Verify the structure matches MedicineResult TypedDict
        assert isinstance(medicine, dict)
        assert medicine["id"] == "123456"
        assert medicine["openfda"]["generic_name"] == ["ibuprofen"]
        assert medicine["openfda"]["brand_name"] == ["Advil"]
        assert medicine["indications_and_usage"] == ["For temporary relief of minor aches and pains"]
        assert medicine["openfda"]["manufacturer_name"] == ["Pfizer"]
        assert medicine["openfda"]["product_type"] == ["HUMAN OTC DRUG"]

def test_find_medicine_by_label_not_found(test_db, mock_openfda_empty_response):
    with patch('requests.get') as mock_get:
        mock_get.return_value.json.return_value = mock_openfda_empty_response
        mock_get.return_value.status_code = 200

        medicine = OpenFDAService().find_medicine_by_label("nonexistent-medicine")
        assert medicine is None

def test_find_medicine_by_label_api_error(test_db):
    with patch('requests.get') as mock_get:
        mock_get.side_effect = requests.exceptions.RequestException("API error")

        medicine = OpenFDAService().find_medicine_by_label("ibuprofen")
        assert medicine is None

def test_find_medicine_by_label_malformed_response(test_db, mock_openfda_malformed_response):
    with patch('requests.get') as mock_get:
        mock_get.return_value.json.return_value = mock_openfda_malformed_response
        mock_get.return_value.status_code = 200

        medicine = OpenFDAService().find_medicine_by_label("ibuprofen")
        # Should still return the partial data
        assert medicine["id"] == "123456"
        assert medicine["openfda"]["generic_name"] == ["ibuprofen"]