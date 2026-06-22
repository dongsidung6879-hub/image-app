# AI Resiliency Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Triển khai cơ chế chịu lỗi (Exponential Backoff & In-Memory Circuit Breaker) cho kết nối AI.

**Architecture:** Sử dụng thư viện `tenacity` để xử lý thử lại (retry) với độ trễ tăng dần (exponential backoff). Một class `CircuitBreaker` sẽ lưu trữ trạng thái ngắt mạch trên RAM cục bộ của mỗi worker để chuyển hướng sang Fallback sau 5 lần thử thất bại liên tiếp. Khối `generation_service` đóng vai trò điều phối giữa hai thành phần trên.

**Tech Stack:** Python 3, FastAPI, Pytest, Tenacity

## Global Constraints

- Không sử dụng các thư viện ngoài ngoài danh sách trong `requirements.txt` (đã có `tenacity`).
- Viết unit test đi kèm cho từng logic. (Test Driven Development)
- Code chuẩn PEP8.

---

### Task 1: Xây dựng In-Memory Circuit Breaker

**Files:**
- Create: `backend/utils/circuit_breaker.py`
- Create: `backend/tests/test_circuit_breaker.py`

**Interfaces:**
- Produces: `class CircuitBreaker(failure_threshold=5, recovery_timeout=300)`

- [ ] **Step 1: Write the failing test**

```python
# backend/tests/test_circuit_breaker.py
import time
from backend.utils.circuit_breaker import CircuitBreaker

def test_circuit_breaker_transitions():
    cb = CircuitBreaker(failure_threshold=3, recovery_timeout=1)
    
    # 1. Ban đầu là CLOSED
    assert cb.is_allow_request() is True
    
    # 2. Báo lỗi 3 lần -> chuyển sang OPEN
    cb.record_failure()
    cb.record_failure()
    cb.record_failure()
    assert cb.is_allow_request() is False
    
    # 3. Đợi hết timeout -> chuyển sang HALF_OPEN
    time.sleep(1.1)
    assert cb.is_allow_request() is True  # Mở hé cho request đầu tiên
    
    # 4. Request thử nghiệm thất bại -> Quay lại OPEN
    cb.record_failure()
    assert cb.is_allow_request() is False
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && python -m pytest tests/test_circuit_breaker.py -v`
Expected: FAIL with "ImportError: cannot import name 'CircuitBreaker'"

- [ ] **Step 3: Write minimal implementation**

```python
# backend/utils/circuit_breaker.py
import time

class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, recovery_timeout: float = 300.0):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = 0.0

    def is_allow_request(self) -> bool:
        if self.failure_count >= self.failure_threshold:
            # Nếu đang trong giai đoạn OPEN
            if time.time() - self.last_failure_time < self.recovery_timeout:
                return False
        return True

    def record_failure(self) -> None:
        self.failure_count += 1
        self.last_failure_time = time.time()

    def record_success(self) -> None:
        self.failure_count = 0
        self.last_failure_time = 0.0
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd backend && python -m pytest tests/test_circuit_breaker.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add backend/utils/circuit_breaker.py backend/tests/test_circuit_breaker.py
git commit -m "feat(backend): implement in-memory circuit breaker state machine"
```

---

### Task 2: Cấu hình Exponential Backoff Caller với Tenacity

**Files:**
- Create: `backend/ai/client.py`
- Create: `backend/tests/test_ai_client.py`

**Interfaces:**
- Produces: `def call_llm_api(prompt: str) -> str` (Đã được wrap bởi `@retry` của tenacity)

- [ ] **Step 1: Write the failing test**

```python
# backend/tests/test_ai_client.py
import pytest
from tenacity import RetryError
from unittest.mock import patch
from backend.ai.client import call_llm_api

@patch("backend.ai.client.fake_network_request")
def test_call_llm_api_retries_and_fails(mock_request):
    # Cấu hình mock để luôn raise Exception
    mock_request.side_effect = Exception("API 503")
    
    with pytest.raises(RetryError):
        call_llm_api("hello")
        
    # Kiểm tra xem nó đã cố gắng gọi ít nhất 5 lần
    assert mock_request.call_count == 5
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && python -m pytest tests/test_ai_client.py -v`
Expected: FAIL with "ImportError"

- [ ] **Step 3: Write minimal implementation**

```python
# backend/ai/client.py
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd backend && python -m pytest tests/test_ai_client.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add backend/ai/client.py backend/tests/test_ai_client.py
git commit -m "feat(backend): setup tenacity retry loop for AI client"
```

---

### Task 3: Orchestrator Service (Tích hợp Fallback)

**Files:**
- Create: `backend/services/generation_service.py`
- Create: `backend/tests/test_generation_service.py`

**Interfaces:**
- Consumes: `CircuitBreaker` (Task 1), `call_llm_api` (Task 2)
- Produces: `def generate_content(prompt: str) -> dict`

- [ ] **Step 1: Write the failing test**

```python
# backend/tests/test_generation_service.py
from unittest.mock import patch
from backend.services.generation_service import GenerationService
from backend.utils.circuit_breaker import CircuitBreaker

@patch("backend.services.generation_service.call_llm_api")
def test_generation_fallback_when_circuit_open(mock_call):
    # Khởi tạo service với cb cấu hình sẵn
    cb = CircuitBreaker()
    service = GenerationService(circuit_breaker=cb)
    
    # Ép CB sang OPEN
    for _ in range(5):
        cb.record_failure()
        
    result = service.generate_content("test")
    
    # Kiểm tra kịch bản Fallback (API không được gọi)
    assert result["status"] == "error"
    assert result["code"] == "CAPACITY_EXHAUSTED"
    assert mock_call.call_count == 0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && python -m pytest tests/test_generation_service.py -v`
Expected: FAIL

- [ ] **Step 3: Write minimal implementation**

```python
# backend/services/generation_service.py
from tenacity import RetryError
from backend.utils.circuit_breaker import CircuitBreaker
from backend.ai.client import call_llm_api

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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd backend && python -m pytest tests/test_generation_service.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add backend/services/generation_service.py backend/tests/test_generation_service.py
git commit -m "feat(backend): implement generation orchestrator with fallback"
```
