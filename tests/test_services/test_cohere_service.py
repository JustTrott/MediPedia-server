import pytest
import json
from unittest.mock import AsyncMock, patch, MagicMock

@pytest.mark.asyncio
async def test_extract_label_success(cohere_service, mock_cohere_client):
    # Mock response
    mock_response = MagicMock()
    mock_response.generations = [MagicMock(text="acetaminophen")]
    mock_cohere_client.generate.return_value = mock_response

    result = await cohere_service.extract_label("Tylenol (acetaminophen) 500mg tablets")
    
    assert result == "acetaminophen"
    mock_cohere_client.generate.assert_called_once()

@pytest.mark.asyncio
async def test_extract_label_cleanup(cohere_service, mock_cohere_client):
    # Test that the service properly cleans up whitespace and formatting
    mock_response = MagicMock()
    mock_response.generations = [MagicMock(text="  Ibuprofen  \n  ")]
    mock_cohere_client.generate.return_value = mock_response

    result = await cohere_service.extract_label("Advil (Ibuprofen) tablets")
    
    assert result == "ibuprofen"

@pytest.mark.asyncio
async def test_filter_by_profile_safe_medicine(cohere_service, mock_cohere_client):
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
    mock_response.generations = [MagicMock(text='{"can_take": true, "warning": null}')]
    mock_cohere_client.generate.return_value = mock_response

    result = await cohere_service.filter_by_profile(medicine_data, profile_data)
    
    assert result["can_take"] is True
    assert result["warning"] is None

@pytest.mark.asyncio
async def test_filter_by_profile_unsafe_medicine(cohere_service, mock_cohere_client):
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
    mock_response.generations = [
        MagicMock(text='{"can_take": false, "warning": "Patient has aspirin allergy"}')
    ]
    mock_cohere_client.generate.return_value = mock_response

    result = await cohere_service.filter_by_profile(medicine_data, profile_data)
    
    assert result["can_take"] is False
    assert "aspirin allergy" in result["warning"]

@pytest.mark.asyncio
async def test_filter_by_profile_invalid_json_response(cohere_service, mock_cohere_client):
    medicine_data = json.dumps({"name": "Test"})
    profile_data = json.dumps({"allergies": "none"})

    mock_response = MagicMock()
    mock_response.generations = [MagicMock(text='invalid json')]
    mock_cohere_client.generate.return_value = mock_response

    result = await cohere_service.filter_by_profile(medicine_data, profile_data)
    
    assert result["can_take"] is False
    assert "Error analyzing medicine safety" in result["warning"]

@pytest.mark.asyncio
async def test_filter_by_profile_missing_fields(cohere_service, mock_cohere_client):
    medicine_data = json.dumps({"name": "Test"})
    profile_data = json.dumps({"allergies": "none"})

    mock_response = MagicMock()
    mock_response.generations = [MagicMock(text='{"warning": "some warning"}')]
    mock_cohere_client.generate.return_value = mock_response

    result = await cohere_service.filter_by_profile(medicine_data, profile_data)
    
    assert result["can_take"] is False
    assert "Error analyzing medicine safety" in result["warning"]

@pytest.mark.asyncio
async def test_filter_by_profile_invalid_field_types(cohere_service, mock_cohere_client):
    medicine_data = json.dumps({"name": "Test"})
    profile_data = json.dumps({"allergies": "none"})

    mock_response = MagicMock()
    mock_response.generations = [
        MagicMock(text='{"can_take": "false", "warning": "Error analyzing medicine safety" }')  # Invalid types
    ]
    mock_cohere_client.generate.return_value = mock_response

    result = await cohere_service.filter_by_profile(medicine_data, profile_data)
    
    assert result["can_take"] is False
    assert "Error analyzing medicine safety" in result["warning"] 