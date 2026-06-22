import pytest
from tenacity import RetryError
from unittest.mock import patch, MagicMock
import httpx
from ai.client import call_llm_api

@patch("ai.client.httpx.post")
def test_call_llm_api_retries_and_fails(mock_post):
    # Cấu hình mock để luôn raise HTTPError (mô phỏng 503)
    mock_post.side_effect = httpx.HTTPStatusError(
        "503 Service Unavailable", 
        request=MagicMock(), 
        response=MagicMock(status_code=503)
    )
    
    with pytest.raises(RetryError):
        call_llm_api("hello")
        
    assert mock_post.call_count == 5

@patch("ai.client.httpx.post")
def test_call_llm_api_success(mock_post):
    # Cấu hình mock để trả về 200 OK
    mock_response = MagicMock()
    mock_response.json.return_value = {"images": [{"url": "http://example.com/image.png"}]}
    mock_post.return_value = mock_response
    
    result = call_llm_api("hello")
    
    assert result == {"images": [{"url": "http://example.com/image.png"}]}
    assert mock_post.call_count == 1
