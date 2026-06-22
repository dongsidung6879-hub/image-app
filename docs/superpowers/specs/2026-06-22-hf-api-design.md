# Hugging Face Free API Integration Design

## Mục tiêu (Goal)
Thay thế hệ thống API trả phí hiện tại (FAL AI / OpenAI) bằng Hugging Face Inference API (Miễn phí) cho tính năng tạo ảnh từ văn bản.

## Kiến trúc (Architecture)
1. **Model:** Sử dụng `stabilityai/stable-diffusion-xl-base-1.0` (Mô hình SDXL mã nguồn mở chất lượng rất cao) thông qua Inference API của Hugging Face.
2. **Xác thực (Auth):** Người dùng cần khai báo biến `HF_API_KEY` trong file `.env`.
3. **Luồng dữ liệu (Data Flow):**
   - API Client (`backend/ai/client.py`) gửi HTTP POST request tới Hugging Face kèm header `Authorization: Bearer {HF_API_KEY}` và body `{"inputs": prompt}`.
   - Hugging Face trả về trực tiếp Dữ liệu nhị phân của bức ảnh (Raw Image Bytes) thay vì URL.
   - Hàm `generate_image` sẽ trả về `bytes`.
   - `main.py` nhận bytes và đẩy sang `storage_service.py` để lưu thành file `.png`.

## Components Impacted
1. **`backend/.env.example`**: Xóa `FAL_KEY`, thêm `HF_API_KEY`.
2. **`backend/ai/client.py`**: Viết lại hàm `generate_image` để gọi HF API và nhận `bytes`.
3. **`backend/services/storage_service.py`**: Thêm hàm `save_image_bytes(data: bytes) -> str` để lưu ảnh nhị phân (bên cạnh hàm tải ảnh từ URL cũ).
4. **`backend/main.py`**: Đổi logic nhận JSON cũ thành nhận `bytes` và gọi `save_image_bytes`.
5. **`backend/services/generation_service.py`**: Xóa luồng Fallback cũ vì không còn cần thiết.

## Xử lý Lỗi (Error Handling)
- Nếu `HF_API_KEY` bị thiếu, báo lỗi 500.
- Nếu Hugging Face đang tải model (Cold Start), nó sẽ trả về mã lỗi 503 với thông báo "Model is currently loading". Hàm Client có thể bắt lỗi này và báo người dùng đợi khoảng 30s-1 phút.
