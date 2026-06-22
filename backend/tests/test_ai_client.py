import pytest
from unittest.mock import patch, MagicMock
from ai.client import generate_image
import os

@pytest.mark.asyncio
@patch("ai.client.httpx.post")
async def test_generate_image_success(mock_post):
    os.environ["HF_API_KEY"] = "fake_key"
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.content = b"fake_image_bytes"
    mock_post.return_value = mock_response
    
    result = await generate_image("a cute cat")
    assert result == b"fake_image_bytes"

@pytest.mark.asyncio
@patch("ai.client.httpx.post")
async def test_generate_image_model_loading(mock_post):
    os.environ["HF_API_KEY"] = "fake_key"
    mock_response = MagicMock()
    mock_response.status_code = 503
    mock_post.return_value = mock_response
    
    with pytest.raises(RuntimeError, match="Model is currently loading"):
        await generate_image("a cute cat")
