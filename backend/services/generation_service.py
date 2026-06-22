from tenacity import RetryError
from utils.circuit_breaker import CircuitBreaker
from ai.client import call_llm_api

# Khởi tạo biến toàn cục (singleton cho toàn bộ worker)
global_circuit_breaker = CircuitBreaker()

class GenerationService:
    def __init__(self, circuit_breaker: CircuitBreaker = None):
        self.cb = circuit_breaker or global_circuit_breaker

    def generate_content(self, prompt: str) -> dict:
        # Nếu Circuit Breaker ngắt mạch, chặn luôn (Fallback Hard)
        if not self.cb.is_allow_request():
            return {
                "status": "error", 
                "code": "CAPACITY_EXHAUSTED", 
                "message": "AI models are currently overloaded. Please try again in a few minutes."
            }
        
        try:
            # Gọi LLM Client (đã bọc Retry loop)
            result = call_llm_api(prompt)
            self.cb.record_success()
            return {"status": "success", "data": result}
        except RetryError:
            # Bị RetryError tức là thử 5 lần đều fail
            self.cb.record_failure() # Cập nhật Circuit Breaker (Lưu ý: với retry 5 lần thì failure_count ở đây chỉ tăng 1, ta cấu hình threshold tuỳ ý)
            
            # (Hack) Vì 1 lần RetryError đã là đại diện cho 5 lần gọi rớt, ta gán thẳng threshold để ngắt mạch lập tức:
            self.cb.failure_count = self.cb.failure_threshold
            self.cb.record_failure() # Cập nhật lại timestamp
            
            return {
                "status": "error", 
                "code": "CAPACITY_EXHAUSTED", 
                "message": "AI models are currently overloaded. Please try again in a few minutes."
            }
