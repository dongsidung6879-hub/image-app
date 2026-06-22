# AI Resiliency Design Spec: Exponential Backoff & Circuit Breaker

## 1. Overview
Hệ thống kết nối AI của dự án cần cơ chế chịu lỗi (resiliency) triệt để nhằm đối phó với tình trạng `HTTP 503 Service Unavailable / MODEL_CAPACITY_EXHAUSTED` từ phía API server của LLM. Thiết kế này áp dụng pattern "Exponential Backoff với Jitter" kết hợp "In-Memory Circuit Breaker" và cơ chế Fallback an toàn.

## 2. Architecture

### 2.1. Exponential Backoff Caller (`backend/ai/client.py`)
- Sử dụng thư viện `tenacity` để bọc các hàm gọi LLM.
- **Chiến lược Retry:**
  - `stop_after_attempt(5)`: Thử tối đa 5 lần.
  - `wait_exponential_jitter(initial=10, max=120, exp_base=1.6)`: Lần 1 đợi khoảng 10s, lần 2 tăng lên khoảng 16s, sau đó tăng dần lên tối đa 120s giữa các lần gọi nghiệm thu. Sử dụng jitter để tránh thundering herd problem.

### 2.2. In-Memory Circuit Breaker (`backend/utils/circuit_breaker.py`)
- Một class `CircuitBreaker` nhẹ quản lý trạng thái kết nối tới AI API.
- Trạng thái được lưu trên RAM (độc lập cho mỗi Uvicorn worker):
  - **CLOSED:** Trạng thái bình thường. Mọi request đi qua AI Client. Nếu có lỗi, tăng biến đếm (failure count). Nếu gọi thành công, reset biến đếm.
  - **OPEN:** Trạng thái ngắt mạch. Được kích hoạt khi số lần gọi thất bại liên tiếp đạt ngưỡng (Ví dụ: 5 lần). Trong khoảng thời gian `recovery_timeout` (ví dụ: 300 giây/5 phút), MỌI request đều lập tức bị từ chối/bắn sang Fallback mà không cố gọi AI Client.
  - **HALF-OPEN:** Sau khi hết `recovery_timeout`, cho phép 1 request đi qua để thử nghiệm. Nếu thành công -> chuyển về CLOSED. Nếu thất bại -> quay lại OPEN và reset thời gian đợi.

### 2.3. Fallback Orchestrator (`backend/services/generation_service.py`)
- Làm điểm trung chuyển giữa API Endpoint và Logic gọi AI.
- Kiểm tra trạng thái CircuitBreaker trước khi gọi AI Client.
- Bắt lỗi `RetryError` từ `tenacity` hoặc lỗi do CircuitBreaker báo OPEN để xử lý logic dự phòng:
  - Tùy chọn 1 (Soft): Gọi sang LLM phụ (Ví dụ OpenAI/Claude) nếu có config trong `.env`.
  - Tùy chọn 2 (Hard): Trả về JSON lỗi graceful 503 cho frontend: `{"error": "AI models are currently overloaded. Please try again in a few minutes.", "code": "CAPACITY_EXHAUSTED"}`.

## 3. Scope & Constraints
- Giai đoạn hiện tại không sử dụng Redis để phân tán CircuitBreaker. Trạng thái ngắt mạch được duy trì ở local memory của từng worker để tối giản kiến trúc.
- Cần bổ sung các bài unit test cơ bản để mô phỏng trạng thái state machine của CircuitBreaker.
