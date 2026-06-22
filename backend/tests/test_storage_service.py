import pytest
from unittest.mock import patch, MagicMock
from services.storage_service import download_and_save_image
import os
from pathlib import Path

@pytest.mark.asyncio
@patch("services.storage_service.httpx.AsyncClient.get")
async def test_download_and_save_image(mock_get):
    # Setup mock for httpx
    mock_response = MagicMock()
    mock_response.content = b"fake_image_data"
    mock_response.raise_for_status = MagicMock()
    mock_get.return_value = mock_response
    
    result = await download_and_save_image("http://fake.com/img.png")
    
    assert result.startswith("uploads/")
    assert result.endswith(".png")
    
    # Verify file was created
    file_path = Path(result)
    assert file_path.exists()
    
    # Verify content
    with open(file_path, "rb") as f:
        content = f.read()
    assert content == b"fake_image_data"
    
    # Clean up
    os.remove(file_path)
