import os
import logging
import urllib.parse
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential_jitter, retry_if_exception_type

from utils.circuit_breaker import CircuitBreaker

logger = logging.getLogger(__name__)

# Singleton circuit breaker cho toàn bộ app (per worker)
_circuit_breaker = CircuitBreaker(failure_threshold=5, recovery_timeout=300.0)

# Primary: Pollinations.ai — free, no API key, highly available
POLLINATIONS_URL = "https://image.pollinations.ai/prompt/{prompt}?nologo=true&width=768&height=768&model=flux"

# Fallback: HuggingFace Inference API
HF_MODEL_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"


async def _generate_via_pollinations(prompt: str) -> bytes:
    """Call Pollinations.ai — returns image bytes directly via GET request."""
    encoded = urllib.parse.quote(prompt)
    url = POLLINATIONS_URL.format(prompt=encoded)
    async with httpx.AsyncClient(timeout=120.0, follow_redirects=True) as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.content


async def _generate_via_huggingface(prompt: str) -> bytes:
    """Call HuggingFace Inference API — requires HF_API_KEY env var."""
    hf_api_key = os.getenv("HF_API_KEY", "")
    if not hf_api_key:
        raise ValueError("HF_API_KEY is not set")

    headers = {"Authorization": f"Bearer {hf_api_key}"}
    payload = {"inputs": prompt}

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(HF_MODEL_URL, headers=headers, json=payload)

    if response.status_code == 503:
        raise RuntimeError("HF model is currently loading. Please wait 30-60 seconds and try again.")

    response.raise_for_status()
    return response.content


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential_jitter(initial=5, max=30, exp_base=1.5),
    retry=retry_if_exception_type(RuntimeError),
    reraise=True,
)
async def generate_image(prompt: str) -> bytes:
    """Generate image using Pollinations.ai (primary) with HuggingFace as fallback."""
    if not _circuit_breaker.is_allow_request():
        raise RuntimeError("AI service is currently unavailable (circuit open). Please try again later.")

    # --- Primary: Pollinations.ai ---
    try:
        logger.info("Calling Pollinations.ai for prompt: %.60s", prompt)
        image_bytes = await _generate_via_pollinations(prompt)
        _circuit_breaker.record_success()
        logger.info("Pollinations.ai returned %d bytes", len(image_bytes))
        return image_bytes
    except httpx.RequestError as exc:
        logger.warning("Pollinations.ai request failed: %s. Falling back to HuggingFace.", exc)
    except httpx.HTTPStatusError as exc:
        logger.warning("Pollinations.ai HTTP error %s. Falling back to HuggingFace.", exc.response.status_code)

    # --- Fallback: HuggingFace ---
    try:
        logger.info("Calling HuggingFace API for prompt: %.60s", prompt)
        image_bytes = await _generate_via_huggingface(prompt)
        _circuit_breaker.record_success()
        logger.info("HuggingFace API returned %d bytes", len(image_bytes))
        return image_bytes
    except httpx.RequestError as exc:
        _circuit_breaker.record_failure()
        raise RuntimeError(f"Network error when calling HF API: {exc}") from exc
    except httpx.HTTPStatusError as exc:
        _circuit_breaker.record_failure()
        raise RuntimeError(f"HF API HTTP error: {exc.response.status_code}") from exc
