import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from ai.client import generate_image, _circuit_breaker
import os


def _reset_circuit_breaker():
    """Reset singleton circuit breaker state between tests."""
    _circuit_breaker.failure_count = 0
    _circuit_breaker.last_failure_time = 0.0


@pytest.mark.asyncio
async def test_generate_image_success():
    _reset_circuit_breaker()
    os.environ["HF_API_KEY"] = "fake_key"

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.content = b"fake_image_bytes"
    mock_response.raise_for_status = MagicMock()

    mock_client = AsyncMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)
    mock_client.post = AsyncMock(return_value=mock_response)

    with patch("ai.client.httpx.AsyncClient", return_value=mock_client):
        result = await generate_image("a cute cat")

    assert result == b"fake_image_bytes"


@pytest.mark.asyncio
async def test_generate_image_model_loading_raises():
    _reset_circuit_breaker()
    os.environ["HF_API_KEY"] = "fake_key"

    mock_response = MagicMock()
    mock_response.status_code = 503

    mock_client = AsyncMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)
    mock_client.post = AsyncMock(return_value=mock_response)

    with patch("ai.client.httpx.AsyncClient", return_value=mock_client):
        with pytest.raises(RuntimeError, match="Model is currently loading"):
            await generate_image("a cute cat")
