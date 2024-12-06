import pytest
from unittest.mock import MagicMock, patch
import json
from app.services.gemini_service import GeminiService
from fastapi import UploadFile

@pytest.fixture
def mock_gemini_model():
    with patch('google.generativeai.GenerativeModel') as mock_model:
        mock_instance = MagicMock()
        mock_model.return_value = mock_instance
        yield mock_instance

@pytest.fixture
def gemini_service(mock_gemini_model):
    return GeminiService()

def test_extract_label_success(gemini_service, mock_gemini_model):
    mock_response = MagicMock()
    mock_response.text = "acetaminophen"
    mock_gemini_model.generate_content.return_value = mock_response

    result = gemini_service.extract_label("Tylenol (acetaminophen) 500mg tablets")
    
    assert result == "acetaminophen"
    mock_gemini_model.generate_content.assert_called_once()

def test_extract_label_cleanup(gemini_service, mock_gemini_model):
    mock_response = MagicMock()
    mock_response.text = "  Ibuprofen  \n  "
    mock_gemini_model.generate_content.return_value = mock_response

    result = gemini_service.extract_label("Advil (Ibuprofen) tablets")
    
    assert result == "ibuprofen"

def test_filter_by_profile_safe_medicine(gemini_service, mock_gemini_model):
    medicine_data = json.dumps({
        "name": "Acetaminophen",
        "description": "Pain reliever"
    })
    profile_data = json.dumps({
        "allergies": "none",
        "conditions": "none",
        "age": 30
    })

    mock_response = MagicMock()
    mock_response.text = '{"can_take": true, "warning": null}'
    mock_gemini_model.generate_content.return_value = mock_response

    result = gemini_service.filter_by_profile(medicine_data, profile_data)
    
    assert result["can_take"] is True
    assert result["warning"] is None

def test_filter_by_profile_unsafe_medicine(gemini_service, mock_gemini_model):
    medicine_data = json.dumps({
        "name": "Aspirin",
        "description": "Blood thinner"
    })
    profile_data = json.dumps({
        "allergies": "aspirin",
        "conditions": "none",
        "age": 45
    })

    mock_response = MagicMock()
    mock_response.text = '{"can_take": false, "warning": "Patient has aspirin allergy"}'
    mock_gemini_model.generate_content.return_value = mock_response

    result = gemini_service.filter_by_profile(medicine_data, profile_data)
    
    assert result["can_take"] is False
    assert "aspirin allergy" in result["warning"]

def test_filter_by_profile_invalid_json_response(gemini_service, mock_gemini_model):
    medicine_data = json.dumps({"name": "Test"})
    profile_data = json.dumps({"allergies": "none"})

    mock_response = MagicMock()
    mock_response.text = 'invalid json'
    mock_gemini_model.generate_content.return_value = mock_response

    result = gemini_service.filter_by_profile(medicine_data, profile_data)
    
    assert result["can_take"] is False
    assert "Error analyzing medicine safety" in result["warning"]

def test_filter_by_profile_missing_fields(gemini_service, mock_gemini_model):
    medicine_data = json.dumps({"name": "Test"})
    profile_data = json.dumps({"allergies": "none"})

    mock_response = MagicMock()
    mock_response.text = '{"warning": "some warning"}'
    mock_gemini_model.generate_content.return_value = mock_response

    result = gemini_service.filter_by_profile(medicine_data, profile_data)
    
    assert result["can_take"] is False
    assert "Error analyzing medicine safety" in result["warning"]

def test_filter_by_profile_invalid_field_types(gemini_service, mock_gemini_model):
    medicine_data = json.dumps({"name": "Test"})
    profile_data = json.dumps({"allergies": "none"})

    mock_response = MagicMock()
    mock_response.text = '{"can_take": "false", "warning": "Error analyzing medicine safety" }'
    mock_gemini_model.generate_content.return_value = mock_response

    result = gemini_service.filter_by_profile(medicine_data, profile_data)
    
    assert result["can_take"] is False
    assert "Error analyzing medicine safety" in result["warning"]

def test_extract_label_from_image_success(gemini_service, mock_gemini_model, test_image):
    mock_response = MagicMock()
    mock_response.text = "acetaminophen"
    mock_gemini_model.generate_content.return_value = mock_response

    result = gemini_service.extract_label_from_image(test_image.getvalue())
    
    assert result == "acetaminophen"
    mock_gemini_model.generate_content.assert_called_once()
    assert len(mock_gemini_model.generate_content.call_args[0][0]) == 2  # prompt and image

def test_extract_label_from_image_cleanup(gemini_service, mock_gemini_model, test_image):
    mock_response = MagicMock()
    mock_response.text = "  Ibuprofen  \n  "
    mock_gemini_model.generate_content.return_value = mock_response

    result = gemini_service.extract_label_from_image(test_image.getvalue())
    
    assert result == "ibuprofen"

def test_extract_label_from_image_error(gemini_service, mock_gemini_model, test_image):
    mock_gemini_model.generate_content.side_effect = Exception("API error")

    with pytest.raises(ValueError) as exc_info:
        gemini_service.extract_label_from_image(test_image.getvalue())
    
    assert "Failed to extract drug name from image: API error" in str(exc_info.value)

def test_extract_label_from_image_invalid_image(gemini_service, mock_gemini_model):
    result = gemini_service.extract_label_from_image(b"not an image")
    
    assert result == ""
    mock_gemini_model.generate_content.assert_not_called()

def test_extract_label_no_drug_found(gemini_service, mock_gemini_model):
    mock_response = MagicMock()
    mock_response.text = "error"
    mock_gemini_model.generate_content.return_value = mock_response

    with pytest.raises(ValueError) as exc_info:
        gemini_service.extract_label("Random text with no medicine")
    
    assert "No valid drug name found in text" in str(exc_info.value)

def test_extract_label_api_error(gemini_service, mock_gemini_model):
    mock_gemini_model.generate_content.side_effect = Exception("API error")

    with pytest.raises(ValueError) as exc_info:
        gemini_service.extract_label("Tylenol")
    
    assert "Failed to extract drug name" in str(exc_info.value)

def test_extract_label_from_image_no_drug_found(gemini_service, mock_gemini_model, test_image):
    mock_response = MagicMock()
    mock_response.text = "error"
    mock_gemini_model.generate_content.return_value = mock_response

    with pytest.raises(ValueError) as exc_info:
        gemini_service.extract_label_from_image(test_image.getvalue())
    
    assert "No valid drug name found in image" in str(exc_info.value)

def test_extract_label_from_image_invalid_image(gemini_service, mock_gemini_model):
    with pytest.raises(ValueError) as exc_info:
        gemini_service.extract_label_from_image(b"not an image")
    
    assert "Failed to extract drug name from image" in str(exc_info.value) 