import pytest
from tenacity import RetryError
from unittest.mock import patch
from ai.client import call_llm_api

@patch("ai.client.fake_network_request")
def test_call_llm_api_retries_and_fails(mock_request):
    # Cấu hình mock để luôn raise Exception
    mock_request.side_effect = Exception("API 503")
    
    with pytest.raises(RetryError):
        call_llm_api("hello")
        
    # Kiểm tra xem nó đã cố gắng gọi ít nhất 5 lần
    assert mock_request.call_count == 5
