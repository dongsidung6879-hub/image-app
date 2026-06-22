import pytest
from unittest.mock import patch
from services.generation_service import GenerationService
from utils.circuit_breaker import CircuitBreaker

@patch("services.generation_service.call_llm_api")
def test_generation_fallback_when_circuit_open(mock_call):
    cb = CircuitBreaker()
    service = GenerationService(circuit_breaker=cb)
    
    for _ in range(5):
        cb.record_failure()
        
    result = service.generate_content("test")
    
    assert result["status"] == "error"
    assert result["code"] == "CAPACITY_EXHAUSTED"
    assert mock_call.call_count == 0
