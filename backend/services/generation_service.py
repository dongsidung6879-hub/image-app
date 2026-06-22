from tenacity import RetryError
from utils.circuit_breaker import CircuitBreaker
from ai.client import call_llm_api
from ai.fallback_client import call_openai_api
import logging

logger = logging.getLogger(__name__)

global_circuit_breaker = CircuitBreaker()

class GenerationService:
    def __init__(self, circuit_breaker: CircuitBreaker = None):
        self.cb = circuit_breaker or global_circuit_breaker

    def _attempt_fallback(self, prompt: str) -> dict:
        try:
            logger.info("Attempting Soft Fallback to OpenAI...")
            result = call_openai_api(prompt)
            return {"status": "success", "source": "fallback", "data": result}
        except Exception as e:
            logger.error(f"Fallback also failed: {str(e)}")
            return {
                "status": "error", 
                "code": "CAPACITY_EXHAUSTED", 
                "message": "AI models are currently overloaded. Please try again in a few minutes."
            }

    def generate_content(self, prompt: str) -> dict:
        # Nếu Circuit Breaker ngắt mạch, thử Fallback ngay lập tức
        if not self.cb.is_allow_request():
            return self._attempt_fallback(prompt)
        
        try:
            # Gọi LLM Client (đã bọc Retry loop)
            result = call_llm_api(prompt)
            self.cb.record_success()
            return {"status": "success", "source": "primary", "data": result}
        except RetryError:
            # Bị RetryError tức là thử 5 lần đều fail
            self.cb.failure_count = self.cb.failure_threshold
            self.cb.record_failure() # Ngắt mạch lập tức
            
            # Thử Fallback
            return self._attempt_fallback(prompt)
