# Hugging Face Free API Integration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Thay thế hệ thống API trả phí hiện tại (FAL AI) bằng Hugging Face Inference API (Miễn phí) cho tính năng tạo ảnh từ văn bản.

**Architecture:** API Client gửi HTTP POST request tới Hugging Face. Hugging Face trả về trực tiếp dữ liệu nhị phân của bức ảnh (Raw Image Bytes). `main.py` nhận bytes và gọi `save_image_bytes` (đã được implement trước đó) để lưu ảnh. Bỏ qua logic Fallback cũ.

**Tech Stack:** `httpx`, `fastapi`.

## Global Constraints
- Yêu cầu cấu hình `HF_API_KEY` trong `.env`.
- Không sử dụng API key FAL_KEY nữa.
- Trả về 503 HTTP status code nếu model đang tải (Cold Start) với thông báo rõ ràng.
- Tuân thủ chuẩn TDD (Test-Driven Development).

---

### Task 1: Cập nhật Environment và Client API

**Files:**
- Modify: `backend/.env.example`
- Modify: `backend/ai/client.py`
- Modify: `backend/tests/test_ai_client.py`

**Interfaces:**
- Produces: `generate_image(prompt: str) -> bytes`

- [ ] **Step 1: Write the failing test**
```python
# backend/tests/test_ai_client.py
import pytest
from unittest.mock import patch, MagicMock
from ai.client import generate_image
import os

@pytest.mark.asyncio
@patch("ai.client.httpx.post")
async def test_generate_image_success(mock_post):
    os.environ["HF_API_KEY"] = "fake_key"
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.content = b"fake_image_bytes"
    mock_post.return_value = mock_response
    
    result = await generate_image("a cute cat")
    assert result == b"fake_image_bytes"
```

- [ ] **Step 2: Run test to verify it fails**
Run: `cd backend && ..\.venv\Scripts\pytest tests/test_ai_client.py -v`
Expected: FAIL

- [ ] **Step 3: Write minimal implementation**
```python
# backend/ai/client.py
import os
import logging
import httpx

logger = logging.getLogger(__name__)

async def generate_image(prompt: str) -> bytes:
    hf_api_key = os.getenv("HF_API_KEY", "")
    if not hf_api_key:
        raise ValueError("HF_API_KEY is not set")
        
    url = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
    headers = {"Authorization": f"Bearer {hf_api_key}"}
    payload = {"inputs": prompt}
    
    response = httpx.post(url, headers=headers, json=payload, timeout=60.0)
    
    if response.status_code == 503:
        raise RuntimeError("Model is currently loading. Please wait a few seconds.")
        
    response.raise_for_status()
    return response.content
```
*(Also remove `FAL_KEY` and add `HF_API_KEY=` to `backend/.env.example`)*

- [ ] **Step 4: Run test to verify it passes**
Run: `cd backend && ..\.venv\Scripts\pytest tests/test_ai_client.py -v`
Expected: PASS

- [ ] **Step 5: Commit**
```bash
git add backend/ai/client.py backend/tests/test_ai_client.py backend/.env.example
git commit -m "refactor(backend): integrate HF API returning raw bytes"
```

### Task 2: Cập nhật GenerationService và Main App

**Files:**
- Modify: `backend/services/generation_service.py`
- Modify: `backend/main.py`

**Interfaces:**
- Consumes: `generate_image(prompt: str) -> bytes` (từ Task 1)
- Consumes: `save_image_bytes(data: bytes) -> str` (từ `storage_service.py`)

- [ ] **Step 1: Write the failing test**
Sửa/cập nhật test trong `test_generation_service.py` và `test_main.py` để mock `generate_image` trả về `b"bytes"`.

- [ ] **Step 2: Run test to verify it fails**
Run: `cd backend && ..\.venv\Scripts\pytest -v`

- [ ] **Step 3: Write minimal implementation**
```python
# Trong backend/services/generation_service.py
from ai.client import generate_image

class GenerationService:
    async def generate_content(self, prompt: str) -> bytes:
        return await generate_image(prompt)
```

```python
# Trong backend/main.py
@app.post("/generate-image", response_model=schemas.ImageRecordResponse)
async def generate_image_endpoint(request: schemas.ImageRecordCreate, db: Session = Depends(get_db)):
    service = GenerationService()
    try:
        image_bytes = await service.generate_content(request.prompt)
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))
        
    try:
        from services.storage_service import save_image_bytes
        local_path = await save_image_bytes(image_bytes)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save image: {e}")
        
    db_image = models.ImageRecord(prompt=request.prompt, file_path=local_path)
    db.add(db_image)
    db.commit()
    db.refresh(db_image)
    
    return db_image
```

- [ ] **Step 4: Run test to verify it passes**
Run: `cd backend && ..\.venv\Scripts\pytest -v`
Expected: PASS

- [ ] **Step 5: Commit**
```bash
git add backend/services/generation_service.py backend/main.py
git commit -m "refactor(backend): update app to save image bytes directly and remove fallback"
```
