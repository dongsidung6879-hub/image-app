import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from ai.client import generate_image, _circuit_breaker
import os


def _reset_circuit_breaker():
    """Reset singleton circuit breaker state between tests."""
    _circuit_breaker.failure_count = 0
    _circuit_breaker.last_failure_time = 0.0


def _make_mock_client(status_code: int = 200, content: bytes = b"fake_image_bytes"):
    mock_response = MagicMock()
    mock_response.status_code = status_code
    mock_response.content = content
    mock_response.raise_for_status = MagicMock()

    mock_client = AsyncMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)
    mock_client.get = AsyncMock(return_value=mock_response)
    mock_client.post = AsyncMock(return_value=mock_response)
    return mock_client


@pytest.mark.asyncio
async def test_generate_image_success_via_pollinations():
    """Primary path: Pollinations.ai returns image bytes."""
    _reset_circuit_breaker()
    mock_client = _make_mock_client(content=b"pollinations_image_bytes")

    with patch("ai.client.httpx.AsyncClient", return_value=mock_client):
        result = await generate_image("a cute cat")

    assert result == b"pollinations_image_bytes"


@pytest.mark.asyncio
async def test_generate_image_fallback_to_huggingface():
    """When Pollinations fails, falls back to HuggingFace."""
    _reset_circuit_breaker()
    os.environ["HF_API_KEY"] = "fake_hf_key"

    import httpx as real_httpx

    call_count = 0
    hf_response = MagicMock()
    hf_response.status_code = 200
    hf_response.content = b"hf_image_bytes"
    hf_response.raise_for_status = MagicMock()

    async def mock_get(*args, **kwargs):
        raise real_httpx.RequestError("DNS failed", request=MagicMock())

    async def mock_post(*args, **kwargs):
        return hf_response

    mock_client = AsyncMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)
    mock_client.get = mock_get
    mock_client.post = mock_post

    with patch("ai.client.httpx.AsyncClient", return_value=mock_client):
        result = await generate_image("a cute cat")

    assert result == b"hf_image_bytes"


@pytest.mark.asyncio
async def test_generate_image_hf_model_loading_raises():
    """Both Pollinations fail and HF returns 503 → RuntimeError."""
    _reset_circuit_breaker()
    os.environ["HF_API_KEY"] = "fake_hf_key"

    import httpx as real_httpx

    hf_response = MagicMock()
    hf_response.status_code = 503

    async def mock_get(*args, **kwargs):
        raise real_httpx.RequestError("DNS failed", request=MagicMock())

    async def mock_post(*args, **kwargs):
        return hf_response

    mock_client = AsyncMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)
    mock_client.get = mock_get
    mock_client.post = mock_post

    with patch("ai.client.httpx.AsyncClient", return_value=mock_client):
        with pytest.raises(RuntimeError, match="HF model is currently loading"):
            await generate_image("a cute cat")
