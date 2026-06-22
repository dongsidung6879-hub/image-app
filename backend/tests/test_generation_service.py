import pytest
from unittest.mock import patch, MagicMock
from services.generation_service import GenerationService
from utils.circuit_breaker import CircuitBreaker

@patch("services.generation_service.call_openai_api")
@patch("services.generation_service.call_llm_api")
def test_generation_soft_fallback(mock_fal, mock_openai):
    # Mock FAL AI fails, CircuitBreaker trips, we fall back to OpenAI
    cb = CircuitBreaker()
    service = GenerationService(circuit_breaker=cb)
    
    # Ép CB sang OPEN
    for _ in range(5):
        cb.record_failure()
        
    mock_openai.return_value = {"data": [{"url": "http://openai.com/image.png"}]}
    
    result = service.generate_content("test")
    
    assert result["status"] == "success"
    assert result["source"] == "fallback"
    assert result["data"] == {"data": [{"url": "http://openai.com/image.png"}]}
    assert mock_fal.call_count == 0
    assert mock_openai.call_count == 1

@patch("services.generation_service.call_openai_api")
@patch("services.generation_service.call_llm_api")
def test_generation_hard_fallback_if_both_fail(mock_fal, mock_openai):
    cb = CircuitBreaker()
    service = GenerationService(circuit_breaker=cb)
    
    for _ in range(5):
        cb.record_failure()
        
    mock_openai.side_effect = Exception("OpenAI Error")
    
    result = service.generate_content("test")
    
    assert result["status"] == "error"
    assert result["code"] == "CAPACITY_EXHAUSTED"
