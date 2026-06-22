import os
import logging
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential_jitter, retry_if_exception_type

logger = logging.getLogger(__name__)

# Lấy FAL_KEY từ biến môi trường
FAL_KEY = os.getenv("FAL_KEY", "")

def make_fal_request(prompt: str) -> dict:
    """Make real HTTP request to FAL AI API."""
    url = "https://fal.run/fal-ai/fast-sdxl"
    headers = {
        "Authorization": f"Key {FAL_KEY}",
        "Content-Type": "application/json"
    }
    payload = {"prompt": prompt}
    
    response = httpx.post(url, headers=headers, json=payload, timeout=30.0)
    response.raise_for_status() # Raise exception for 4xx/5xx để trigger Retry của tenacity
    return response.json()

@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential_jitter(initial=10, max=120, exp_base=1.6),
    retry=retry_if_exception_type(Exception),
    reraise=False # Will raise RetryError instead of real Exception if all 5 retries fail
)
def call_llm_api(prompt: str) -> dict:
    logger.info(f"Calling FAL AI API for prompt: {prompt}")
    return make_fal_request(prompt)
