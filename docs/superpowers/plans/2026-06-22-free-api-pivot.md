# Cập nhật API Miễn phí (Free API Pivot) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Chuyển đổi hệ thống từ việc gọi API trả phí (FAL AI/OpenAI) sang sử dụng API hoàn toàn miễn phí của Pollinations.ai để tạo ảnh từ Prompt.

**Architecture:** 
Thay vì phải gọi HTTP Request để chờ FAL AI sinh ảnh và trả về JSON, ta sẽ chuyển URL sinh ảnh thành `https://image.pollinations.ai/prompt/{prompt}`. Trả URL này về cho hệ thống Storage tự động tải ảnh như cũ. Điều này giúp loại bỏ phụ thuộc vào API keys và hoàn toàn miễn phí.

**Tech Stack:** `urllib.parse`, `fastapi`.

## Global Constraints

- Không sử dụng API Key.
- Giữ nguyên luồng tải ảnh (Storage Service) để frontend vẫn hiển thị ảnh mượt mà.
- Tuân thủ chuẩn TDD (Test-Driven Development).

---

### Task 1: Cập nhật AI Client sang Pollinations
Thay đổi logic trong `backend/ai/client.py` để không còn dùng FAL_KEY, thay vào đó tạo Pollinations URL.

**Files:**
- Modify: `backend/ai/client.py`
- Modify: `backend/tests/test_ai_client.py`

**Interfaces:**
- Produces: `generate_image(prompt: str)` trả về `{"status": "success", "data": {"images": [{"url": "https://image.pollinations.ai/..."}]}}`

- [ ] **Step 1: Viết test (Failing test)**
```python
# Trong backend/tests/test_ai_client.py
import pytest
from ai.client import generate_image

@pytest.mark.asyncio
async def test_generate_image_pollinations():
    result = await generate_image("a cute cat")
    assert result["status"] == "success"
    assert "image.pollinations.ai" in result["data"]["images"][0]["url"]
    assert "a%20cute%20cat" in result["data"]["images"][0]["url"]
```

- [ ] **Step 2: Chạy test**
Run: `cd backend && python -m pytest tests/test_ai_client.py -v`
Expected: FAIL

- [ ] **Step 3: Implement Code**
```python
# Trong backend/ai/client.py
import urllib.parse

async def generate_image(prompt: str) -> dict:
    encoded_prompt = urllib.parse.quote(prompt)
    url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&nologo=true"
    
    return {
        "status": "success",
        "data": {
            "images": [{"url": url}]
        }
    }
```

- [ ] **Step 4: Chạy lại test**
Run: `cd backend && python -m pytest tests/test_ai_client.py -v`
Expected: PASS

- [ ] **Step 5: Commit**
```bash
git add backend/ai/client.py backend/tests/test_ai_client.py
git commit -m "refactor(backend): pivot to free pollinations API"
```

---

### Task 2: Dọn dẹp Fallback và Resiliency cũ (Tùy chọn)
Vì Pollinations là URL Generator (không cần kết nối chờ JSON), ta không còn cần mạch chống lỗi CircuitBreaker phức tạp hay OpenAI Fallback nữa.

**Files:**
- Modify: `backend/services/generation_service.py`
- Delete: `backend/ai/fallback_client.py`

- [ ] **Step 1: Viết Test (Sửa test hiện tại)**
- Xoá/sửa các test liên quan tới fallback trong `test_generation_service.py`.

- [ ] **Step 2: Implement Code**
```python
# Trong backend/services/generation_service.py
from ai.client import generate_image
import asyncio

class GenerationService:
    def generate_content(self, prompt: str) -> dict:
        return asyncio.run(generate_image(prompt))
```

- [ ] **Step 3: Chạy test tổng thể**
Run: `cd backend && python -m pytest -v`

- [ ] **Step 4: Commit**
```bash
git add backend/services/generation_service.py
git commit -m "refactor(backend): clean up unused fallback logic"
```
