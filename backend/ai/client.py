import os
import logging
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential_jitter, retry_if_exception_type

from utils.circuit_breaker import CircuitBreaker

logger = logging.getLogger(__name__)

# Singleton circuit breaker cho toàn bộ app (per worker)
_circuit_breaker = CircuitBreaker(failure_threshold=5, recovery_timeout=300.0)

HF_MODEL_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"


@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential_jitter(initial=10, max=120, exp_base=1.6),
    retry=retry_if_exception_type(RuntimeError),
    reraise=True,
)
async def generate_image(prompt: str) -> bytes:
    hf_api_key = os.getenv("HF_API_KEY", "")
    if not hf_api_key:
        raise ValueError("HF_API_KEY is not set")

    if not _circuit_breaker.is_allow_request():
        raise RuntimeError("AI service is currently unavailable (circuit open). Please try again later.")

    headers = {"Authorization": f"Bearer {hf_api_key}"}
    payload = {"inputs": prompt}

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(HF_MODEL_URL, headers=headers, json=payload)

        if response.status_code == 503:
            _circuit_breaker.record_failure()
            raise RuntimeError("Model is currently loading. Please wait 30-60 seconds and try again.")

        response.raise_for_status()
        _circuit_breaker.record_success()
        return response.content

    except httpx.HTTPStatusError:
        _circuit_breaker.record_failure()
        raise
    except httpx.RequestError as exc:
        _circuit_breaker.record_failure()
        raise RuntimeError(f"Network error when calling HF API: {exc}") from exc
