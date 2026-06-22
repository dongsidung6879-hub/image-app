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
