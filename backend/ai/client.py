import logging
from tenacity import retry, stop_after_attempt, wait_exponential_jitter, retry_if_exception_type

logger = logging.getLogger(__name__)

def fake_network_request(prompt: str) -> str:
    """Mock network request. In production, this uses httpx."""
    pass

@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential_jitter(initial=10, max=120, exp_base=1.6),
    retry=retry_if_exception_type(Exception),
    reraise=False # Will raise RetryError instead
)
def call_llm_api(prompt: str) -> str:
    logger.info("Calling LLM API...")
    return fake_network_request(prompt)
