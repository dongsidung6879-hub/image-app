import pytest
from unittest.mock import patch, AsyncMock
from services.generation_service import GenerationService

@pytest.mark.asyncio
@patch("services.generation_service.generate_image", new_callable=AsyncMock)
async def test_generation_service(mock_generate):
    mock_generate.return_value = b"fake_image_bytes"
    
    service = GenerationService()
    result = await service.generate_content("test prompt")
    
    assert result == b"fake_image_bytes"
    mock_generate.assert_called_once_with("test prompt")
