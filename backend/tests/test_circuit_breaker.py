import time
from utils.circuit_breaker import CircuitBreaker

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
